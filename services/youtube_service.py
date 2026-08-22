"""
services/youtube_service.py
Extract transcript and metadata from YouTube videos.
Uses Invidious public API instances as a cloud-friendly alternative to direct YouTube requests.
"""

import re
import os
import requests
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


# Public Invidious instances — used as cloud-friendly transcript fallback
INVIDIOUS_INSTANCES = [
    "https://invidious.nerdvpn.de",
    "https://inv.nadeko.net",
    "https://invidious.privacydev.net",
    "https://yt.artemislena.eu",
    "https://invidious.lunar.icu",
    "https://iv.melmac.space",
    "https://invidious.perennialte.ch",
]


def extract_video_id(url: str) -> Optional[str]:
    """Extract the 11-character video ID from any YouTube URL format."""
    patterns = [
        r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_video_title(video_id: str) -> str:
    """Fetch the video title via oEmbed (no auth required)."""
    try:
        resp = requests.get(
            f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json",
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("title", "Unknown Title")
    except Exception:
        pass
    return "Unknown Title"


def _parse_vtt(vtt_content: str) -> str:
    """Parse a WebVTT caption file into clean plain text."""
    lines = vtt_content.split("\n")
    text_lines = []

    for line in lines:
        line = line.strip()
        # Skip header, timestamps, cue identifiers, and empty lines
        if not line or "WEBVTT" in line or "-->" in line or line.isdigit():
            continue
        # Strip VTT/HTML tags like <00:00:01.000>, <c>, </c>, <i>, etc.
        clean = re.sub(r"<[^>]+>", "", line).strip()
        if clean:
            text_lines.append(clean)

    # Remove consecutive duplicate lines (VTT overlapping captions)
    unique_lines: list[str] = []
    prev = None
    for line in text_lines:
        if line != prev:
            unique_lines.append(line)
            prev = line

    return " ".join(unique_lines)


def _fetch_via_invidious(video_id: str) -> str:
    """
    Fetch transcript via public Invidious API instances.
    These instances have residential/non-cloud IPs so they bypass YouTube's cloud IP blocks.
    Returns transcript text, or empty string if all instances fail.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    for instance in INVIDIOUS_INSTANCES:
        try:
            # Step 1: Get list of available caption tracks
            resp = requests.get(
                f"{instance}/api/v1/captions/{video_id}",
                timeout=12,
                headers=headers,
            )
            if resp.status_code != 200:
                continue

            tracks = resp.json().get("captions", [])
            if not tracks:
                continue

            # Prefer English captions, fall back to first available track
            selected = next(
                (t for t in tracks if t.get("language_code", "").startswith("en")),
                tracks[0],
            )
            caption_url = selected.get("url", "")
            if not caption_url:
                continue

            # Step 2: Download the caption file (VTT format)
            full_url = f"{instance}{caption_url}"
            cap_resp = requests.get(full_url, timeout=15, headers=headers)
            if cap_resp.status_code != 200:
                continue

            # Step 3: Parse and return plain text
            transcript_text = _parse_vtt(cap_resp.text)
            if transcript_text.strip():
                return transcript_text

        except Exception:
            continue  # Try the next instance

    return ""


def get_transcript(url: str) -> dict:
    """
    Returns:
        {
            "video_id": str,
            "title": str,
            "transcript": str,
            "word_count": int,
            "char_count": int,
        }
    Raises ValueError with a user-friendly message on failure.
    Strategy:
        1. Try Invidious public API instances (cloud-friendly, no IP blocks).
        2. Fall back to youtube-transcript-api with proxy if configured.
    """
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError(
            "❌ Could not extract a valid video ID. "
            "Please paste a valid YouTube URL (e.g. https://youtu.be/dQw4w9WgXcQ)."
        )

    # --- Strategy 1: Try Invidious instances ---
    transcript_text = _fetch_via_invidious(video_id)

    # --- Strategy 2: Fall back to youtube-transcript-api with optional proxy ---
    if not transcript_text:
        try:
            import streamlit as st
            proxy_username = st.secrets.get("WEBSHARE_USERNAME", "").strip()
            proxy_password = st.secrets.get("WEBSHARE_PASSWORD", "").strip()
            proxy_host     = st.secrets.get("WEBSHARE_PROXY_HOST", "p.webshare.io").strip()
            proxy_port     = st.secrets.get("WEBSHARE_PROXY_PORT", "80").strip()
        except Exception:
            proxy_username = os.getenv("WEBSHARE_USERNAME", "").strip()
            proxy_password = os.getenv("WEBSHARE_PASSWORD", "").strip()
            proxy_host     = os.getenv("WEBSHARE_PROXY_HOST", "p.webshare.io").strip()
            proxy_port     = os.getenv("WEBSHARE_PROXY_PORT", "80").strip()

        proxy_configured = bool(proxy_username and proxy_password)

        try:
            if proxy_configured:
                proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"
                try:
                    from youtube_transcript_api.proxies import GenericProxyConfig
                    api = YouTubeTranscriptApi(
                        proxy_config=GenericProxyConfig(
                            http_url=proxy_url,
                            https_url=proxy_url,
                        )
                    )
                except ImportError:
                    api = YouTubeTranscriptApi(proxies={"http": proxy_url, "https": proxy_url})
            else:
                api = YouTubeTranscriptApi()

            transcript_list = api.fetch(video_id)
            transcript_text = " ".join(seg.text for seg in transcript_list)

        except TranscriptsDisabled:
            raise ValueError("❌ Transcripts are disabled for this video.")
        except NoTranscriptFound:
            raise ValueError(
                "❌ No transcript found for this video. "
                "Try a video that has auto-generated or manual captions."
            )
        except Exception as exc:
            msg = str(exc).lower()
            if "407" in msg or "proxy authentication" in msg:
                raise ValueError(
                    "❌ Proxy authentication failed. "
                    "Please double-check WEBSHARE_USERNAME and WEBSHARE_PASSWORD in your Streamlit secrets."
                )
            # Last resort — both strategies failed
            raise ValueError(
                "❌ Could not retrieve the transcript. "
                "YouTube may have disabled captions for this video, or all transcript sources are unavailable. "
                "Please try a different video."
            )

    if not transcript_text.strip():
        raise ValueError(
            "❌ No transcript content could be extracted for this video. "
            "Try a video that has captions enabled."
        )

    title = get_video_title(video_id)

    return {
        "video_id": video_id,
        "title": title,
        "transcript": transcript_text,
        "word_count": len(transcript_text.split()),
        "char_count": len(transcript_text),
    }

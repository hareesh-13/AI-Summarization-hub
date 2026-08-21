"""
services/youtube_service.py
Extract transcript and metadata from YouTube videos.
"""

import re
import os
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


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
    import requests
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
    """
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError(
            "❌ Could not extract a valid video ID. "
            "Please paste a valid YouTube URL (e.g. https://youtu.be/dQw4w9WgXcQ)."
        )

    # Read proxy credentials — try st.secrets first (Streamlit Cloud), then os.getenv (local)
    try:
        import streamlit as st
        proxy_username = st.secrets.get("WEBSHARE_USERNAME", "").strip()
        proxy_password = st.secrets.get("WEBSHARE_PASSWORD", "").strip()
    except Exception:
        proxy_username = os.getenv("WEBSHARE_USERNAME", "").strip()
        proxy_password = os.getenv("WEBSHARE_PASSWORD", "").strip()

    proxy_configured = bool(proxy_username and proxy_password)

    try:
        if proxy_configured:
            proxy_url = f"http://{proxy_username}:{proxy_password}@p.webshare.io:80"
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
        if any(k in msg for k in ["blocked", "ip", "cloud", "requestblocked", "ipblocked"]):
            if proxy_configured:
                raise ValueError(
                    "❌ The Webshare proxy credentials may be incorrect or the proxy is not working. "
                    "Please double-check WEBSHARE_USERNAME and WEBSHARE_PASSWORD in your Streamlit secrets."
                )
            else:
                raise ValueError(
                    "❌ YouTube is blocking requests from this server. "
                    "Add WEBSHARE_USERNAME and WEBSHARE_PASSWORD to your Streamlit Cloud secrets to fix this."
                )
        raise ValueError(f"❌ Failed to fetch transcript: {exc}")

    title = get_video_title(video_id)

    return {
        "video_id": video_id,
        "title": title,
        "transcript": transcript_text,
        "word_count": len(transcript_text.split()),
        "char_count": len(transcript_text),
    }

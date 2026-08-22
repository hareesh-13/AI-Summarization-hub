import os
import re
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url: str) -> str:
    """
    Parses and extracts the 11-character video ID from any YouTube URL layout.
    """
    if not url:
        return None
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?|shorts)/|.*[?&]v=)|youtu\.be/)([^"&?/\s]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_youtube_transcript(video_url: str) -> str:
    """
    Bypasses cloud proxy parameters, pulls raw transcript chunks,
    and returns a clean unified string block.
    """
    # Double-check environment variables are cleared at runtime
    for var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
        if var in os.environ:
            del os.environ[var]

    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid URL format. Could not parse the YouTube Video ID.")

    try:
        # Force empty strings into proxies dict to strip standard runtime defaults
        raw_data = YouTubeTranscriptApi.get_transcript(
            video_id, 
            proxies={"http": "", "https": ""}
        )
        
        # Merge dictionary data entries into one coherent block of text
        full_text = " ".join([entry["text"] for entry in raw_data])
        return re.sub(r'\s+', ' ', full_text).strip()

    except Exception as e:
        error_str = str(e)
        if "407" in error_str:
            raise RuntimeError("Streamlit Cloud proxy infrastructure is refusing your connection token.")
        elif "403" in error_str or "Too Many Requests" in error_str:
            raise RuntimeError("YouTube has throttled/blocked this cloud host IP range. Try again shortly.")
        else:
            raise RuntimeError(f"Transcript compilation error: {error_str}")

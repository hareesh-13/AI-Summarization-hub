"""
utils/analytics.py
Calculate and return analytics metrics for text.
"""

import math


def compute_analytics(original_text: str, summary: str) -> dict:
    """Return analytics metrics comparing original text to summary."""
    orig_words = len(original_text.split())
    orig_chars = len(original_text)
    summ_words = len(summary.split())
    summ_chars = len(summary)

    # Reading time at ~238 wpm average
    orig_reading_time = max(1, math.ceil(orig_words / 238))
    summ_reading_time = max(1, math.ceil(summ_words / 238))

    # Compression ratio
    if orig_words > 0:
        compression = round((1 - summ_words / orig_words) * 100, 1)
    else:
        compression = 0.0

    return {
        "original_word_count": orig_words,
        "original_char_count": orig_chars,
        "original_reading_time_min": orig_reading_time,
        "summary_word_count": summ_words,
        "summary_char_count": summ_chars,
        "summary_reading_time_min": summ_reading_time,
        "compression_ratio": compression,
    }

"""
Freestyle Wrangler Component

This module implements the normalize_subtitles function for the Freestyle Wrangler
component of the subtitle alignment competition.
"""

from typing import dict, Any, list


def normalize_subtitles(caption: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize a single subtitle caption.

    Args:
        caption: A dictionary containing raw subtitle data with potentially
                inconsistent formats, encoding issues, etc.

    Returns:
        A normalized subtitle dictionary with the following structure:
        {
            "id": int,                    # Unique identifier for the subtitle entry
            "start": float,               # Start time in seconds
            "end": float,                 # End time in seconds
            "text": str,                  # Cleaned text content
            "phonemes": list[str],        # list of phoneme strings
            "speaker": str (optional)     # Speaker identifier if available
        }
    """
    # Your implementation here
    pass

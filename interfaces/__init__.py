"""
Interface definitions for the subtitle alignment competition.

This package contains interface definitions for both components of the competition:
1. Freestyle Wrangler - Data normalization and preprocessing
2. The Sync Showdown - Subtitle alignment algorithm implementation
"""

from .wrangler_interface import WranglerInterface, load_subtitles, save_subtitles
from .alignment_interface import (
    AlignmentInterface, 
    AlignmentConfig, 
    AlignmentResult, 
    apply_offset
)

__all__ = [
    'WranglerInterface',
    'AlignmentInterface',
    'AlignmentConfig',
    'AlignmentResult',
    'load_subtitles',
    'save_subtitles',
    'apply_offset'
]

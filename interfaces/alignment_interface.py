
"""
The Sync Showdown Interface Definition

This module defines the interface for "The Sync Showdown" component of the
subtitle alignment competition. The Sync Showdown is responsible for
implementing the Phonetic Walk algorithm to align two sets of subtitles.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
import json
from pathlib import Path


class AlignmentResult:
    """
    Class representing the result of an alignment operation.
    """
    
    def __init__(
        self,
        status: str,
        offset_seconds: Optional[float] = None,
        confidence: Optional[float] = None,
        alignment_path: Optional[List[Tuple[int, int]]] = None,
        reason: Optional[str] = None
    ):
        """
        Initialize an AlignmentResult.
        
        Args:
            status: 'success' or 'failure'
            offset_seconds: The calculated time offset in seconds (if successful)
            confidence: A confidence score between 0.0 and 1.0 (if successful)
            alignment_path: The alignment path as a list of (i, j) index pairs (if successful)
            reason: The reason for failure (if status is 'failure')
        """
        self.status = status
        self.offset_seconds = offset_seconds
        self.confidence = confidence
        self.alignment_path = alignment_path
        self.reason = reason
    
    def is_success(self) -> bool:
        """
        Check if the alignment was successful.
        
        Returns:
            True if the alignment was successful, False otherwise
        """
        return self.status == 'success'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the result to a dictionary.
        
        Returns:
            A dictionary representation of the alignment result
        """
        result = {'status': self.status}
        
        if self.is_success():
            result.update({
                'offset_seconds': self.offset_seconds,
                'confidence': self.confidence
            })
            if self.alignment_path:
                result['alignment_path'] = self.alignment_path
        else:
            result['reason'] = self.reason
            result['offset_seconds'] = None
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlignmentResult':
        """
        Create an AlignmentResult from a dictionary.
        
        Args:
            data: Dictionary containing alignment result data
            
        Returns:
            An AlignmentResult instance
        """
        if data['status'] == 'success':
            return cls(
                status='success',
                offset_seconds=data.get('offset_seconds'),
                confidence=data.get('confidence'),
                alignment_path=data.get('alignment_path')
            )
        else:
            return cls(
                status='failure',
                reason=data.get('reason')
            )
    
    @classmethod
    def success(
        cls,
        offset_seconds: float,
        confidence: float,
        alignment_path: Optional[List[Tuple[int, int]]] = None
    ) -> 'AlignmentResult':
        """
        Create a successful alignment result.
        
        Args:
            offset_seconds: The calculated time offset in seconds
            confidence: A confidence score between 0.0 and 1.0
            alignment_path: The alignment path as a list of (i, j) index pairs
            
        Returns:
            A successful AlignmentResult
        """
        return cls(
            status='success',
            offset_seconds=offset_seconds,
            confidence=confidence,
            alignment_path=alignment_path
        )
    
    @classmethod
    def failure(cls, reason: str) -> 'AlignmentResult':
        """
        Create a failed alignment result.
        
        Args:
            reason: The reason for failure
            
        Returns:
            A failed AlignmentResult
        """
        return cls(
            status='failure',
            reason=reason
        )


class AlignmentConfig:
    """
    Configuration parameters for the alignment algorithm.
    """
    
    def __init__(
        self,
        phonetic_similarity_threshold: float = 0.7,
        smear_similarity_threshold: float = 0.5,
        initial_search_window_seconds: float = 120.0,
        local_search_neighborhood: Dict[str, List[int]] = None,
        min_path_length: int = 5,
        max_consecutive_gaps: int = 2,
        gap_penalty: float = 0.1,
        speaker_mismatch_penalty: float = 0.5,
        offset_consistency_threshold_sd: float = 0.5
    ):
        """
        Initialize alignment configuration parameters.
        
        Args:
            phonetic_similarity_threshold: Minimum similarity score for direct matches
            smear_similarity_threshold: Minimum similarity score for smear matches
            initial_search_window_seconds: Max time difference for initial search
            local_search_neighborhood: Relative indices to check for next match
            min_path_length: Minimum number of match points required
            max_consecutive_gaps: Maximum number of consecutive skipped chunks
            gap_penalty: Penalty applied to path score for each skipped chunk
            speaker_mismatch_penalty: Penalty for speaker mismatches
            offset_consistency_threshold_sd: Max standard deviation for offsets
        """
        self.phonetic_similarity_threshold = phonetic_similarity_threshold
        self.smear_similarity_threshold = smear_similarity_threshold
        self.initial_search_window_seconds = initial_search_window_seconds
        self.local_search_neighborhood = local_search_neighborhood or {'i_steps': [1, 2], 'j_steps': [1, 2]}
        self.min_path_length = min_path_length
        self.max_consecutive_gaps = max_consecutive_gaps
        self.gap_penalty = gap_penalty
        self.speaker_mismatch_penalty = speaker_mismatch_penalty
        self.offset_consistency_threshold_sd = offset_consistency_threshold_sd
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.
        
        Returns:
            A dictionary representation of the configuration
        """
        return {
            'phonetic_similarity_threshold': self.phonetic_similarity_threshold,
            'smear_similarity_threshold': self.smear_similarity_threshold,
            'initial_search_window_seconds': self.initial_search_window_seconds,
            'local_search_neighborhood': self.local_search_neighborhood,
            'min_path_length': self.min_path_length,
            'max_consecutive_gaps': self.max_consecutive_gaps,
            'gap_penalty': self.gap_penalty,
            'speaker_mismatch_penalty': self.speaker_mismatch_penalty,
            'offset_consistency_threshold_sd': self.offset_consistency_threshold_sd
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlignmentConfig':
        """
        Create an AlignmentConfig from a dictionary.
        
        Args:
            data: Dictionary containing configuration parameters
            
        Returns:
            An AlignmentConfig instance
        """
        return cls(**data)


def align_subtitles(
    subtitles1: List[Dict[str, Any]],
    subtitles2: List[Dict[str, Any]],
    config: Optional[AlignmentConfig] = None
) -> AlignmentResult:
    """
    Align two sets of subtitles using the Phonetic Walk algorithm.
    
    This is the main entry point for The Sync Showdown component.
    The function should implement the complete Phonetic Walk algorithm including:
    - Finding an initial anchor match
    - Following the alignment path
    - Handling signal smearing
    - Calculating and validating the offset
    - Generating confidence scores
    
    Args:
        subtitles1: First set of normalized subtitle dictionaries
        subtitles2: Second set of normalized subtitle dictionaries
        config: Optional configuration parameters for the alignment algorithm
        
    Returns:
        An AlignmentResult object containing the alignment results
        
    Raises:
        ValueError: If the input data is invalid or insufficient
    """
    raise NotImplementedError("Implement align_subtitles to align two sets of subtitles")


def apply_offset(subtitles: List[Dict[str, Any]], offset_seconds: float) -> List[Dict[str, Any]]:
    """
    Apply a time offset to a set of subtitles.
    
    Args:
        subtitles: List of subtitle dictionaries
        offset_seconds: Time offset to apply in seconds (positive or negative)
        
    Returns:
        List of subtitle dictionaries with adjusted timestamps
    """
    result = []
    for subtitle in subtitles:
        adjusted = subtitle.copy()
        adjusted['start'] = subtitle['start'] + offset_seconds
        adjusted['end'] = subtitle['end'] + offset_seconds
        result.append(adjusted)
    return result


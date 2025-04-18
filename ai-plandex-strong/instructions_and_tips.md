
# Subtitle Alignment Competition: Instructions and Tips

## Overview

This document provides detailed instructions and implementation tips for the subtitle alignment competition. The competition consists of two main components:

1. **Freestyle Wrangler** - Data normalization and preprocessing
2. **The Sync Showdown** - Subtitle alignment algorithm implementation

## Core Instructions

### Freestyle Wrangler

The Freestyle Wrangler component is responsible for normalizing and preprocessing raw subtitle data. Your implementation should:

1. **Parse Raw Data**
   - Handle various input formats (JSON, text files, etc.)
   - Extract subtitle entries with their timestamps, text, and metadata

2. **Normalize Timestamps**
   - Convert all timestamps to a consistent format (floating-point seconds)
   - Handle various timestamp formats (HH:MM:SS.mmm, MM:SS:FF, etc.)
   - Resolve missing or malformed timestamps

3. **Clean Text Content**
   - Handle encoding issues (UTF-8, special characters, etc.)
   - Normalize punctuation and formatting
   - Remove irrelevant content (e.g., release group messages)

4. **Handle Missing Data**
   - Implement fallbacks for missing fields
   - Estimate missing timestamps based on context
   - Generate phonetic representations for text

5. **Resolve Overlaps**
   - Detect and resolve overlapping timestamps
   - Ensure chronological ordering of subtitles

### The Sync Showdown

The Sync Showdown component implements the Phonetic Walk algorithm for subtitle alignment. Your implementation should:

1. **Calculate Phonetic Similarity**
   - Implement a robust phonetic similarity function
   - Handle speaker constraints appropriately
   - Normalize similarity scores

2. **Find Initial Anchor Match**
   - Identify a high-confidence initial match
   - Establish a starting point for alignment

3. **Follow Alignment Path**
   - Implement the path-following algorithm
   - Handle gaps and smearing appropriately
   - Maintain path consistency

4. **Calculate and Validate Offset**
   - Compute the median offset from the alignment path
   - Validate offset consistency
   - Generate confidence scores

## Interface Requirements

Your implementation must conform to the following simplified interfaces:

```python
def normalize_subtitles(caption):
    """
    Normalize a single subtitle caption.
    
    Args:
        caption: A dictionary containing raw subtitle data
        
    Returns:
        A normalized subtitle dictionary
    """
    pass

def align_subtitles(subtitles1, subtitles2, config=None):
    """
    Align two sets of normalized subtitles.
    
    Args:
        subtitles1: First set of normalized subtitles
        subtitles2: Second set of normalized subtitle
        config: Optional configuration parameters
        
    Returns:
        An alignment result with offset and confidence
    """
    pass
```

## Implementation Freedom

**Important:** You have complete freedom in how you implement the solutions for both components. The only requirements are:

1. Your implementation must use the function signatures specified above
2. Your implementation must return data in the expected format
3. Your solution must handle the challenges described in the competition documentation

Beyond these minimal requirements, you are free to:

- Choose any algorithms, data structures, or approaches you prefer
- Create any helper functions or utility modules as needed
- Implement the solution in your own style and organization
- Use any libraries or tools that are appropriate for the task

There is no "correct" implementation approach. The competition is designed to evaluate your ability to solve the problem effectively, not to follow a specific implementation pattern.

## Testing Your Implementation

To test your implementation, we provide several challenge sets with different characteristics:

1. **Basic Alignment** - Simple subtitles with consistent offset
2. **Encoding Challenges** - Subtitles with various encoding issues and special characters
3. **Varying Offset** - Subtitles where the offset changes gradually throughout the file
4. **Missing Data** - Subtitles with missing fields and incomplete information

Your solution will be evaluated on how well it handles each of these challenges, both individually and in combination.

## Reference Implementation Suggestions

The following sections contain optional implementation suggestions and tips. These are provided as a reference and are not required to follow. You are encouraged to develop your own approach based on your understanding of the problem.

### Reference: Handling Missing Data and Edge Cases

When implementing the Phonetic Walking algorithm, you'll encounter various real-world challenges with subtitle data. Here's how you might handle common edge cases:

#### Missing Phonemes

* If a chunk is missing phonemes (e.g., due to failed dictionary lookup), you have several options:
  * Skip the chunk entirely (treat it as a gap)
  * Use a fallback phonetic representation based on simple letter-to-sound rules
  * For very short words (1-3 characters), consider using the raw text for comparison
* Always log chunks with missing phonemes for later analysis

#### Missing Timestamps

* If a chunk is missing start or end timestamps:
  * For missing end times, estimate using start time + average duration based on text length
  * For missing start times, estimate using previous chunk's end time + small gap (e.g., 0.1s)
  * If timestamps are completely absent, the chunk should be excluded from alignment

#### Empty or Invalid Text

* Chunks with empty text but valid timestamps should be preserved as potential gaps
* Chunks with only non-speech markers (e.g., "[Music]", "[Applause]") should be excluded from phonetic matching but preserved in the final alignment

#### Missing Speaker Information

* When speaker information is missing for one or both sets:
  * Set `speaker_mismatch_penalty` to 0 for those comparisons
  * Consider using a reduced penalty when only one set has speaker information

#### Handling Boundary Cases

* **Start and End of Files:**
  * The algorithm may struggle to find matches at the very beginning or end of files
  * Consider relaxing thresholds slightly for the first and last few chunks
  * For very short files (fewer than `min_path_length` * 2 chunks), consider reducing `min_path_length`

* **Sparse Content:**
  * When dealing with sparse dialog (long gaps between spoken lines):
    * Increase `initial_search_window_seconds` to account for potentially larger offsets
    * Consider timestamp-based pre-alignment for very sparse content

* **Overlapping Speech:**
  * When multiple speakers talk simultaneously:
    * Speaker information becomes crucial - prioritize matches with matching speakers
    * Be prepared for lower similarity scores due to transcription differences
    * Consider treating overlapping segments as potential smearing candidates

### Reference: Phonetic Similarity Calculation in Detail

The phonetic similarity calculation is the core of the alignment algorithm. Here's a more detailed explanation:

#### Basic Similarity Calculation

1. **Normalized Levenshtein Distance:**
   ```
   similarity = 1.0 - (levenshtein_distance(phonemes1, phonemes2) / max(len(phonemes1), len(phonemes2)))
   ```
   
   This approach works well for most cases but has limitations with very different length sequences.

2. **Improved Similarity with Length Consideration:**
   ```
   length_ratio = min(len(phonemes1), len(phonemes2)) / max(len(phonemes1), len(phonemes2))
   base_similarity = 1.0 - (levenshtein_distance(phonemes1, phonemes2) / max(len(phonemes1), len(phonemes2)))
   adjusted_similarity = base_similarity * (0.5 + 0.5 * length_ratio)
   ```
   
   This penalizes matches between very different length sequences while still allowing partial matches.

#### Advanced Phonetic Similarity

For more accurate phonetic matching, consider these enhancements:

1. **Phonetic Confusion Matrix:**
   * Create a matrix of common phonetic confusions (e.g., 'P'/'B', 'T'/'D', 'S'/'Z')
   * Use this matrix with Needleman-Wunsch or Smith-Waterman algorithms for sequence alignment
   * Example: Assign lower penalties (0.2-0.4) for confusable phonemes versus high penalties (0.8-1.0) for completely different phonemes

2. **Phonetic Feature Matching:**
   * Compare phonemes based on their linguistic features (voicing, place of articulation, etc.)
   * Example: 'P' and 'B' differ only in voicing, so they should have higher similarity than 'P' and 'N'
   * This approach requires a phonetic feature database but produces more linguistically accurate results

3. **Syllable-Based Matching:**
   * Group phonemes into syllables before comparison
   * Compare syllable patterns rather than individual phonemes
   * This can be more robust to minor transcription differences

#### Practical Implementation Tips

1. **Caching:**
   * Cache similarity calculations to avoid recomputing the same pairs
   * This is especially important when exploring the local search neighborhood

2. **Normalization:**
   * Always ensure the final similarity score is normalized to [0.0, 1.0]
   * Apply any speaker mismatch penalties after normalization

3. **Thresholds:**
   * Start with conservative thresholds (`phonetic_similarity_threshold` = 0.7, `smear_similarity_threshold` = 0.5)
   * Adjust based on your specific subtitle data characteristics
   * Consider dynamic thresholds that adapt to the overall similarity distribution in your data

### Reference: Signal Smearing Examples and Detection

Signal smearing occurs when content is split differently between the two subtitle sets. Here are common scenarios and detection strategies:

#### Common Smearing Scenarios

1. **One-to-Many Split:**
   ```
   Set 1: "What do you think about the proposal we discussed yesterday?"
   Set 2: "What do you think" | "about the proposal" | "we discussed yesterday?"
   ```
   
   In this case, one chunk in Set 1 corresponds to three chunks in Set 2.

2. **Many-to-One Merge:**
   ```
   Set 1: "I don't" | "know what" | "to say."
   Set 2: "I don't know what to say."
   ```
   
   Here, three chunks in Set 1 correspond to one chunk in Set 2.

3. **Boundary Shift:**
   ```
   Set 1: "Tell me what happened" | "after the meeting."
   Set 2: "Tell me" | "what happened after the meeting."
   ```
   
   The chunk boundary is in a different place, creating partial matches.

#### Detecting and Handling Smears

1. **Adjacent Chunk Merging:**
   * When a chunk has moderate similarity with multiple adjacent chunks in the other set:
     * Try merging the phonemes of adjacent chunks
     * Compare the merged sequence with the original chunk
     * If similarity improves significantly, record a smeared match

   Example pseudocode:
   ```
   if similarity(chunk1_i, chunk2_j) < threshold and similarity(chunk1_i, chunk2_j+1) < threshold:
       merged_phonemes = chunk2_j.phonemes + chunk2_j+1.phonemes
       merged_similarity = calculate_similarity(chunk1_i.phonemes, merged_phonemes)
       
       if merged_similarity > threshold:
           # Record smeared match (i maps to both j and j+1)
           record_smeared_match(i, [j, j+1], merged_similarity)
   ```

2. **Sliding Window Approach:**
   * Use a sliding window of varying sizes to detect potential smears
   * Compare each chunk with windows of different sizes in the other set
   * Select the window size that maximizes similarity

3. **Practical Implementation:**
   * Start with the simpler approach (Option 1 in the algorithm description)
   * Only implement the more complex approach if your subtitle data frequently contains smearing
   * Always validate smeared matches by checking if the implied offsets are consistent with the rest of the path

#### Example Smear Detection and Resolution

Consider this example:

```
Set 1, chunk i: "What do you think about the proposal?"
Set 2, chunk j: "What do you"
Set 2, chunk j+1: "think about"
Set 2, chunk j+2: "the proposal?"

Similarity(i, j) = 0.45 (below threshold)
Similarity(i, j+1) = 0.40 (below threshold)
Similarity(i, j+2) = 0.50 (below threshold)

Merged similarity(i, [j, j+1, j+2]) = 0.85 (above threshold)
```

The algorithm would:
1. Detect that individual similarities are below threshold
2. Try merging adjacent chunks
3. Find that the merged similarity is high
4. Record a smeared match: (i, [j, j+1, j+2])
5. Advance i by 1 and j by 3 in the path following

### Reference: Handling Speaker Mismatches

Speaker information can significantly improve alignment accuracy when available. Here's how to effectively use and handle speaker information:

#### Speaker Matching Strategies

1. **Binary Speaker Matching:**
   * The simplest approach: apply full penalty if speakers don't match
   * ```if speaker1_i != speaker2_j: similarity -= speaker_mismatch_penalty```
   * Works well when speaker labels are consistent between subtitle sets

2. **Fuzzy Speaker Matching:**
   * For cases where speaker labels might differ slightly between sets:
   * Use string similarity for speaker names (e.g., "John" vs "John Smith")
   * Consider speakers equivalent if similarity exceeds a threshold
   * ```if speaker_similarity(speaker1_i, speaker2_j) < speaker_match_threshold: similarity -= speaker_mismatch_penalty```

3. **Speaker Consistency Checking:**
   * Maintain a mapping of speakers between sets as matches are found
   * If a new match contradicts established speaker mappings, apply a higher penalty
   * This helps maintain consistent speaker assignments throughout the alignment

#### Handling Missing or Unreliable Speaker Information

1. **Partial Speaker Information:**
   * When only one set has speaker information:
     * Initialize with no speaker constraints
     * After finding initial matches, infer speaker mappings
     * Apply speaker constraints in subsequent iterations

2. **Inconsistent Speaker Labeling:**
   * If speaker labeling is inconsistent within a set:
     * Reduce `speaker_mismatch_penalty` to make it a soft constraint
     * Consider using speaker information only for chunks where confidence in speaker labeling is high

3. **Dynamic Speaker Penalty:**
   * Adjust `speaker_mismatch_penalty` based on confidence in speaker information
   * Start with a lower penalty and increase it as more consistent speaker mappings are established
   * ```dynamic_penalty = base_penalty * (1.0 - uncertainty_factor)```

   * ```dynamic_penalty = base_penalty * (1.0 - uncertainty_factor)```

#### Practical Implementation Guidelines

1. **Default Settings:**
   * Start with `speaker_mismatch_penalty = 0.5` when speaker information is available
   * Set `speaker_mismatch_penalty = 0` when speaker information is missing or unreliable

2. **Speaker-Aware Path Following:**
   * When extending the path, prioritize matches that maintain speaker consistency
   * Consider relaxing phonetic similarity requirements slightly for matches with consistent speakers

3. **Handling Speaker Changes:**
   * Be especially careful at speaker transition points
   * These are often points where subtitle timing can vary significantly
   * Consider allowing larger gaps around speaker changes

4. **Validation:**
   * After alignment, verify that speaker patterns are consistent between the aligned sets
   * Large discrepancies in speaker patterns may indicate alignment errors

## Testing Your Implementation

To test your implementation, we provide several challenge sets with different characteristics:

1. **Basic Alignment** - Simple subtitles with consistent offset
2. **Encoding Challenges** - Subtitles with various encoding issues and special characters
3. **Varying Offset** - Subtitles where the offset changes gradually throughout the file
4. **Missing Data** - Subtitles with missing fields and incomplete information

Your solution will be evaluated on how well it handles each of these challenges, both individually and in combination.

## Conclusion

Remember that the competition evaluates both your ability to clean messy data and implement a complex algorithm. The example input files showcase some typical issues, but in real usage, you could encounter more severe or different anomalies. Your solution should be flexible enough to handle unexpected data quirks.

Good luck!


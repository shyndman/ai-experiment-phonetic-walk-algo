
> [!Caution] Courtesy of Gemini, show-off loser

# Subtitle Alignment Algorithm (Phonetic Walking)
## 1. Goal
To accurately determine the temporal offset between two sets of subtitles (Set 1 and Set 2) derived from the same audio source. Set 2 is assumed to have a potentially significant, but relatively consistent, time offset compared to Set 1. The algorithm achieves this by identifying a sequence of corresponding subtitle chunks (an alignment path) based primarily on phonetic similarity.
## 2. Input
#### Set 1 Subtitles
A list/array of subtitle entries, ordered by time. Each entry should contain:

| `id1`       | Unique identifier for the chunk (e.g., index `i`)                                                                                                                                                                                                                                                                                         |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `t1_start`  | Start timestamp (e.g., in seconds)                                                                                                                                                                                                                                                                                                        |
| `t1_end`    | End timestamp (e.g., in seconds)                                                                                                                                                                                                                                                                                                          |
| `text1`     | The transcribed text content                                                                                                                                                                                                                                                                                                              |
| `phonemes1` | **(Required)** Pre-computed phonetic representation of `text1`. This should be a sequence of phoneme symbols (e.g., `['K', 'AE', 'T']` or `K AE T`). The process for generating this (e.g., CMU dictionary lookup, potentially with fallback for unknown words) is external to this core alignment algorithm but crucial for its success. |
| `speaker1`  | **(Optional but Recommended)** Identifier for the speaker, if available through diarization. Used as a strong constraint                                                                                                                                                                                                                  |
#### Set 2 Subtitles
Identical structure (`id2`, `t2_start`, `t2_end`, `text2`, `phonemes2`, `speaker2`). Also ordered by time.

#### Configuration Parameters

| name                              | (type) description                                                                                                                                                                                                                     |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `phonetic_similarity_threshold`   | (float, e.g., 0.7): Minimum normalized similarity score between phoneme sequences for two chunks to be considered a potential direct match.                                                                                            |
| `smear_similarity_threshold`      | (float, e.g., 0.5): Minimum normalized similarity score for considering partial matches contributing to a "smear" (see below)                                                                                                          |
| `initial_search_window_seconds`   | (float, e.g., 120.0): Max time difference (+/-) around a Set 1 chunk's start time to search for its initial match in Set 2.                                                                                                            |
| `local_search_neighborhood`       | (int tuple/object, e.g., `{'i_steps': [1, 2], 'j_steps': [1, 2]}`): Defines the relative indices `(di, dj)` to check for the *next* match when extending the path from `(i, j)`. E.g., check `(i+1, j+1)`, `(i+1, j+2)`, `(i+2, j+1)`. |
| `min_path_length`                 | (int, e.g., 5): Minimum number of match points required in the alignment path for it to be considered valid.                                                                                                                           |
| `max_consecutive_gaps`            | (int, e.g., 2): Maximum number of chunks that can be skipped consecutively in either set while trying to extend the path.                                                                                                              |
| `gap_penalty`                     | (float, e.g., 0.1): Penalty applied to path score for each skipped chunk (gap).                                                                                                                                                        |
| `speaker_mismatch_penalty`        | Penalty applied to similarity score if speakers mismatch (effectively preventing match if penalty is high). Set to 0 if speaker info is unavailable or unused.                                                                         |
| `offset_consistency_threshold_sd` | Maximum standard deviation allowed for the calculated offsets along the path for the alignment to be considered reliable.                                                                                                              |

## 3. Core Concepts
#### Chunk Representation
Each subtitle entry (`{id, start, end, text, phonemes, speaker}`) is a fundamental unit or "chunk".
#### Phonetic Similarity Function
`Similarity(chunk_i, chunk_j)`: Calculates similarity based on each of the arguments' phonemes.

**Algorithm:** Use a robust sequence alignment algorithm suitable for phonemes. Normalized Levenshtein distance is a simple option (`1 - levenshtein(p1, p2) / max(len(p1), len(p2))`). More advanced options like Needleman-Wunsch or Smith-Waterman allow for custom scoring matrices (e.g., slightly penalizing common phoneme confusions like 'P'/'B' or 'S'/'Z' less than completely different phonemes).

> [!attention] Normalization Required
> The result must be normalized, typically between 0.0 (completely dissimilar) and 1.0 (identical).

**Speaker Constraint:** If speaker information is used (`speaker_mismatch_penalty > 0`) and `speaker1[i] != speaker2[j]`, apply the penalty (e.g., `score = score - speaker_mismatch_penalty`, potentially clamped at 0).
#### Conceptual Similarity Matrix
A mental model of an M x N grid (M = # chunks in Set 1, N = # chunks in Set 2) where cell `(i, j)` contains `Similarity(chunk_i, chunk_j)`. The algorithm *navigates* this conceptual grid without necessarily computing all values.
#### Alignment Path
A sequence of index pairs `Path = [(i_0, j_0), (i_1, j_1), ..., (i_k, j_k)]` such that:
    *   `i_0 < i_1 < ... < i_k` (Indices in Set 1 are strictly increasing).
    *   `j_0 <= j_1 <= ... <= j_k` (Indices in Set 2 are non-decreasing; allows for smears where one `i` maps to multiple `j`'s, though the core walk primarily seeks increasing `j`).
    *   Each pair `(i_n, j_n)` represents a high-confidence match between `chunk_i_n` and `chunk_j_n`.
    *   The "steps" between consecutive pairs `(i_n, j_n)` and `(i_{n+1}, j_{n+1})` are small (e.g., `i_{n+1} - i_n <= max_consecutive_gaps + 1`).
#### Offset Calculation
For a matched pair `(i, j)`, the implied offset is `offset(i, j) = t2_start[j] - t1_start[i]`. The goal is to find a path where `offset(i, j)` is consistent across all pairs in the path.
#### Signal Smearing Detection
Occurs when a single chunk `i` in Set 1 corresponds linguistically to multiple adjacent chunks `j, j+1, ...` in Set 2 (or vice versa). Detected during path following when `Similarity(i, j)` is moderate, and `Similarity(i, j+1)` is also moderate, and perhaps the combined content of `j` and `j+1` yields a high similarity with `i`. The path needs to represent this relationship, potentially as `(i, [j, j+1])`.
## 4. Algorithm Steps
1.  **Preprocessing:**
    *   Load Set 1 and Set 2 subtitle data.
    *   Verify timestamps are sorted.
    *   Ensure `phonemes` field is populated for all chunks. Report errors/warnings for chunks where phonetic lookup failed.

2.  **Find Initial Anchor Match:**
    *   **Goal:** Find the first highly probable match to establish a starting point and rough offset.
    *   **Process:**
        *   Iterate through `i` from `0` up to a small number (e.g., `5` or `10`) in Set 1.
        *   For each `i`, determine the time-based search range in Set 2: `[t1_start[i] - initial_search_window_seconds, t1_start[i] + initial_search_window_seconds]`.
        *   Efficiently find all chunks `j` in Set 2 whose `t2_start[j]` falls within this time range.
        *   Calculate `score = Similarity(i, j)` for all candidate `j` found.
        *   Store the `(i, j, score)` triplets that exceed `phonetic_similarity_threshold`.
        *   After checking the initial batch of `i`'s, select the triplet `(i_0, j_0, score_0)` with the absolute highest score as the initial anchor.
    *   **Failure:** If no score exceeds the threshold within the initial search, the alignment fails. Consider reporting this or trying with relaxed parameters / wider initial search.

3.  **Follow the Path (Walking):**
    *   **Initialization:**
        *   `Path = [(i_0, j_0)]`
        *   `current_i = i_0`, `current_j = j_0`
        *   `consecutive_gaps = 0`
        *   `path_score = score_0` (or initialize differently)
    *   **Iteration Loop:** Continue as long as `current_i < M-1` and `current_j < N-1` (where M, N are lengths of Set 1, Set 2).
        *   **Find Best Next Step:**
            *   Identify candidate next indices `(next_i, next_j)` based on `local_search_neighborhood` relative to `(current_i, current_j)`. For example, check `(current_i+1, current_j+1)`, `(current_i+1, current_j+2)`, `(current_i+2, current_j+1)`. Ensure indices stay within bounds `[0, M-1]` and `[0, N-1]`.
            *   Calculate `score = Similarity(next_i, next_j)` for all valid candidates.
            *   Select the candidate `(best_next_i, best_next_j)` with the maximum score (`best_score`).
        *   **Evaluate Step:**
            *   **Strong Match:** If `best_score >= phonetic_similarity_threshold`:
                *   Append `(best_next_i, best_next_j)` to `Path`.
                *   Update `current_i = best_next_i`, `current_j = best_next_j`.
                *   `path_score += best_score`.
                *   `consecutive_gaps = 0`.
            *   **Potential Smear:** (Requires more complex logic) If `best_score` is below threshold but multiple candidates involving `current_i+1` (or `current_j+1`) have scores above `smear_similarity_threshold`, investigate smearing:
                *   *Option 1 (Simpler):* Treat the highest scoring one (even if below main threshold) as a weak match/gap if allowed.
                *   *Option 2 (Complex):* Attempt merging phonemes of adjacent chunks (e.g., `phonemes2[j+1] + phonemes2[j+2]`) and compare `phonemes1[i+1]` to this merged sequence. If *that* similarity is high, record a smeared match like `(i+1, [j+1, j+2])` in the path, advance `i` by 1, `j` by 2, and reset gap count. This needs careful state management.
            *   **Gap:** If `best_score` is below threshold (and smearing not detected/handled) AND `consecutive_gaps < max_consecutive_gaps`:
                *   Increment `consecutive_gaps`.
                *   Apply `gap_penalty` to `path_score`.
                *   Advance indices cautiously: typically increment the index (`i` or `j`) corresponding to the smaller step in the `best_next_i, best_next_j` pair that failed (e.g., if `(i+1, j+1)` failed, try starting next search from `(i+1, j+1)` again, effectively skipping either `i` or `j` depending on which index advances in the next successful step). Alternatively, simply advance both `current_i` and `current_j` by 1 as a simple gap strategy. *Needs refinement.*
            *   **Terminate Path:** If `best_score` is below threshold AND `consecutive_gaps >= max_consecutive_gaps`, break the loop (path ends here).
    *   **Loop Termination:** The loop also terminates if `current_i` or `current_j` reaches the end of their respective sets.

4.  **Validate Path and Calculate Offset:**
    *   **Check Length:** If `len(Path) < min_path_length`, alignment fails (path too short).
    *   **Calculate Offsets:** For each pair `(i, j)` in `Path`, calculate `offset_ij = t2_start[j] - t1_start[i]`. Store these offsets in a list.
    *   **Analyze Consistency:**
        *   Calculate the median of the offsets (more robust to outliers than mean). Let this be `median_offset`.
        *   (Optional: Filter out offsets that are far from the median - e.g., more than 2*SD away, then recalculate).
        *   Calculate the standard deviation (`sd_offset`) of the (potentially filtered) offsets.
    *   **Check Consistency:** If `sd_offset > offset_consistency_threshold_sd`, alignment fails (offset varies too much).
    *   **Success:** If path is long enough and offset is consistent, the alignment is successful. The final determined offset is `median_offset`.

5.  **Output:**
    *   Return an object indicating success or failure.
    *   On success:
        *   `status: 'success'`
        *   `offset_seconds: median_offset`
        *   `confidence: calculate_confidence_score(Path, sd_offset)` (e.g., based on path length, average similarity on path, inverse of sd_offset).
        *   `alignment_path: Path` (optional, for debugging).
    *   On failure:
        *   `status: 'failure'`
        *   `reason: 'no_anchor_found' | 'path_too_short' | 'offset_inconsistent'`
        *   `offset_seconds: null`

## 5. Handling Missing Data and Edge Cases

When implementing the Phonetic Walking algorithm, you'll encounter various real-world challenges with subtitle data. Here's how to handle common edge cases:

### Missing or Incomplete Data

1. **Missing Phonemes:**
   * If a chunk is missing phonemes (e.g., due to failed dictionary lookup), you have several options:
     * Skip the chunk entirely (treat it as a gap)
     * Use a fallback phonetic representation based on simple letter-to-sound rules
     * For very short words (1-3 characters), consider using the raw text for comparison
   * Always log chunks with missing phonemes for later analysis

2. **Missing Timestamps:**
   * If a chunk is missing start or end timestamps:
     * For missing end times, estimate using start time + average duration based on text length
     * For missing start times, estimate using previous chunk's end time + small gap (e.g., 0.1s)
     * If timestamps are completely absent, the chunk should be excluded from alignment

3. **Empty or Invalid Text:**
   * Chunks with empty text but valid timestamps should be preserved as potential gaps
   * Chunks with only non-speech markers (e.g., "[Music]", "[Applause]") should be excluded from phonetic matching but preserved in the final alignment

4. **Missing Speaker Information:**
   * When speaker information is missing for one or both sets:
     * Set `speaker_mismatch_penalty` to 0 for those comparisons
     * Consider using a reduced penalty when only one set has speaker information

### Handling Boundary Cases

1. **Start and End of Files:**
   * The algorithm may struggle to find matches at the very beginning or end of files
   * Consider relaxing thresholds slightly for the first and last few chunks
   * For very short files (fewer than `min_path_length` * 2 chunks), consider reducing `min_path_length`

2. **Sparse Content:**
   * When dealing with sparse dialog (long gaps between spoken lines):
     * Increase `initial_search_window_seconds` to account for potentially larger offsets
     * Consider timestamp-based pre-alignment for very sparse content

3. **Overlapping Speech:**
   * When multiple speakers talk simultaneously:
     * Speaker information becomes crucial - prioritize matches with matching speakers
     * Be prepared for lower similarity scores due to transcription differences
     * Consider treating overlapping segments as potential smearing candidates

## 6. Phonetic Similarity Calculation in Detail

The phonetic similarity calculation is the core of the alignment algorithm. Here's a more detailed explanation:

### Basic Similarity Calculation

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

### Advanced Phonetic Similarity

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

### Practical Implementation Tips

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

## 7. Signal Smearing Examples and Detection

Signal smearing occurs when content is split differently between the two subtitle sets. Here are common scenarios and detection strategies:

### Common Smearing Scenarios

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

### Detecting and Handling Smears

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

### Example Smear Detection and Resolution

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

## 8. Handling Speaker Mismatches

Speaker information can significantly improve alignment accuracy when available. Here's how to effectively use and handle speaker information:

### Speaker Matching Strategies

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

### Handling Missing or Unreliable Speaker Information

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

### Practical Implementation Guidelines

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


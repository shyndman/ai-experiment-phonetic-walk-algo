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

**Algorithm:** Use a robust sequence alignment algorithm suitable for phonemes. Normalized Levenshtein distance is a simple option (`1 - levenshtein(p1, p2) / max(len(p1), len(p2))`). More advanced options like Needleman-Wunsch or Smith-Waterman allow for custom scoring matrices.

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
                *   Advance indices cautiously: typically increment the index (`i` or `j`) corresponding to the smaller step in the `best_next_i, best_next_j` pair that failed (e.g., if `(i+1, j+1)` failed, try starting next search from `(i+1, j+1)` again, effectively skipping either `i` or `j` depending on which index advances in the next successful step). Alternatively, simply advance both `current_i` and `current_j` by 1 as a simple gap strategy.
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

## 5. Implementation Notes

For detailed implementation suggestions, examples, and tips on handling edge cases, please refer to the `instructions_and_tips.md` document. It contains comprehensive guidance on:

- Handling missing data and edge cases
- Phonetic similarity calculation techniques
- Signal smearing detection and resolution
- Speaker mismatch handling strategies

The core algorithm described in this document focuses on the essential steps and concepts, while the implementation details are left to the competitor's discretion.

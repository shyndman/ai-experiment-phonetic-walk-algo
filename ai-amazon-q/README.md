# AI Experiment: Subtitle Alignment Competition

## Overview

This project serves as a benchmark to evaluate the ability of various Large Language Models (LLMs) to implement a subtitle alignment solution. The competition consists of two main components:

1. **Freestyle Wrangler** - A data normalization and preprocessing component
2. **The Sync Showdown** - The core subtitle alignment algorithm implementation

Multiple LLMs will attempt to implement both components based on identical prompts, allowing for a fair comparison of their capabilities in understanding and accurately implementing complex algorithms with real-world data challenges.

## Competition Structure

### Freestyle Wrangler

The Freestyle Wrangler component focuses on data normalization and preprocessing. Competitors must handle various real-world subtitle data challenges, including:

- Inconsistent timestamp formats
- Encoding issues with quotes, special characters, and non-ASCII text
- Missing or incomplete data fields
- Overlapping timestamps
- Varying punctuation and formatting
- Random messages from release groups
- Partial foreign language text

Competitors have freedom to implement creative solutions for cleaning and normalizing the data, as long as the output conforms to the required interface for the alignment component.

### The Sync Showdown

The Sync Showdown component implements the core Phonetic Walk algorithm for subtitle alignment. This algorithm time-shifts subtitles when they are not properly synchronized with their associated dialog. The implementation must:

- Follow the detailed algorithm specification in ALGORITHM.md
- Handle edge cases appropriately
- Produce consistent and accurate alignment results
- Integrate seamlessly with the output from the Freestyle Wrangler component

## Data Normalization Requirements

Competitors are expected to handle data normalization as part of their solution. The competition provides raw subtitle data that contains various challenges and quirks commonly found in real-world subtitle files. Your implementation should:

- Convert all timestamps to a consistent format (floating-point seconds)
- Handle missing or malformed data gracefully
- Clean up encoding issues while preserving essential content
- Resolve overlapping timestamps
- Normalize punctuation differences between subtitle sets
- Identify and handle "foreign" content appropriately
- Filter out irrelevant content (like release group messages)

The goal is to create a robust solution that can be dropped into a working system with real human input and produce reliable results.

## Interface Requirements

To ensure consistent evaluation, all implementations must conform to specific interfaces:

1. **Freestyle Wrangler Interface**
   - Input: Raw JSON subtitle data
   - Output: Normalized subtitle data in a consistent format
   - Must handle all data normalization challenges

2. **The Sync Showdown Interface**
   - Input: Normalized subtitle data from the Wrangler component
   - Output: Alignment information including time offsets and confidence scores
   - Must implement the Phonetic Walk algorithm as specified

3. **End-to-End Interface**
   - Must support chaining the Wrangler and Showdown components together
   - Input: Raw JSON subtitle data
   - Output: Aligned subtitle data with appropriate time offsets

Detailed interface specifications are provided in the `interfaces` directory.

## Evaluation Criteria

Implementations will be judged on the following criteria:

1. **Correctness** (35 points)
   - Does the implementation correctly follow the algorithm as specified?
   - Does it handle edge cases appropriately?
   - Is the output consistent with expected results?

2. **Robustness** (25 points)
   - How well does the solution handle messy, real-world data?
   - Does it gracefully handle missing or malformed data?
   - Is it resilient to encoding issues and other data quirks?

3. **Code Quality** (20 points)
   - Is the code well-structured and organized?
   - Are variable names meaningful and consistent?
   - Is there appropriate error handling?
   - Is the code efficient in terms of time and space complexity?

4. **Completeness** (15 points)
   - Does the implementation include all aspects of both components?
   - Are there any missing features or functionality?

5. **Documentation** (5 points)
   - Is the code well-commented?
   - Are there clear explanations for non-obvious parts of the implementation?

## Testing Methodology

Each implementation will be tested in three phases:

1. **Freestyle Wrangler Test** - Testing only the data normalization component
2. **The Sync Showdown Test** - Testing only the alignment algorithm with pre-normalized data
3. **End-to-End Test** - Testing the complete pipeline from raw data to aligned subtitles

The test data includes:
- Subtitle files with various normalization challenges
- Subtitle files that are consistently early or late
- Subtitle files with varying offsets throughout
- Edge cases (very short files, files with unusual patterns, etc.)

## Participating LLMs

- Amazon Q
- Augment
- Claude Code
- Gemini 2.5 Pro (via Copilot)
- Plandex Cheap
- Plandex Strong

## Results Table

| LLM | Correctness (35) | Robustness (25) | Code Quality (20) | Completeness (15) | Documentation (5) | Total (100) |
|-----|------------------|-----------------|-------------------|-------------------|-------------------|-------------|
| [Augment Code](https://www.augmentcode.com/)<br>_Agent mode_ | | | | | | |
| [Gemini 2.5 Pro](https://aistudio.google.com/welcome)<br>_via CoPilot_ | | | | | | |
| [Plandex v2](https://plandex.ai/)<br>__**Strong** model pack__ | | | | | | |
| [Plandex v2](https://plandex.ai/)<br>__**Cheap** model pack__ | | | | | | |
| [Augment](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) | | | | | | |
| ... | | | | | | |

## Getting Started

1. Review the algorithm specification in ALGORITHM.md
2. Examine the sample subtitle data and schemas in the `data` directory
3. Implement both the Freestyle Wrangler and The Sync Showdown components
4. Test your implementation with the provided test data
5. Submit your solution according to the submission guidelines

## Important Notes

- The example input files showcase some typical issues, but in real usage, you could encounter more severe or different anomalies
- Your solution should be flexible enough to handle unexpected data quirks
- The competition evaluates both your ability to clean messy data and implement a complex algorithm

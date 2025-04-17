# AI Experiment: Phonetic Walk Implementation

## Overview

This project serves as a benchmark to evaluate the ability of various Large Language Models (LLMs) to implement a specific algorithm called "Phonetic Walk." This algorithm is designed to time-shift subtitles when they are not properly synchronized with their associated dialog.

Multiple LLMs will attempt to implement the same algorithm based on identical prompts, allowing for a fair comparison of their capabilities in understanding and accurately implementing a novel algorithm.

## The Phonetic Walk Algorithm

### Algorithm Description

```
[I will fill this section with the detailed description of the Phonetic Walk algorithm]
```

## The Prompt

```
[I will fill this section with the exact prompt given to each LLM]
```

## Evaluation Criteria

The LLMs will be judged on the following criteria:

1. **Correctness** (40 points)
   - Does the implementation correctly follow the algorithm as specified?
   - Does it handle edge cases appropriately?
   - Is the output consistent with expected results?

2. **Code Quality** (25 points)
   - Is the code well-structured and organized?
   - Are variable names meaningful and consistent?
   - Is there appropriate error handling?
   - Is the code efficient in terms of time and space complexity?

3. **Completeness** (20 points)
   - Does the implementation include all aspects of the algorithm?
   - Are there any missing features or components?

4. **Documentation** (15 points)
   - Is the code well-commented?
   - Are there clear explanations for non-obvious parts of the implementation?
   - Is there usage documentation or examples?

## Participating LLMs

- GPT-4
- Claude 3
- Gemini
- Llama 3
- [Add other LLMs as needed]

## Testing Methodology

1. Each LLM will be given the exact same prompt describing the Phonetic Walk algorithm.
2. The responses will be collected without modifications.
3. Each implementation will be tested with the same set of input data:
   - Synchronized subtitle/audio pairs (control)
   - Subtitle files that are consistently early or late
   - Subtitle files with varying offsets throughout
   - Edge cases (very short files, files with unusual patterns, etc.)

## Results Table

| LLM | Correctness (40) | Code Quality (25) | Completeness (20) | Documentation (15) | Total (100) |
|-----|------------------|-------------------|-------------------|-------------------|-------------|
| [Augment Code](https://www.augmentcode.com/)<br>_Agent mode_ | | | | | |
| [Gemini 2.5 Pro](https://aistudio.google.com/welcome)<br>_via CoPilot_ | | | | | |
| [Plandex v2](https://plandex.ai/)<br>__**Strong** model pack__ | | | | | |
| [Plandex v2](https://plandex.ai/)<br>__**Cheap** model pack__ | | | | | |
| [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) | | | | | |
| ... | | | | | |

## Analysis

[This section will be filled after conducting the experiment, analyzing the differences between implementations, strengths and weaknesses of each LLM, etc.]


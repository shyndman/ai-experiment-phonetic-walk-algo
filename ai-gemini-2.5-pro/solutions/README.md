# Subtitle Alignment Competition - Implementation Instructions

## Overview

This directory contains your implementation for the subtitle alignment competition. You need to implement two main components:

1. **Freestyle Wrangler** - Data normalization and preprocessing
2. **The Sync Showdown** - Subtitle alignment algorithm implementation

## File Structure

Your implementation must follow this file structure:

- `wrangler.py`: Contains the `normalize_subtitles()` function for the Freestyle Wrangler component
- `alignment.py`: Contains the `align_subtitles()` function for the Sync Showdown component

Only files in this `solutions/` directory will be evaluated. Make sure your implementation follows the interface requirements specified in the competition documentation.

## Implementation Requirements

### Freestyle Wrangler

Implement the following function in `wrangler.py`:

```python
def normalize_subtitles(caption):
    """
    Normalize a single subtitle caption.
    
    Args:
        caption: A dictionary containing raw subtitle data
        
    Returns:
        A normalized subtitle dictionary
    """
    # Your implementation here
```

This function should handle all aspects of normalization including:
- Converting timestamps to a consistent format (floating-point seconds)
- Cleaning text content (handling encoding issues, formatting, etc.)
- Handling missing or incomplete data
- Generating or validating phonetic representations

### The Sync Showdown

Implement the following function in `alignment.py`:

```python
def align_subtitles(subtitles1, subtitles2, config=None):
    """
    Align two sets of normalized subtitles.
    
    Args:
        subtitles1: First set of normalized subtitles
        subtitles2: Second set of normalized subtitles
        config: Optional configuration parameters
        
    Returns:
        An alignment result with offset and confidence
    """
    # Your implementation here
```

This function should implement the Phonetic Walk algorithm as described in the ALGORITHM.md document.

## Implementation Freedom

You have complete freedom in how you implement the solutions for both components. The only requirements are:

1. Your implementation must use the function signatures specified above
2. Your implementation must return data in the expected format
3. Your solution must handle the challenges described in the competition documentation

Beyond these minimal requirements, you are free to:

- Choose any algorithms, data structures, or approaches you prefer
- Create any helper functions or utility modules as needed
- Implement the solution in your own style and organization
- Use any libraries or tools that are appropriate for the task

## Code Quality Requirements

Your code will be evaluated not only for correctness but also for quality. Please ensure your implementation:

1. **Passes Linting**: Your code should pass all Ruff linting checks. A `.ruff.toml` configuration file is provided in your workspace.
2. **Uses Modern Python**: Avoid deprecated functions, methods, or libraries.
3. **Includes Type Hints**: All functions should have proper type annotations.
4. **Has Documentation**: Include docstrings for all functions and classes.
5. **Handles Errors Gracefully**: Implement appropriate error handling for edge cases.
6. **Is Efficient**: Consider time and space complexity in your implementation.

## Testing Your Implementation

You can test your implementation using the provided test data in the `data/` directory. The evaluation will be performed on similar but different test data.

To run the linter to check your code:

```bash
source ../.venv/bin/activate
ruff check .
```

And automatically fix some issues with:

```bash
ruff check --fix .
```

## Submission

Your final submission will be evaluated based solely on the contents of this `solutions/` directory. Make sure your implementation follows all the requirements specified in the competition documentation.

Good luck!

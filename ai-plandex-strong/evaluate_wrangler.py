#!/usr/bin/env python3
"""
Evaluation Script for the Freestyle Wrangler Component

This script evaluates the Freestyle Wrangler component of competitor solutions
by testing their ability to normalize subtitle data with various challenges.
"""

import os
import sys
import json
import time
import argparse
import importlib.util
from pathlib import Path
from typing import Any
import traceback


def load_module_from_path(module_name: str, file_path: str):
    """
    Dynamically load a Python module from a file path.

    Args:
        module_name: Name to give the loaded module
        file_path: Path to the Python file to load

    Returns:
        The loaded module

    Raises:
        ImportError: If the module cannot be loaded
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_subtitles(file_path: str) -> list[dict[str, Any]]:
    """
    Load subtitle data from a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        list of subtitle dictionaries

    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_normalized_subtitle(subtitle: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate that a normalized subtitle meets the requirements.

    Args:
        subtitle: A normalized subtitle dictionary

    Returns:
        A tuple (is_valid, errors) where is_valid is True if the subtitle is valid,
        and errors is a list of error messages if it's not valid
    """
    errors = []

    # Check required fields
    required_fields = ['id', 'start', 'end', 'text', 'phonemes']
    for field in required_fields:
        if field not in subtitle:
            errors.append(f"Missing required field: {field}")

    # Check field types
    if 'id' in subtitle and not isinstance(subtitle['id'], (int, str)):
        errors.append(f"Field 'id' must be an integer or string, got {type(subtitle['id'])}")

    if 'start' in subtitle and not isinstance(subtitle['start'], (int, float)):
        errors.append(f"Field 'start' must be a number, got {type(subtitle['start'])}")

    if 'end' in subtitle and not isinstance(subtitle['end'], (int, float)):
        errors.append(f"Field 'end' must be a number, got {type(subtitle['end'])}")

    if 'text' in subtitle and not isinstance(subtitle['text'], str):
        errors.append(f"Field 'text' must be a string, got {type(subtitle['text'])}")

    if 'phonemes' in subtitle and not isinstance(subtitle['phonemes'], list):
        errors.append(f"Field 'phonemes' must be a list, got {type(subtitle['phonemes'])}")
    elif 'phonemes' in subtitle:
        for i, phoneme in enumerate(subtitle['phonemes']):
            if not isinstance(phoneme, str):
                errors.append(f"Phoneme at index {i} must be a string, got {type(phoneme)}")

    if 'speaker' in subtitle and not isinstance(subtitle['speaker'], str):
        errors.append(f"Field 'speaker' must be a string, got {type(subtitle['speaker'])}")

    # Check timestamp ordering
    if 'start' in subtitle and 'end' in subtitle:
        if subtitle['start'] > subtitle['end']:
            errors.append(f"Start time ({subtitle['start']}) is greater than end time ({subtitle['end']})")

    return len(errors) == 0, errors


def evaluate_wrangler(
    competitor_dir: str,
    test_data_dir: str,
    output_dir: str | None = None,
    verbose: bool = False
) -> dict[str, Any]:
    """
    Evaluate the Freestyle Wrangler component of a competitor solution.

    Args:
        competitor_dir: Path to the competitor's directory
        test_data_dir: Path to the test data directory
        output_dir: Path to save evaluation results (optional)
        verbose: Whether to print verbose output

    Returns:
        A dictionary containing evaluation results
    """
    # Prepare paths
    competitor_name = os.path.basename(competitor_dir)
    wrangler_path = os.path.join(competitor_dir, "solutions", "wrangler.py")

    if not os.path.exists(wrangler_path):
        print(f"Error: Wrangler implementation not found at {wrangler_path}")
        return {
            "competitor": competitor_name,
            "status": "error",
            "error": f"Wrangler implementation not found at {wrangler_path}",
            "score": 0,
            "details": {}
        }

    # Load the competitor's wrangler module
    try:
        wrangler_module = load_module_from_path("wrangler", wrangler_path)
        normalize_subtitles = getattr(wrangler_module, "normalize_subtitles")
    except Exception as e:
        error_msg = f"Error loading wrangler module: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return {
            "competitor": competitor_name,
            "status": "error",
            "error": error_msg,
            "score": 0,
            "details": {}
        }

    # Find test data sets
    test_sets = []
    for root, dirs, files in os.walk(test_data_dir):
        if "set1-subtitles.json" in files and "set2-subtitles.json" in files:
            test_set_name = os.path.relpath(root, test_data_dir)
            if test_set_name == ".":
                test_set_name = "default"
            test_sets.append((test_set_name, root))

    if not test_sets:
        print(f"Error: No test data found in {test_data_dir}")
        return {
            "competitor": competitor_name,
            "status": "error",
            "error": f"No test data found in {test_data_dir}",
            "score": 0,
            "details": {}
        }

    # Evaluate each test set
    results = {
        "competitor": competitor_name,
        "status": "success",
        "score": 0,
        "details": {}
    }

    total_score = 0
    max_score = 0

    for test_set_name, test_set_dir in test_sets:
        if verbose:
            print(f"Evaluating test set: {test_set_name}")

        set1_path = os.path.join(test_set_dir, "set1-subtitles.json")
        set2_path = os.path.join(test_set_dir, "set2-subtitles.json")

        set1_subtitles = load_subtitles(set1_path)
        set2_subtitles = load_subtitles(set2_path)

        set1_results = evaluate_wrangler_on_set(normalize_subtitles, set1_subtitles, "set1", verbose)
        set2_results = evaluate_wrangler_on_set(normalize_subtitles, set2_subtitles, "set2", verbose)

        # Calculate scores
        set1_score = set1_results["score"]
        set2_score = set2_results["score"]
        test_set_score = (set1_score + set2_score) / 2

        total_score += test_set_score
        max_score += 100  # Maximum score per test set

        results["details"][test_set_name] = {
            "set1": set1_results,
            "set2": set2_results,
            "score": test_set_score
        }

        if verbose:
            print(f"Test set {test_set_name} score: {test_set_score:.2f}/100")

    # Calculate overall score (normalized to 100)
    if max_score > 0:
        results["score"] = (total_score / max_score) * 100

    if verbose:
        print(f"Overall score: {results['score']:.2f}/100")

    # Save results if output directory is provided
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{competitor_name}_wrangler_results.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

        if verbose:
            print(f"Results saved to {output_path}")

    return results


def evaluate_wrangler_on_set(
    normalize_subtitles_func,
    subtitles: list[dict[str, Any]],
    set_name: str,
    verbose: bool = False
) -> dict[str, Any]:
    """
    Evaluate the Freestyle Wrangler on a single subtitle set.

    Args:
        normalize_subtitles_func: The normalize_subtitles function from the competitor's solution
        subtitles: list of subtitle dictionaries to normalize
        set_name: Name of the subtitle set (for reporting)
        verbose: Whether to print verbose output

    Returns:
        A dictionary containing evaluation results for this set
    """
    results = {
        "total_subtitles": len(subtitles),
        "successful_normalizations": 0,
        "failed_normalizations": 0,
        "validation_errors": 0,
        "error_details": [],
        "processing_time": 0,
        "score": 0
    }

    normalized_subtitles = []
    start_time = time.time()

    # Process each subtitle
    for i, subtitle in enumerate(subtitles):
        try:
            normalized = normalize_subtitles_func(subtitle)
            normalized_subtitles.append(normalized)

            # Validate the normalized subtitle
            is_valid, errors = validate_normalized_subtitle(normalized)
            if is_valid:
                results["successful_normalizations"] += 1
            else:
                results["validation_errors"] += 1
                error_detail = {
                    "subtitle_index": i,
                    "errors": errors
                }
                results["error_details"].append(error_detail)

                if verbose:
                    print(f"Validation errors for subtitle {i} in {set_name}:")
                    for error in errors:
                        print(f"  - {error}")

        except Exception as e:
            results["failed_normalizations"] += 1
            error_detail = {
                "subtitle_index": i,
                "exception": str(e),
                "traceback": traceback.format_exc()
            }
            results["error_details"].append(error_detail)

            if verbose:
                print(f"Error normalizing subtitle {i} in {set_name}: {str(e)}")

    results["processing_time"] = time.time() - start_time

    # Calculate score (out of 100)
    if results["total_subtitles"] > 0:
        # 70% for successful normalizations
        normalization_score = (results["successful_normalizations"] / results["total_subtitles"]) * 70

        # 30% for validation (no errors)
        validation_score = ((results["successful_normalizations"] - results["validation_errors"]) / results["total_subtitles"]) * 30

        results["score"] = max(0, normalization_score + validation_score)

    return results


def main():
    parser = argparse.ArgumentParser(description="Evaluate the Freestyle Wrangler component")
    parser.add_argument("competitor_dir", help="Path to the competitor's directory")
    parser.add_argument("--test-data", default="data", help="Path to the test data directory")
    parser.add_argument("--output-dir", help="Path to save evaluation results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print verbose output")

    args = parser.parse_args()

    results = evaluate_wrangler(
        args.competitor_dir,
        args.test_data,
        args.output_dir,
        args.verbose
    )

    print(f"Competitor: {results['competitor']}")
    print(f"Status: {results['status']}")
    print(f"Score: {results['score']:.2f}/100")

    if results['status'] == "error":
        print(f"Error: {results['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()

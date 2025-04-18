#!/usr/bin/env python3
"""
Setup Competition Directories

This script sets up the competition directories by copying schemas and sample data
to each AI competitor directory.
"""

import os
import shutil
import json
import argparse
from pathlib import Path

# AI competitor directories
AI_DIRS = [
    "ai-augment",
    "ai-claude-code",
    "ai-gemini-2.5-pro",
    "ai-plandex-cheap",
    "ai-plandex-strong"
]

def create_directories():
    """Create the AI competitor directories if they don't exist."""
    for ai_dir in AI_DIRS:
        os.makedirs(ai_dir, exist_ok=True)
        print(f"Created directory: {ai_dir}")

def copy_schemas_and_data(data_dir="data"):
    """
    Copy schemas and sample data to each AI competitor directory.

    Args:
        data_dir: Directory containing the schemas and sample data
    """
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)

    # Generate sample data if it doesn't exist
    if not os.path.exists(os.path.join(data_dir, "set1-schema.json")):
        print("Sample data not found. Generating sample data...")
        try:
            import data_generator
            data_generator.generate_test_data(data_dir, num_entries=30, offset=3.5, include_challenges=True)
        except ImportError:
            print("Warning: data_generator.py not found. Skipping sample data generation.")

    # Copy schemas and sample data to each AI competitor directory
    for ai_dir in AI_DIRS:
        # Create data subdirectory in each AI directory
        ai_data_dir = os.path.join(ai_dir, "data")
        os.makedirs(ai_data_dir, exist_ok=True)

        # Copy schema and sample data files
        for filename in ["set1-schema.json", "set1-subtitles.json",
                         "set2-schema.json", "set2-subtitles.json"]:
            src_file = os.path.join(data_dir, filename)
            dst_file = os.path.join(ai_data_dir, filename)

            if os.path.exists(src_file):
                shutil.copy2(src_file, dst_file)
                print(f"Copied {src_file} to {dst_file}")
            else:
                print(f"Warning: {src_file} not found. Skipping.")

def copy_interfaces():
    """Copy interface definitions to each AI competitor directory."""
    if not os.path.exists("interfaces"):
        print("Warning: interfaces directory not found. Skipping interface copying.")
        return

    for ai_dir in AI_DIRS:
        # Create interfaces subdirectory in each AI directory
        ai_interfaces_dir = os.path.join(ai_dir, "interfaces")
        os.makedirs(ai_interfaces_dir, exist_ok=True)

        # Copy all files from interfaces directory
        for filename in os.listdir("interfaces"):
            if filename.endswith(".py"):
                src_file = os.path.join("interfaces", filename)
                dst_file = os.path.join(ai_interfaces_dir, filename)
                shutil.copy2(src_file, dst_file)
                print(f"Copied {src_file} to {dst_file}")

def copy_documentation():
    """Copy README.md, ALGORITHM.md, and instructions_and_tips.md to each AI competitor directory."""
    for ai_dir in AI_DIRS:
        for filename in ["README.md", "ALGORITHM.md", "instructions_and_tips.md"]:
            if os.path.exists(filename):
                dst_file = os.path.join(ai_dir, filename)
                shutil.copy2(filename, dst_file)
                print(f"Copied {filename} to {dst_file}")
            else:
                print(f"Warning: {filename} not found. Skipping.")


def copy_solution_templates():
    """Copy simplified solution templates to each AI competitor directory."""
    for ai_dir in AI_DIRS:
        # Create solutions directory
        solutions_dir = os.path.join(ai_dir, "solutions")
        os.makedirs(solutions_dir, exist_ok=True)

        # Copy solution README
        solutions_readme = os.path.join(ai_dir, "solutions", "README.md")
        if os.path.exists(solutions_readme):
            print(f"Solutions README already exists at {solutions_readme}")
        elif os.path.exists("solutions_template/README.md"):
            shutil.copy2("solutions_template/README.md", solutions_readme)
            print(f"Copied solutions README to {solutions_readme}")

        # Copy minimal solution template files
        for filename in ["wrangler.py", "alignment.py"]:
            dst_file = os.path.join(solutions_dir, filename)
            if os.path.exists(dst_file):
                print(f"Solution file already exists at {dst_file}")
            elif os.path.exists(f"solutions_template/{filename}"):
                shutil.copy2(f"solutions_template/{filename}", dst_file)
                print(f"Copied solution template {filename} to {dst_file}")
            else:
                # If template directory doesn't exist, copy from another competitor if available
                for other_dir in AI_DIRS:
                    if other_dir != ai_dir:
                        src_file = os.path.join(other_dir, "solutions", filename)
                        if os.path.exists(src_file):
                            shutil.copy2(src_file, dst_file)
                            print(f"Copied solution template {filename} from {other_dir} to {dst_file}")
                            break

        # Copy .ruff.toml configuration
        ruff_config = os.path.join(ai_dir, ".ruff.toml")
        if os.path.exists(ruff_config):
            print(f"Ruff configuration already exists at {ruff_config}")
        elif os.path.exists(".ruff.toml"):
            shutil.copy2(".ruff.toml", ruff_config)
            print(f"Copied .ruff.toml to {ruff_config}")


def copy_requirements():
    """Copy requirements.txt to each AI competitor directory."""
    if not os.path.exists("requirements.txt"):
        print("Warning: requirements.txt not found. Skipping.")
        return

    for ai_dir in AI_DIRS:
        dst_file = os.path.join(ai_dir, "requirements.txt")
        shutil.copy2("requirements.txt", dst_file)
        print(f"Copied requirements.txt to {dst_file}")


def copy_evaluation_scripts():
    """Copy evaluation scripts to each AI competitor directory."""
    evaluation_scripts = [
        "evaluate_wrangler.py",
        "evaluate_alignment.py",
        "evaluate_end_to_end.py"
    ]

    for script in evaluation_scripts:
        if not os.path.exists(script):
            print(f"Warning: {script} not found. Skipping.")
            continue

        for ai_dir in AI_DIRS:
            dst_file = os.path.join(ai_dir, script)
            shutil.copy2(script, dst_file)
            print(f"Copied {script} to {dst_file}")
    for ai_dir in AI_DIRS:
        # Create interfaces subdirectory in each AI directory
        ai_interfaces_dir = os.path.join(ai_dir, "interfaces")
        os.makedirs(ai_interfaces_dir, exist_ok=True)

        # Copy all files from interfaces directory
        for filename in os.listdir("interfaces"):
            if filename.endswith(".py"):
                src_file = os.path.join("interfaces", filename)
                dst_file = os.path.join(ai_interfaces_dir, filename)
                shutil.copy2(src_file, dst_file)
                print(f"Copied {src_file} to {dst_file}")

def copy_documentation():
    """Copy README.md, ALGORITHM.md, and instructions_and_tips.md to each AI competitor directory."""
    for ai_dir in AI_DIRS:
        for filename in ["README.md", "ALGORITHM.md", "instructions_and_tips.md"]:
            if os.path.exists(filename):
                dst_file = os.path.join(ai_dir, filename)
                shutil.copy2(filename, dst_file)
                print(f"Copied {filename} to {dst_file}")
            else:
                print(f"Warning: {filename} not found. Skipping.")

def main():
    parser = argparse.ArgumentParser(description="Set up competition directories")
    parser.add_argument("--data-dir", default="data", help="Directory containing schemas and sample data")
    args = parser.parse_args()

    create_directories()
    copy_schemas_and_data(args.data_dir)
    copy_interfaces()
    copy_documentation()
    copy_solution_templates()
    copy_requirements()
    copy_evaluation_scripts()

    print("Competition directories setup complete!")


if __name__ == "__main__":
    main()

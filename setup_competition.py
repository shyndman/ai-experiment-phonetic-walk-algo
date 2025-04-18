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
    "ai-gpt4",
    "ai-claude",
    "ai-gemini",
    "ai-llama3"
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

def main():
    parser = argparse.ArgumentParser(description="Set up competition directories")
    parser.add_argument("--data-dir", default="data", help="Directory containing schemas and sample data")
    args = parser.parse_args()
    
    create_directories()
    copy_schemas_and_data(args.data_dir)
    copy_interfaces()
    copy_documentation()
    
    print("Competition directories setup complete!")

if __name__ == "__main__":
    main()


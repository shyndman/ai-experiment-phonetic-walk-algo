#!/usr/bin/env python3
"""
Test Data Generator for Subtitle Alignment Competition

This script generates test data with various challenges to test both the
"Freestyle Wrangler" and "The Sync Showdown" components of the competition.
"""

import json
import random
import os
import argparse
import string
import re
from datetime import datetime, timedelta
import unicodedata

# Constants for data generation
SPEAKERS = ["Speaker 1", "Speaker 2", "Speaker 3", "Speaker 4", "Speaker 5"]
FOREIGN_PHRASES = [
    "你好，世界", 
    "こんにちは世界", 
    "안녕하세요 세계", 
    "Привет, мир",
    "مرحبا بالعالم"
]
RELEASE_GROUP_MESSAGES = [
    "[SubsBy-ReleaseGroup]",
    ">>> Subtitles by SubTeam <<<",
    "-- Visit www.example.com for more subtitles --",
    "*** PLEASE SUPPORT OUR WORK ***",
    "== Synced and corrected by SubsTeam =="
]
ENCODING_ISSUES = {
    "'": ["'", "´", "`", "'"],
    '"': ['"', '"', '″', '„', '«', '»'],
    "-": ["–", "—", "−", "‐", "‑"],
    "...": ["…", ". . .", ".."],
    "&": ["&amp;", "＆", "﹠", "＆"],
}

# Phoneme mapping for English words
PHONEME_MAPPING = {
    'A': ['AH', 'AE', 'AA', 'AO', 'AW', 'AY'],
    'B': ['B'],
    'C': ['CH', 'K', 'S'],
    'D': ['D', 'DH'],
    'E': ['EH', 'ER', 'EY'],
    'F': ['F'],
    'G': ['G'],
    'H': ['HH'],
    'I': ['IH', 'IY'],
    'J': ['JH'],
    'K': ['K'],
    'L': ['L'],
    'M': ['M'],
    'N': ['N', 'NG'],
    'O': ['OW', 'OY'],
    'P': ['P'],
    'Q': ['K'],
    'R': ['R'],
    'S': ['S', 'SH'],
    'T': ['T', 'TH'],
    'U': ['UH', 'UW'],
    'V': ['V'],
    'W': ['W'],
    'X': ['K', 'S'],
    'Y': ['Y'],
    'Z': ['Z', 'ZH'],
}

# Common words for generating subtitles
COMMON_WORDS = [
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "I", 
    "it", "for", "not", "on", "with", "he", "as", "you", "do", "at", 
    "this", "but", "his", "by", "from", "they", "we", "say", "her", "she", 
    "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", 
    "so", "up", "out", "if", "about", "who", "get", "which", "go", "me", 
    "when", "make", "can", "like", "time", "no", "just", "him", "know", "take", 
    "people", "into", "year", "your", "good", "some", "could", "them", "see", "other", 
    "than", "then", "now", "look", "only", "come", "its", "over", "think", "also", 
    "back", "after", "use", "two", "how", "our", "work", "first", "well", "way", 
    "even", "new", "want", "because", "any", "these", "give", "day", "most", "us"
]

def generate_word():
    """Generate a random word from common words list."""
    return random.choice(COMMON_WORDS)

def generate_sentence(min_words=3, max_words=15):
    """Generate a random sentence."""
    num_words = random.randint(min_words, max_words)
    words = [generate_word() for _ in range(num_words)]
    words[0] = words[0].capitalize()
    return " ".join(words) + random.choice([".", "!", "?"])

def generate_phonemes(text):
    """Generate mock phonemes for text."""
    # Simple phoneme generation - not linguistically accurate
    phonemes = []
    for char in text.upper():
        if char in PHONEME_MAPPING and random.random() > 0.1:  # 10% chance of missing phoneme
            phoneme = random.choice(PHONEME_MAPPING[char])
            phonemes.append(phoneme)
    
    # Randomly introduce phoneme errors (5% chance)
    for i in range(len(phonemes)):
        if random.random() < 0.05:
            if random.random() < 0.5:
                # Replace with similar phoneme
                char = phonemes[i][0]
                if char in PHONEME_MAPPING:
                    phonemes[i] = random.choice(PHONEME_MAPPING[char])
            else:
                # Delete phoneme
                phonemes[i] = ""
    
    # Filter out empty phonemes
    phonemes = [p for p in phonemes if p]
    
    return phonemes

def format_timestamp(seconds, format_type=None):
    """Format seconds into different timestamp formats."""
    if format_type is None:
        format_type = random.choice(["standard", "decimal", "frames"])
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    
    if format_type == "standard":
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace(".", ":")
    elif format_type == "decimal":
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    elif format_type == "frames":
        frames = int((secs - int(secs)) * 30)  # Assuming 30fps
        return f"{hours:02d}:{minutes:02d}:{int(secs):02d}:{frames:02d}"
    else:
        return str(seconds)

def introduce_encoding_issues(text, probability=0.3):
    """Introduce encoding issues into text."""
    if random.random() > probability:
        return text
    
    for original, replacements in ENCODING_ISSUES.items():
        if original in text and random.random() < 0.3:
            replacement = random.choice(replacements)
            text = text.replace(original, replacement, 1)
    
    # Randomly add a zero-width space or other invisible character
    if random.random() < 0.1:
        pos = random.randint(0, len(text) - 1)
        invisible_char = random.choice(['\u200B', '\u200C', '\u200D', '\u2060'])
        text = text[:pos] + invisible_char + text[pos:]
    
    return text

def introduce_transcription_errors(text, probability=0.2):
    """Introduce transcription errors into text."""
    if random.random() > probability:
        return text
    
    words = text.split()
    if not words:
        return text
    
    error_type = random.choice(["typo", "missing_word", "extra_word", "word_replacement"])
    
    if error_type == "typo" and words:
        # Replace a character in a random word with a typo
        word_idx = random.randint(0, len(words) - 1)
        word = words[word_idx]
        if len(word) > 1:
            char_idx = random.randint(0, len(word) - 1)
            typo_char = random.choice(string.ascii_lowercase)
            word = word[:char_idx] + typo_char + word[char_idx+1:]
            words[word_idx] = word
    
    elif error_type == "missing_word" and len(words) > 2:
        # Remove a random word
        word_idx = random.randint(0, len(words) - 1)
        words.pop(word_idx)
    
    elif error_type == "extra_word":
        # Add a random word
        word_idx = random.randint(0, len(words))
        words.insert(word_idx, generate_word())
    
    elif error_type == "word_replacement" and words:
        # Replace a word with another random word
        word_idx = random.randint(0, len(words) - 1)
        words[word_idx] = generate_word()
    
    return " ".join(words)

def introduce_punctuation_variations(text, probability=0.3):
    """Introduce variations in punctuation."""
    if random.random() > probability:
        return text
    
    variation_type = random.choice(["newlines", "commas", "quotes", "apostrophes"])
    
    if variation_type == "newlines":
        # Add or remove newlines
        if "\n" in text and random.random() < 0.5:
            # Remove a newline
            text = text.replace("\n", " ", 1)
        else:
            # Add a newline
            words = text.split()
            if len(words) > 3:
                split_point = random.randint(1, len(words) - 2)
                text = " ".join(words[:split_point]) + "\n" + " ".join(words[split_point:])
    
    elif variation_type == "commas":
        # Add or remove commas
        if "," in text and random.random() < 0.5:
            # Remove a comma
            text = text.replace(", ", " ", 1)
        else:
            # Add a comma
            words = text.split()
            if len(words) > 3:
                comma_point = random.randint(1, len(words) - 2)
                words[comma_point] = words[comma_point] + ","
                text = " ".join(words)
    
    elif variation_type == "quotes":
        # Change quote style
        if '"' in text:
            replacement = random.choice(['"', '"', '«', '»'])
            text = text.replace('"', replacement)
    
    elif variation_type == "apostrophes":
        # Change apostrophe style
        if "'" in text:
            replacement = random.choice(["'", "´", "`"])
            text = text.replace("'", replacement)
    
    return text

def generate_subtitle_entry(idx, start_time, end_time, offset=0, format_type=None, include_challenges=True):
    """Generate a single subtitle entry."""
    # Decide if this will be a special entry
    is_special = random.random() < 0.1 and include_challenges
    
    if is_special:
        special_type = random.choice(["foreign", "release_group", "encoding_heavy", "missing_data"])
        
        if special_type == "foreign":
            text = random.choice(FOREIGN_PHRASES)
            speaker = random.choice(SPEAKERS)
        elif special_type == "release_group":
            text = random.choice(RELEASE_GROUP_MESSAGES)
            speaker = ""  # No speaker for release group messages
        elif special_type == "encoding_heavy":
            text = introduce_encoding_issues(generate_sentence(), 0.9)
            speaker = random.choice(SPEAKERS)
        elif special_type == "missing_data":
            text = generate_sentence()
            speaker = "" if random.random() < 0.5 else random.choice(SPEAKERS)
    else:
        text = generate_sentence()
        speaker = random.choice(SPEAKERS)
    
    # Apply various transformations if challenges are enabled
    if include_challenges:
        # Introduce encoding issues
        text = introduce_encoding_issues(text)
        
        # Introduce transcription errors
        text = introduce_transcription_errors(text)
        
        # Introduce punctuation variations
        text = introduce_punctuation_variations(text)
    
    # Generate phonemes
    phonemes = generate_phonemes(text)
    
    # Apply offset to second set
    if offset != 0:
        start_time += offset
        end_time += offset
    
    # Format timestamps
    start_formatted = format_timestamp(start_time, format_type)
    end_formatted = format_timestamp(end_time, format_type)
    
    # Sometimes create overlapping timestamps
    if include_challenges and random.random() < 0.1:
        # Make this subtitle overlap with the next one
        end_time += random.uniform(0.1, 0.5)
        end_formatted = format_timestamp(end_time, format_type)
    
    # Sometimes omit end timestamp
    if include_challenges and random.random() < 0.05:
        end_formatted = ""
    
    # Create the entry
    entry = {
        "id": idx,
        "start": start_formatted,
        "end": end_formatted,
        "text": text,
        "phonemes": phonemes
    }
    
    # Add speaker if available
    if speaker:
        entry["speaker"] = speaker
    
    return entry, end_time

def generate_subtitle_set(num_entries=50, base_duration=2.0, gap=0.5, offset=0, 
                          format_type=None, include_challenges=True):
    """Generate a set of subtitle entries."""
    entries = []
    current_time = random.uniform(0, 10)  # Random start time
    
    for i in range(num_entries):
        # Determine duration for this subtitle
        duration = random.uniform(base_duration * 0.5, base_duration * 1.5)
        
        # Generate the entry
        entry, end_time = generate_subtitle_entry(
            i, current_time, current_time + duration, 
            offset, format_type, include_challenges
        )
        entries.append(entry)
        
        # Update current time for next entry
        current_time = end_time + random.uniform(gap * 0.5, gap * 1.5)
        
        # Occasionally create a longer gap
        if random.random() < 0.1:
            current_time += random.uniform(2, 5)
    
    return entries

def create_schema(include_speaker=True):
    """Create a schema for the subtitle data."""
    properties = {
        "id": {"type": "integer", "description": "Unique identifier for the subtitle entry"},
        "start": {"type": "string", "description": "Start timestamp for the subtitle"},
        "end": {"type": "string", "description": "End timestamp for the subtitle"},
        "text": {"type": "string", "description": "The subtitle text content"},
        "phonemes": {"type": "array", "items": {"type": "string"}, "description": "Phonetic representation of the text"}
    }
    
    if include_speaker:
        properties["speaker"] = {"type": "string", "description": "Speaker identifier"}
    
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "items": {
            "type": "object",
            "properties": properties,
            "required": ["id", "start", "text", "phonemes"]
        }
    }
    
    return schema

def generate_test_data(output_dir, num_entries=50, offset=5.0, include_challenges=True):
    """Generate test data for the subtitle alignment competition."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate set 1 with standard format
    set1 = generate_subtitle_set(
        num_entries=num_entries,
        format_type="standard",
        include_challenges=include_challenges
    )
    
    # Generate set 2 with decimal format and offset
    set2 = generate_subtitle_set(
        num_entries=num_entries,
        format_type="decimal",
        offset=offset,
        include_challenges=include_challenges
    )
    
    # Create schemas
    schema1 = create_schema(include_speaker=True)
    schema2 = create_schema(include_speaker=True)
    
    # Write data to files
    with open(os.path.join(output_dir, "set1-subtitles.json"), "w", encoding="utf-8") as f:
        json.dump(set1, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(output_dir, "set2-subtitles.json"), "w", encoding="utf-8") as f:
        json.dump(set2, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(output_dir, "set1-schema.json"), "w", encoding="utf-8") as f:
        json.dump(schema1, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(output_dir, "set2-schema.json"), "w", encoding="utf-8") as f:
        json.dump(schema2, f, ensure_ascii=False, indent=2)
    
    print(f"Generated test data in {output_dir}")
    print(f"- Set 1: {len(set1)} entries")
    print(f"- Set 2: {len(set2)} entries with {offset}s offset")

def generate_challenge_sets(output_dir, base_entries=30):
    """Generate multiple challenge sets with different characteristics."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Challenge 1: Basic alignment with consistent offset
    challenge_dir = os.path.join(output_dir, "challenge1_basic")
    os.makedirs(challenge_dir, exist_ok=True)
    generate_test_data(
        challenge_dir, 
        num_entries=base_entries, 
        offset=3.5, 
        include_challenges=False
    )
    
    # Challenge 2: Alignment with encoding issues
    challenge_dir = os.path.join(output_dir, "challenge2_encoding")
    os.makedirs(challenge_dir, exist_ok=True)
    generate_test_data(
        challenge_dir, 
        num_entries=base_entries, 
        offset=4.2, 
        include_challenges=True
    )
    
    # Challenge 3: Alignment with varying offset
    challenge_dir = os.path.join(output_dir, "challenge3_varying_offset")
    os.makedirs(challenge_dir, exist_ok=True)
    
    # Generate set 1
    set1 = generate_subtitle_set(
        num_entries=base_entries,
        format_type="standard",
        include_challenges=True
    )
    
    # Generate set 2 with varying offset
    set2 = []
    current_time = random.uniform(0, 10)
    base_offset = 5.0
    current_offset = base_offset
    
    for i in range(base_entries):
        # Gradually change the offset
        if i > 0 and i % 5 == 0:
            current_offset += random.uniform(-0.5, 0.5)
        
        # Determine duration for this subtitle
        duration = random.uniform(1.0, 3.0)
        
        # Generate the entry with current offset
        entry, end_time = generate_subtitle_entry(
            i, current_time, current_time + duration, 
            current_offset, "decimal", True
        )
        set2.append(entry)
        
        # Update current time for next entry
        current_time = end_time - current_offset + random.uniform(0.2, 0.8)
    
    # Create schemas
    schema1 = create_schema(include_speaker=True)
    schema2 = create_schema(include_speaker=True)
    
    # Write data to files
    with open(os.path.join(challenge_dir, "set1-subtitles.json"), "w", encoding="utf-8") as f:
        json.dump(set1, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(challenge_dir, "set2-subtitles.json"), "w", encoding="utf-8") as f:
        json.dump(set2, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(challenge_dir, "set1-schema.json"), "w", encoding="utf-8") as f:
        json.dump(schema1, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(challenge_dir, "set2-schema.json"), "w", encoding="utf-8") as f:
        json.dump(schema2, f, ensure_ascii=False, indent=2)
    
    # Challenge 4: Alignment with missing data
    challenge_dir = os.path.join(output_dir, "challenge4_missing_data")
    os.makedirs(challenge_dir, exist_ok=True)
    
    # Generate set 1
    set1 = generate_subtitle_set(
        num_entries=base_entries,
        format_type="standard",
        include_challenges=True
    )
    
    # Generate set 2 with missing entries
    set2 = generate_subtitle_set(
        num_entries=base_entries - 5,  # Fewer entries
        format_type="decimal",
        offset=2.8,
        include_challenges=True
    )
    
    # Randomly remove some fields
    for entry in set2:
        if random.random() < 0.2:
            if "speaker" in entry:
                del entry["speaker"]
        if random.random() < 0.1:
            if "end" in entry:
                del entry["end"]
        if random.random() < 0.15:
            entry["phonemes"] = entry["phonemes"][:len(entry["phonemes"])//2]
    
    # Create schemas
    schema1 = create_schema(include_speaker=True)
    schema2 = create_schema(include_speaker=True)
    
    # Write data to files
    with open(os.path.join(challenge_dir, "set1-subtitles.json"), "w", encoding="utf-8") as f:
        json.dump(set1, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(challenge_dir, "set2-subtitles.json"), "w", encoding="utf-8") as f:
        json.dump(set2, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(challenge_dir, "set1-schema.json"), "w", encoding="utf-8") as f:
        json.dump(schema1, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(challenge_dir, "set2-schema.json"), "w", encoding="utf-8") as f:
        json.dump(schema2, f, ensure_ascii=False, indent=2)
    
    print(f"Generated challenge sets in {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Generate test data for subtitle alignment competition")
    parser.add_argument("--output", default="data", help="Output directory for test data")
    parser.add_argument("--entries", type=int, default=50, help="Number of subtitle entries to generate")
    parser.add_argument("--offset", type=float, default=5.0, help="Time offset for second subtitle set")
    parser.add_argument("--challenges", action="store_true", help="Include data challenges")
    parser.add_argument("--challenge-sets", action="store_true", help="Generate multiple challenge sets")
    
    args = parser.parse_args()
    
    if args.challenge_sets:
        generate_challenge_sets(args.output, args.entries)
    else:
        generate_test_data(args.output, args.entries, args.offset, args.challenges)

if __name__ == "__main__":
    main()

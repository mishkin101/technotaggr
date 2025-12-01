#!/usr/bin/env python3
"""
Download Essentia models for the technotaggr project.
Downloads classification heads and feature extractors with specific model types.
"""
import os
import sys
import subprocess
from pathlib import Path


BASE_URL = "https://essentia.upf.edu/models"
MODELS_DIR = Path(__file__).parent / "models"

# Classification heads to download
CLASSIFIERS = [
    "fs_loop_ds",
    "mood_aggressive",
    "mood_happy",
    "mood_relaxed",
    "mood_sad",
    "nsynth_instrument",
    "nsynth_reverb",
    "tonal_atonal",
]

# Model types we want for each classifier
MODEL_TYPES = [
    "msd-musicnn-1",
    "discogs-effnet-1",
]

# Feature extractors to download
FEATURE_EXTRACTORS = [
    {
        "name": "musicnn",
        "subdir": "msd-musicnn-1",
        "files": ["msd-musicnn-1.json", "msd-musicnn-1.pb"],
    },
    {
        "name": "discogs-effnet",
        "subdir": "discogs-effnet-bs64-1",
        "files": ["discogs-effnet-bs64-1.json", "discogs-effnet-bs64-1.pb"],
    },
]


def download_file(url, dest_path):
    """
    Download a file from URL to destination path using curl.
    
    Args:
        url: Source URL
        dest_path: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    if dest_path.exists():
        print(f"  ✓ Already exists: {dest_path.name}")
        return True
    
    try:
        print(f"  ⬇ Downloading: {dest_path.name}")
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use curl for downloading (skip SSL verification with -k for compatibility)
        result = subprocess.run(
            ["curl", "-k", "-L", "-f", "-o", str(dest_path), url],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"  ✓ Downloaded: {dest_path.name}")
            return True
        else:
            print(f"  ✗ Failed to download {url}")
            if result.stderr:
                # Only show first line of error for cleaner output
                error_line = result.stderr.strip().split('\n')[-1]
                print(f"    Error: {error_line}")
            # Remove partial download
            if dest_path.exists():
                dest_path.unlink()
            return False
            
    except FileNotFoundError:
        print(f"  ✗ curl not found. Please install curl.")
        return False
    except Exception as e:
        print(f"  ✗ Unexpected error downloading {url}: {e}")
        # Remove partial download
        if dest_path.exists():
            dest_path.unlink()
        return False


def download_classification_heads():
    """Download classification head models."""
    print("\n" + "=" * 60)
    print("DOWNLOADING CLASSIFICATION HEADS")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for classifier in CLASSIFIERS:
        print(f"\n📁 {classifier}")
        # Convert classifier name to URL format (replace spaces with underscores)
        classifier_url = classifier.replace(" ", "_").replace("/", "_")
        
        for model_type in MODEL_TYPES:
            # Create filename: e.g., "mood_happy-msd-musicnn-1"
            base_filename = f"{classifier_url}-{model_type}"
            
            # Download .json and .pb files
            for ext in ["json", "pb"]:
                filename = f"{base_filename}.{ext}"
                url = f"{BASE_URL}/classification-heads/{classifier_url}/{filename}"
                dest_path = MODELS_DIR / "classification-heads" / classifier_url / filename
                
                if dest_path.exists():
                    skip_count += 1
                    print(f"  ⊙ Already exists: {filename}")
                elif download_file(url, dest_path):
                    success_count += 1
                else:
                    fail_count += 1
    
    print(f"\n{'─' * 60}")
    print(f"Classification heads: {success_count} downloaded, {skip_count} skipped, {fail_count} failed")
    return success_count, skip_count, fail_count


def download_feature_extractors():
    """Download feature extractor models."""
    print("\n" + "=" * 60)
    print("DOWNLOADING FEATURE EXTRACTORS")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for extractor in FEATURE_EXTRACTORS:
        print(f"\n📁 {extractor['name']}/{extractor['subdir']}")
        
        for filename in extractor["files"]:
            url = f"{BASE_URL}/feature-extractors/{extractor['name']}/{filename}"
            dest_path = MODELS_DIR / "feature-extractors" / extractor["name"] / extractor["subdir"] / filename
            
            if dest_path.exists():
                skip_count += 1
                print(f"  ⊙ Already exists: {filename}")
            elif download_file(url, dest_path):
                success_count += 1
            else:
                fail_count += 1
    
    print(f"\n{'─' * 60}")
    print(f"Feature extractors: {success_count} downloaded, {skip_count} skipped, {fail_count} failed")
    return success_count, skip_count, fail_count


def main():
    """Main download orchestration."""
    print("\n" + "=" * 60)
    print("ESSENTIA MODELS DOWNLOADER")
    print("=" * 60)
    print(f"Target directory: {MODELS_DIR}")
    
    # Download classification heads
    ch_success, ch_skip, ch_fail = download_classification_heads()
    
    # Download feature extractors
    fe_success, fe_skip, fe_fail = download_feature_extractors()
    
    # Summary
    total_success = ch_success + fe_success
    total_skip = ch_skip + fe_skip
    total_fail = ch_fail + fe_fail
    
    print("\n" + "=" * 60)
    print("DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"✓ Successfully downloaded: {total_success}")
    print(f"⊙ Already existed:         {total_skip}")
    print(f"✗ Failed:                  {total_fail}")
    print("=" * 60)
    
    if total_fail > 0:
        print("\n⚠️  Some downloads failed. Please check the URLs and try again.")
        sys.exit(1)
    else:
        print("\n✅ All models are ready!")
        sys.exit(0)


if __name__ == "__main__":
    main()


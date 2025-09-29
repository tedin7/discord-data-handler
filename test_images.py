#!/usr/bin/env python3
"""
Test Image Upload Script
Quick test to upload 5 images to Discord
"""

import subprocess
import sys

def main():
    """Test upload 5 images"""
    print("🧪 Testing Discord Image Upload with 5 files")

    # Run the image uploader in test mode
    cmd = [
        sys.executable,
        "image_uploader.py",
        "--test"
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Image upload test failed: {e}")
    except KeyboardInterrupt:
        print("\n⏹️ Image upload test cancelled by user")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Test Upload Script
Quick test to upload 5 video clips to Discord
"""

import subprocess
import sys

def main():
    """Test upload 5 clips"""
    print("🧪 Testing Discord Upload with 5 clips")

    # Run the uploader in test mode
    cmd = [
        sys.executable,
        "discord_uploader.py",
        "--test",
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Upload test failed: {e}")
    except KeyboardInterrupt:
        print("\n⏹️ Upload test cancelled by user")

if __name__ == "__main__":
    main()
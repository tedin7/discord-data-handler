#!/usr/bin/env python3
"""
Discord Image Uploader
Uploads image files to Discord channels
"""

import os
import json
import requests
import argparse
import time
import hashlib
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class DiscordImageUploader:
    def __init__(self):
        self.token = os.getenv('DISCORD_TOKEN')
        if not self.token:
            raise ValueError("DISCORD_TOKEN not found in .env file")

        self.headers = {
            'Authorization': self.token,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0'
        }

        self.base_url = "https://discord.com/api/v9"
        self.upload_log = Path("image_uploads.json")

    def load_upload_history(self):
        """Load upload history from JSON file"""
        if self.upload_log.exists():
            try:
                with open(self.upload_log, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_upload_history(self, history):
        """Save upload history to JSON file"""
        try:
            with open(self.upload_log, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"⚠️ Warning: Could not save upload history: {e}")

    def get_file_hash(self, file_path):
        """Get MD5 hash of file for tracking"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None

    def extract_channel_id(self, url):
        """Extract channel ID from Discord URL"""
        parts = url.split('/')
        if len(parts) >= 6 and 'channels' in url:
            return parts[-1]
        raise ValueError("Invalid Discord channel URL")

    def upload_file(self, channel_id, file_path, message=""):
        """Upload an image file to a Discord channel"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                print(f"❌ File not found: {file_path}")
                return False

            file_size = file_path.stat().st_size
            discord_limit = 50 * 1024 * 1024  # 50MB Discord limit

            print(f"📁 File size: {file_size / (1024*1024):.2f}MB")

            # Check file size
            if file_size > discord_limit:
                print(f"❌ File too large: {file_size / (1024*1024):.2f}MB (max 50MB)")
                return False

            url = f"{self.base_url}/channels/{channel_id}/messages"

            with open(file_path, 'rb') as f:
                files = {
                    'files[0]': (file_path.name, f, 'application/octet-stream')
                }

                payload = {
                    'content': message,
                    'tts': 'false'
                }

                response = requests.post(url, headers=self.headers, data=payload, files=files)

            if response.status_code == 200:
                print(f"✅ Uploaded: {file_path.name}")
                return True
            else:
                print(f"❌ Failed to upload {file_path.name}: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error uploading {file_path}: {str(e)}")
            return False

    def upload_directory(self, channel_url, directory_path, file_extensions=None, limit=None):
        """Upload all image files from a directory to a Discord channel"""
        try:
            channel_id = self.extract_channel_id(channel_url)
            directory = Path(directory_path)

            if not directory.exists():
                print(f"❌ Directory not found: {directory}")
                return

            # Load upload history
            upload_history = self.load_upload_history()
            channel_key = f"{channel_id}_images"

            if channel_key not in upload_history:
                upload_history[channel_key] = {
                    "channel_url": channel_url,
                    "uploaded_files": {}
                }

            # Default image extensions if none specified
            if file_extensions is None:
                file_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.svg']

            # Find all files with specified extensions
            files_to_upload = []
            for ext in file_extensions:
                files_to_upload.extend(directory.glob(f"*{ext}"))
                files_to_upload.extend(directory.glob(f"*{ext.upper()}"))

            files_to_upload = list(set(files_to_upload))  # Remove duplicates
            files_to_upload.sort()

            # Filter out already uploaded files
            new_files = []
            skipped_count = 0

            for file_path in files_to_upload:
                file_hash = self.get_file_hash(file_path)
                file_key = f"{file_path.name}_{file_hash}"

                if file_key in upload_history[channel_key]["uploaded_files"]:
                    print(f"⏭️  Skipping {file_path.name} (already uploaded)")
                    skipped_count += 1
                else:
                    new_files.append(file_path)

            files_to_upload = new_files

            if limit:
                files_to_upload = files_to_upload[:limit]

            if not files_to_upload:
                if skipped_count > 0:
                    print(f"📁 All {skipped_count} image files already uploaded to this channel")
                else:
                    print(f"❌ No image files found with extensions: {file_extensions}")
                return

            print(f"📁 Found {len(files_to_upload)} new image files to upload")
            if skipped_count > 0:
                print(f"⏭️  Skipped {skipped_count} already uploaded files")
            print(f"📡 Target channel: {channel_url}")

            successful_uploads = 0
            failed_uploads = 0

            for i, file_path in enumerate(files_to_upload, 1):
                print(f"\n[{i}/{len(files_to_upload)}] Uploading {file_path.name}...")

                if self.upload_file(channel_id, file_path):
                    successful_uploads += 1

                    # Record successful upload
                    file_hash = self.get_file_hash(file_path)
                    file_key = f"{file_path.name}_{file_hash}"
                    upload_history[channel_key]["uploaded_files"][file_key] = {
                        "filename": file_path.name,
                        "file_hash": file_hash,
                        "upload_date": datetime.now().isoformat(),
                        "file_size": file_path.stat().st_size
                    }

                    # Save history after each successful upload
                    self.save_upload_history(upload_history)
                else:
                    failed_uploads += 1

                # Rate limiting - Discord allows 5 requests per 5 seconds
                if i < len(files_to_upload):
                    print("⏳ Waiting to avoid rate limits...")
                    time.sleep(2)

            print(f"\n🎉 Upload complete!")
            print(f"✅ Successful: {successful_uploads}")
            print(f"❌ Failed: {failed_uploads}")

        except Exception as e:
            print(f"❌ Error: {str(e)}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Discord Image Uploader')
    parser.add_argument('--channel', type=str,
                       help='Discord channel URL to upload to')
    parser.add_argument('--directory', type=str,
                       help='Directory containing image files to upload')
    parser.add_argument('--limit', type=int, help='Limit number of files to upload')
    parser.add_argument('--extensions', nargs='+',
                       default=['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.svg'],
                       help='Image file extensions to upload')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: upload only 5 files')

    args = parser.parse_args()

    if args.test:
        args.limit = 5
        print("🧪 Test mode: Will upload maximum 5 image files")

    uploader = DiscordImageUploader()

    print("🚀 Starting Discord Image Upload")
    uploader.upload_directory(
        channel_url=args.channel,
        directory_path=args.directory,
        file_extensions=args.extensions,
        limit=args.limit
    )

if __name__ == "__main__":
    main()
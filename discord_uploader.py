#!/usr/bin/env python3
"""
Discord Video Uploader
Uploads video files to Discord channels
"""

import os
import json
import requests
import argparse
import time
import subprocess
import shutil
import hashlib
import random
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class DiscordUploader:
    def __init__(self):
        self.token = os.getenv('DISCORD_TOKEN')
        if not self.token:
            raise ValueError("DISCORD_TOKEN not found in .env file")

        self.headers = {
            'Authorization': self.token,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0'
        }

        self.base_url = "https://discord.com/api/v9"
        self.max_size = 10 * 1024 * 1024  # 10MB target size for compression
        self.upload_log = Path("video_uploads.json")

        # Rate limiting configuration
        self.base_delay = 1.0  # Base delay between requests
        self.max_retries = 5   # Maximum retry attempts for rate limited requests
        self.backoff_factor = 2.0  # Exponential backoff multiplier

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

    def handle_rate_limit(self, response, attempt=0):
        """Handle rate limiting with exponential backoff"""
        if response.status_code == 429:
            try:
                # Discord provides retry-after header in seconds
                retry_after = response.headers.get('retry-after')
                if retry_after:
                    wait_time = float(retry_after)
                    print(f"⏸️  Rate limited! Waiting {wait_time:.1f}s as requested by Discord...")
                else:
                    # Fallback to exponential backoff if no retry-after header
                    wait_time = self.base_delay * (self.backoff_factor ** attempt) + random.uniform(0, 1)
                    print(f"⏸️  Rate limited! Using exponential backoff: {wait_time:.1f}s...")

                # Cap maximum wait time to 5 minutes
                wait_time = min(wait_time, 300)
                time.sleep(wait_time)
                return True

            except Exception as e:
                print(f"⚠️ Error parsing rate limit response: {e}")
                # Default exponential backoff
                wait_time = self.base_delay * (self.backoff_factor ** attempt) + random.uniform(0, 1)
                wait_time = min(wait_time, 300)
                print(f"⏸️  Backing off for {wait_time:.1f}s...")
                time.sleep(wait_time)
                return True

        return False

    def wait_between_requests(self):
        """Standard delay between requests to be respectful to Discord's API"""
        # Random jitter to avoid thundering herd
        delay = self.base_delay + random.uniform(0, 0.5)
        time.sleep(delay)

    def extract_channel_id(self, url):
        """Extract channel ID from Discord URL"""
        parts = url.split('/')
        if len(parts) >= 6 and 'channels' in url:
            return parts[-1]
        raise ValueError("Invalid Discord channel URL")

    def compress_video(self, input_path, target_size_mb=10):
        """Compress video using ffmpeg to target size"""
        try:
            input_path = Path(input_path)
            output_path = input_path.parent / f"compressed_{input_path.name}"

            # Check if ffmpeg is available
            if not shutil.which('ffmpeg'):
                print("❌ ffmpeg not found. Please install ffmpeg to compress large videos.")
                return None

            print(f"🗜️ Compressing {input_path.name} to ~{target_size_mb}MB...")

            # Get video duration first
            duration_cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', str(input_path)
            ]

            try:
                duration = float(subprocess.check_output(duration_cmd).decode().strip())
            except:
                duration = 60  # Default fallback

            # Calculate target bitrate (in kbps)
            # Formula: (target_size_mb * 8 * 1024) / duration_seconds
            target_bitrate = int((target_size_mb * 8 * 1024) / duration * 0.9)  # 90% to account for audio

            # Ensure minimum bitrate
            target_bitrate = max(target_bitrate, 100)

            # ffmpeg command for compression
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-c:v', 'libopenh264',  # Video codec (available on this system)
                '-b:v', f'{target_bitrate}k',  # Video bitrate
                '-c:a', 'aac',  # Audio codec
                '-b:a', '64k',  # Audio bitrate
                '-movflags', '+faststart',  # Web optimization
                '-y',  # Overwrite output file
                str(output_path)
            ]

            # Run ffmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0 and output_path.exists():
                compressed_size = output_path.stat().st_size / (1024 * 1024)
                print(f"✅ Compressed: {compressed_size:.1f}MB")
                return output_path
            else:
                print(f"❌ Compression failed: {result.stderr}")
                return None

        except Exception as e:
            print(f"❌ Error compressing {input_path}: {str(e)}")
            return None

    def upload_file(self, channel_id, file_path, message="", auto_compress=True):
        """Upload a file to a Discord channel with automatic compression and retry logic"""
        try:
            original_path = Path(file_path)
            if not original_path.exists():
                print(f"❌ File not found: {original_path}")
                return False

            current_path = original_path
            file_size = current_path.stat().st_size
            discord_limit = 50 * 1024 * 1024  # 50MB Discord limit

            print(f"📁 File size: {file_size / (1024*1024):.2f}MB")

            # Check if compression is needed
            if file_size > self.max_size and auto_compress:
                # Only compress video files, not GIFs
                if current_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                    compressed_path = self.compress_video(current_path, target_size_mb=9)
                    if compressed_path:
                        current_path = compressed_path
                        file_size = current_path.stat().st_size
                        print(f"📦 Using compressed version: {file_size / (1024*1024):.2f}MB")
                    else:
                        print("⚠️ Compression failed, trying original file...")

            # Final size check
            if file_size > discord_limit:
                print(f"❌ File still too large: {file_size / (1024*1024):.2f}MB (max 50MB)")
                return False

            url = f"{self.base_url}/channels/{channel_id}/messages"

            # Retry loop with exponential backoff
            for attempt in range(self.max_retries + 1):
                try:
                    with open(current_path, 'rb') as f:
                        files = {
                            'files[0]': (current_path.name, f, 'application/octet-stream')
                        }

                        payload = {
                            'content': message,
                            'tts': 'false'
                        }

                        response = requests.post(url, headers=self.headers, data=payload, files=files, timeout=60)

                    # Handle successful upload
                    if response.status_code == 200:
                        print(f"✅ Uploaded: {current_path.name}")
                        # Clean up compressed file if it was created
                        if current_path != original_path and current_path.exists():
                            try:
                                current_path.unlink()
                                print(f"🗑️ Cleaned up temporary compressed file")
                            except:
                                pass
                        return True

                    # Handle rate limiting
                    elif response.status_code == 429:
                        if attempt < self.max_retries:
                            print(f"🔄 Attempt {attempt + 1}/{self.max_retries + 1} - Rate limited")
                            if self.handle_rate_limit(response, attempt):
                                continue
                        else:
                            print(f"❌ Max retries exceeded for {current_path.name} due to rate limiting")
                            break

                    # Handle other errors
                    else:
                        if attempt < self.max_retries and response.status_code >= 500:
                            # Retry server errors
                            wait_time = self.base_delay * (self.backoff_factor ** attempt)
                            print(f"🔄 Server error {response.status_code}, retrying in {wait_time:.1f}s...")
                            time.sleep(wait_time)
                            continue
                        else:
                            print(f"❌ Failed to upload {current_path.name}: {response.status_code}")
                            if response.text:
                                print(f"Response: {response.text[:200]}...")
                            break

                except requests.exceptions.Timeout:
                    if attempt < self.max_retries:
                        wait_time = self.base_delay * (self.backoff_factor ** attempt)
                        print(f"⏰ Upload timeout, retrying in {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"❌ Upload timeout for {current_path.name}")
                        break

                except requests.exceptions.RequestException as e:
                    if attempt < self.max_retries:
                        wait_time = self.base_delay * (self.backoff_factor ** attempt)
                        print(f"🌐 Network error, retrying in {wait_time:.1f}s... ({str(e)[:50]})")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"❌ Network error for {current_path.name}: {str(e)}")
                        break

            # Clean up compressed file if upload failed
            if current_path != original_path and current_path.exists():
                try:
                    current_path.unlink()
                    print(f"🗑️ Cleaned up temporary compressed file")
                except:
                    pass

            return False

        except Exception as e:
            print(f"❌ Error uploading {file_path}: {str(e)}")
            return False

    def upload_directory(self, channel_url, directory_path, file_extensions=None, limit=None, message_template=""):
        """Upload all files from a directory to a Discord channel"""
        try:
            channel_id = self.extract_channel_id(channel_url)
            directory = Path(directory_path)

            if not directory.exists():
                print(f"❌ Directory not found: {directory}")
                return

            # Load upload history
            upload_history = self.load_upload_history()
            channel_key = f"{channel_id}_videos"

            if channel_key not in upload_history:
                upload_history[channel_key] = {
                    "channel_url": channel_url,
                    "uploaded_files": {}
                }

            # Default video extensions if none specified
            if file_extensions is None:
                file_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.gif']

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
                    print(f"📁 All {skipped_count} files already uploaded to this channel")
                else:
                    print(f"❌ No files found with extensions: {file_extensions}")
                return

            print(f"📁 Found {len(files_to_upload)} new files to upload")
            if skipped_count > 0:
                print(f"⏭️  Skipped {skipped_count} already uploaded files")
            print(f"📡 Target channel: {channel_url}")

            successful_uploads = 0
            failed_uploads = 0
            start_time = time.time()

            for i, file_path in enumerate(files_to_upload, 1):
                elapsed_time = time.time() - start_time
                if i > 1:
                    avg_time_per_file = elapsed_time / (i - 1)
                    remaining_files = len(files_to_upload) - i + 1
                    eta_seconds = avg_time_per_file * remaining_files
                    eta_str = f" (ETA: {int(eta_seconds//60)}m {int(eta_seconds%60)}s)"
                else:
                    eta_str = ""

                print(f"\n[{i}/{len(files_to_upload)}] Uploading {file_path.name}...{eta_str}")

                # Create message with template
                message = message_template.format(
                    filename=file_path.name,
                    index=i,
                    total=len(files_to_upload)
                ) if message_template else ""

                if self.upload_file(channel_id, file_path, message):
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

                # Smart rate limiting between uploads
                if i < len(files_to_upload):
                    print("⏳ Waiting between uploads...")
                    self.wait_between_requests()

            total_time = time.time() - start_time
            print(f"\n🎉 Upload complete! Total time: {int(total_time//60)}m {int(total_time%60)}s")
            print(f"✅ Successful: {successful_uploads}")
            print(f"❌ Failed: {failed_uploads}")
            if successful_uploads > 0:
                print(f"⏱️  Average time per successful upload: {total_time/successful_uploads:.1f}s")

        except Exception as e:
            print(f"❌ Error: {str(e)}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Discord Video Uploader')
    parser.add_argument('--channel', type=str,
                       help='Discord channel URL to upload to')
    parser.add_argument('--directory', type=str,
                       help='Directory containing files to upload')
    parser.add_argument('--limit', type=int, help='Limit number of files to upload')
    parser.add_argument('--extensions', nargs='+',
                       default=['.mp4', '.avi', '.mov', '.mkv', '.webm', '.gif'],
                       help='File extensions to upload')
    parser.add_argument('--message', type=str, default="",
                       help='Message template (use {filename}, {index}, {total} for variables)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: upload only 5 files')
    parser.add_argument('--no-compress', action='store_true',
                       help='Disable automatic video compression')
    parser.add_argument('--max-size', type=int, default=10,
                       help='Target compression size in MB (default: 10)')
    parser.add_argument('--max-retries', type=int, default=5,
                       help='Maximum retry attempts for failed uploads (default: 5)')
    parser.add_argument('--base-delay', type=float, default=1.0,
                       help='Base delay between requests in seconds (default: 1.0)')
    parser.add_argument('--backoff-factor', type=float, default=2.0,
                       help='Exponential backoff multiplier (default: 2.0)')

    args = parser.parse_args()

    if args.test:
        args.limit = 5
        print("🧪 Test mode: Will upload maximum 5 files")

    uploader = DiscordUploader()
    uploader.max_size = args.max_size * 1024 * 1024  # Convert MB to bytes
    uploader.max_retries = args.max_retries
    uploader.base_delay = args.base_delay
    uploader.backoff_factor = args.backoff_factor

    print("🚀 Starting Discord Video Upload")
    if not args.no_compress:
        print(f"🗜️ Auto-compression enabled (target: {args.max_size}MB)")

    uploader.upload_directory(
        channel_url=args.channel,
        directory_path=args.directory,
        file_extensions=args.extensions,
        limit=args.limit,
        message_template=args.message
    )

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Discord Channel Downloader
Downloads messages and attachments from Discord channels
"""

import os
import json
import requests
import time
import argparse
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

class DiscordDownloader:
    def __init__(self):
        self.token = os.getenv('DISCORD_TOKEN')
        if not self.token:
            raise ValueError("DISCORD_TOKEN not found in .env file")

        self.headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0'
        }

        self.base_url = "https://discord.com/api/v9"

    def extract_channel_id(self, url):
        """Extract channel ID from Discord URL"""
        # URL format: https://discord.com/channels/guild_id/channel_id
        parts = url.split('/')
        if len(parts) >= 6 and 'channels' in url:
            return parts[-1]  # Last part is channel_id
        raise ValueError("Invalid Discord channel URL")

    def get_messages(self, channel_id, limit=None):
        """Fetch all messages from a channel"""
        messages = []
        last_message_id = None

        print(f"Downloading messages from channel {channel_id}...")

        while True:
            url = f"{self.base_url}/channels/{channel_id}/messages?limit=100"
            if last_message_id:
                url += f"&before={last_message_id}"

            response = requests.get(url, headers=self.headers)

            if response.status_code != 200:
                print(f"Error fetching messages: {response.status_code} - {response.text}")
                break

            batch = response.json()
            if not batch:
                break

            messages.extend(batch)
            last_message_id = batch[-1]['id']

            print(f"Downloaded {len(messages)} messages...")

            if limit and len(messages) >= limit:
                messages = messages[:limit]
                break

            # Rate limiting
            time.sleep(0.5)

        print(f"Total messages downloaded: {len(messages)}")
        return messages

    def download_attachment(self, attachment, download_dir):
        """Download a single attachment"""
        try:
            url = attachment['url']
            filename = attachment['filename']

            # Create safe filename
            safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            filepath = download_dir / safe_filename

            # Avoid overwriting files
            counter = 1
            while filepath.exists():
                name, ext = os.path.splitext(safe_filename)
                filepath = download_dir / f"{name}_{counter}{ext}"
                counter += 1

            response = requests.get(url)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded: {filepath.name}")
                return str(filepath)
            else:
                print(f"Failed to download {filename}: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error downloading {attachment.get('filename', 'unknown')}: {str(e)}")
            return None

    def download_embedded_images(self, message, download_dir):
        """Download images from embeds and message content"""
        downloaded_images = []

        # Check embeds for images
        if message.get('embeds'):
            for embed in message['embeds']:
                # Image in embed
                if embed.get('image', {}).get('url'):
                    url = embed['image']['url']
                    downloaded_path = self.download_image_from_url(url, download_dir)
                    if downloaded_path:
                        downloaded_images.append(downloaded_path)

                # Thumbnail in embed
                if embed.get('thumbnail', {}).get('url'):
                    url = embed['thumbnail']['url']
                    downloaded_path = self.download_image_from_url(url, download_dir)
                    if downloaded_path:
                        downloaded_images.append(downloaded_path)

        # Check message content for image URLs
        if message.get('content'):
            # Find image URLs in message content
            image_urls = re.findall(r'https?://[^\s]+\.(?:png|jpg|jpeg|gif|webp|bmp|svg)', message['content'], re.IGNORECASE)
            for url in image_urls:
                downloaded_path = self.download_image_from_url(url, download_dir)
                if downloaded_path:
                    downloaded_images.append(downloaded_path)

        return downloaded_images

    def download_image_from_url(self, url, download_dir):
        """Download an image from a URL"""
        try:
            # Extract filename from URL
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)

            if not filename or '.' not in filename:
                # Generate filename from URL
                filename = f"image_{hash(url) % 10000}.png"

            # Create safe filename
            safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            filepath = download_dir / safe_filename

            # Avoid overwriting files
            counter = 1
            while filepath.exists():
                name, ext = os.path.splitext(safe_filename)
                filepath = download_dir / f"{name}_{counter}{ext}"
                counter += 1

            response = requests.get(url)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded image: {filepath.name}")
                return str(filepath)
            else:
                print(f"Failed to download image from {url}: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error downloading image from {url}: {str(e)}")
            return None

    def get_guild_channels(self, guild_id):
        """Fetch all channels from a guild/server"""
        url = f"{self.base_url}/guilds/{guild_id}/channels"

        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print(f"Error fetching guild channels: {response.status_code} - {response.text}")
            return []

        channels = response.json()
        text_channels = [ch for ch in channels if ch['type'] in [0, 5]]  # Text and announcement channels

        print(f"Found {len(text_channels)} text channels in guild {guild_id}")
        return text_channels

    def download_guild(self, guild_id, output_dir="downloads", limit=None, attachments_only=False, text_only=False):
        """Download all messages from all channels in a guild/server"""
        try:
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)

            # Create subdirectory for this guild
            guild_dir = output_path / f"guild_{guild_id}"
            guild_dir.mkdir(exist_ok=True)

            # Get all channels in the guild
            channels = self.get_guild_channels(guild_id)

            if not channels:
                print("No accessible channels found in this guild")
                return None

            print(f"\n🚀 Starting download of {len(channels)} channels from guild {guild_id}")

            total_messages = 0
            total_attachments = 0
            total_images = 0
            successful_channels = 0

            for i, channel in enumerate(channels, 1):
                channel_id = channel['id']
                channel_name = channel['name']

                print(f"\n📁 [{i}/{len(channels)}] Downloading channel: #{channel_name} ({channel_id})")

                try:
                    # Create channel subdirectory
                    channel_dir = guild_dir / f"channel_{channel_name}_{channel_id}"
                    channel_dir.mkdir(exist_ok=True)

                    attachments_dir = channel_dir / "attachments"
                    attachments_dir.mkdir(exist_ok=True)

                    # Get messages from this channel
                    messages = self.get_messages(channel_id, limit)

                    if not messages:
                        print(f"   ⚠️ No messages found in #{channel_name}")
                        continue

                    # Process messages and download attachments
                    processed_messages = []
                    channel_attachments = 0
                    channel_images = 0

                    for msg in messages:
                        has_media = False

                        processed_msg = {
                            'id': msg['id'],
                            'timestamp': msg['timestamp'],
                            'author': {
                                'id': msg['author']['id'],
                                'username': msg['author']['username'],
                                'display_name': msg['author'].get('global_name', msg['author']['username'])
                            },
                            'content': msg['content'],
                            'attachments': [],
                            'images': [],
                            'embeds': msg.get('embeds', []),
                            'reactions': msg.get('reactions', [])
                        }

                        # Download attachments (skip if text_only mode)
                        if msg.get('attachments') and not text_only:
                            for attachment in msg['attachments']:
                                downloaded_path = self.download_attachment(attachment, attachments_dir)
                                if downloaded_path:
                                    has_media = True
                                    channel_attachments += 1
                                    processed_msg['attachments'].append({
                                        'filename': attachment['filename'],
                                        'url': attachment['url'],
                                        'local_path': downloaded_path,
                                        'size': attachment.get('size', 0)
                                    })
                        elif msg.get('attachments') and text_only:
                            # In text_only mode, still record attachment metadata without downloading
                            for attachment in msg['attachments']:
                                processed_msg['attachments'].append({
                                    'filename': attachment['filename'],
                                    'url': attachment['url'],
                                    'local_path': None,
                                    'size': attachment.get('size', 0)
                                })

                        # Download embedded images (skip if text_only mode)
                        if not text_only:
                            downloaded_images = self.download_embedded_images(msg, attachments_dir)
                            if downloaded_images:
                                has_media = True
                                channel_images += len(downloaded_images)
                                processed_msg['images'] = downloaded_images

                        # Only include message if it has media when in attachments_only mode
                        if not attachments_only or has_media:
                            processed_messages.append(processed_msg)

                    if not attachments_only:
                        # Save messages to JSON
                        messages_file = channel_dir / "messages.json"
                        with open(messages_file, 'w', encoding='utf-8') as f:
                            json.dump(processed_messages, f, indent=2, ensure_ascii=False)

                        # Create readable text file
                        text_file = channel_dir / "messages.txt"
                        with open(text_file, 'w', encoding='utf-8') as f:
                            f.write(f"Discord Channel Export\n")
                            f.write(f"Guild ID: {guild_id}\n")
                            f.write(f"Channel: #{channel_name} ({channel_id})\n")
                            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write(f"Total Messages: {len(processed_messages)}\n")
                            f.write("=" * 50 + "\n\n")

                            for msg in reversed(processed_messages):
                                timestamp = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                                f.write(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {msg['author']['display_name']}: {msg['content']}\n")

                                if msg['attachments']:
                                    for att in msg['attachments']:
                                        f.write(f"  📎 Attachment: {att['filename']}\n")

                                if msg['images']:
                                    f.write(f"  🖼️ {len(msg['images'])} image(s) downloaded\n")

                                if msg['embeds']:
                                    f.write(f"  🔗 {len(msg['embeds'])} embed(s)\n")

                                f.write("\n")

                    total_messages += len(processed_messages)
                    total_attachments += channel_attachments
                    total_images += channel_images
                    successful_channels += 1

                    print(f"   ✅ #{channel_name}: {len(processed_messages)} messages, {channel_attachments} attachments, {channel_images} images")

                except Exception as e:
                    print(f"   ❌ Error downloading #{channel_name}: {str(e)}")
                    continue

            # Create guild summary
            summary_file = guild_dir / "guild_summary.txt"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"Discord Guild Export Summary\n")
                f.write(f"Guild ID: {guild_id}\n")
                f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Successful Channels: {successful_channels}/{len(channels)}\n")
                f.write(f"Total Messages: {total_messages}\n")
                f.write(f"Total Attachments: {total_attachments}\n")
                f.write(f"Total Images: {total_images}\n")
                f.write("=" * 50 + "\n\n")

                f.write("Downloaded Channels:\n")
                for channel in channels:
                    channel_dir_path = guild_dir / f"channel_{channel['name']}_{channel['id']}"
                    if channel_dir_path.exists():
                        f.write(f"✅ #{channel['name']} ({channel['id']})\n")
                    else:
                        f.write(f"❌ #{channel['name']} ({channel['id']}) - Failed\n")

            print(f"\n✅ Guild download complete!")
            print(f"📁 Output directory: {guild_dir}")
            print(f"📊 Successfully downloaded: {successful_channels}/{len(channels)} channels")
            print(f"📄 Total messages: {total_messages}")
            print(f"📎 Total attachments: {total_attachments}")
            print(f"🖼️ Total images: {total_images}")
            print(f"📋 Summary saved to: {summary_file}")

            return guild_dir

        except Exception as e:
            print(f"❌ Guild download error: {str(e)}")
            return None

    def download_channel(self, channel_url, output_dir="downloads", limit=None, attachments_only=False, text_only=False):
        """Download entire channel content"""
        try:
            channel_id = self.extract_channel_id(channel_url)

            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)

            # Create subdirectory for this channel
            channel_dir = output_path / f"channel_{channel_id}"
            channel_dir.mkdir(exist_ok=True)

            attachments_dir = channel_dir / "attachments"
            attachments_dir.mkdir(exist_ok=True)

            # Get messages
            messages = self.get_messages(channel_id, limit)

            # Process messages and download attachments
            processed_messages = []

            total_attachments = 0
            total_images = 0

            for msg in messages:
                has_media = False

                processed_msg = {
                    'id': msg['id'],
                    'timestamp': msg['timestamp'],
                    'author': {
                        'id': msg['author']['id'],
                        'username': msg['author']['username'],
                        'display_name': msg['author'].get('global_name', msg['author']['username'])
                    },
                    'content': msg['content'],
                    'attachments': [],
                    'images': [],
                    'embeds': msg.get('embeds', []),
                    'reactions': msg.get('reactions', [])
                }

                # Download attachments (skip if text_only mode)
                if msg.get('attachments') and not text_only:
                    for attachment in msg['attachments']:
                        downloaded_path = self.download_attachment(attachment, attachments_dir)
                        if downloaded_path:
                            has_media = True
                            total_attachments += 1
                            processed_msg['attachments'].append({
                                'filename': attachment['filename'],
                                'url': attachment['url'],
                                'local_path': downloaded_path,
                                'size': attachment.get('size', 0)
                            })
                elif msg.get('attachments') and text_only:
                    # In text_only mode, still record attachment metadata without downloading
                    for attachment in msg['attachments']:
                        processed_msg['attachments'].append({
                            'filename': attachment['filename'],
                            'url': attachment['url'],
                            'local_path': None,
                            'size': attachment.get('size', 0)
                        })

                # Download embedded images and images from message content (skip if text_only mode)
                if not text_only:
                    downloaded_images = self.download_embedded_images(msg, attachments_dir)
                    if downloaded_images:
                        has_media = True
                        total_images += len(downloaded_images)
                        processed_msg['images'] = downloaded_images

                # Only include message if it has media when in attachments_only mode
                if not attachments_only or has_media:
                    processed_messages.append(processed_msg)

            if not attachments_only:
                # Save messages to JSON
                messages_file = channel_dir / "messages.json"
                with open(messages_file, 'w', encoding='utf-8') as f:
                    json.dump(processed_messages, f, indent=2, ensure_ascii=False)

                # Create readable text file
                text_file = channel_dir / "messages.txt"
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(f"Discord Channel Export\n")
                    f.write(f"Channel ID: {channel_id}\n")
                    f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Total Messages: {len(processed_messages)}\n")
                    f.write("=" * 50 + "\n\n")

                    for msg in reversed(processed_messages):  # Reverse for chronological order
                        timestamp = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                        f.write(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {msg['author']['display_name']}: {msg['content']}\n")

                        if msg['attachments']:
                            for att in msg['attachments']:
                                f.write(f"  📎 Attachment: {att['filename']}\n")

                        if msg['images']:
                            f.write(f"  🖼️ {len(msg['images'])} image(s) downloaded\n")

                        if msg['embeds']:
                            f.write(f"  🔗 {len(msg['embeds'])} embed(s)\n")

                        f.write("\n")

            print(f"\n✅ Download complete!")
            print(f"📁 Output directory: {channel_dir}")
            print(f"📎 Attachments in: {attachments_dir}")
            print(f"📎 Total attachments downloaded: {total_attachments}")
            print(f"🖼️ Total images downloaded: {total_images}")

            if not attachments_only:
                print(f"📄 Messages saved to: {channel_dir / 'messages.json'}")
                print(f"📄 Readable format: {channel_dir / 'messages.txt'}")
            else:
                print(f"ℹ️ Attachments-only mode: Only downloaded media files")

            return channel_dir

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Discord Channel/Guild Downloader')
    parser.add_argument('--url', type=str,
                       help='Discord channel URL to download')
    parser.add_argument('--guild-id', type=str,
                       help='Discord guild/server ID to download all channels from')
    parser.add_argument('--limit', type=int, help='Limit number of messages to download')
    parser.add_argument('--attachments-only', action='store_true',
                       help='Only download attachments and images, skip message text files')
    parser.add_argument('--text-only', action='store_true',
                       help='Only save text messages, skip downloading attachments and images')
    parser.add_argument('--output', type=str, default='downloads',
                       help='Output directory (default: downloads)')

    args = parser.parse_args()

    downloader = DiscordDownloader()

    if args.guild_id:
        print("🚀 Starting Discord Guild Download")
        print(f"📡 Guild ID: {args.guild_id}")
        if args.attachments_only:
            print("📎 Mode: Attachments and images only")
        if args.text_only:
            print("📝 Mode: Text messages only (no media downloads)")
        if args.limit:
            print(f"📊 Limit: {args.limit} messages per channel")

        result = downloader.download_guild(
            args.guild_id,
            output_dir=args.output,
            limit=args.limit,
            attachments_only=args.attachments_only,
            text_only=args.text_only
        )

        if result:
            print(f"\n🎉 Success! Files saved to: {result}")
        else:
            print("\n❌ Download failed!")
    else:
        print("🚀 Starting Discord Channel Download")
        print(f"📡 Channel URL: {args.url}")
        if args.attachments_only:
            print("📎 Mode: Attachments and images only")
        if args.text_only:
            print("📝 Mode: Text messages only (no media downloads)")
        if args.limit:
            print(f"📊 Limit: {args.limit} messages")

        result = downloader.download_channel(
            args.url,
            output_dir=args.output,
            limit=args.limit,
            attachments_only=args.attachments_only,
            text_only=args.text_only
        )

        if result:
            print(f"\n🎉 Success! Files saved to: {result}")
        else:
            print("\n❌ Download failed!")

if __name__ == "__main__":
    main()
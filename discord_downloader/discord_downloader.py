#!/usr/bin/env python3
"""
Discord Downloader - A Python wrapper for DiscordChatExporter CLI
Scrapes Discord chat history and media files to HTML format.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DiscordDownloader:
    """Main class for handling Discord chat exports."""

    def __init__(self, config_path: str = "config/discord_config.json"):
        self.config_path = Path(config_path)
        self.discord_exporter_path = Path("bin/discordchatexporter/DiscordChatExporter.Cli.dll")
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from JSON file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {
            "token": "",
            "default_output_dir": "output",
            "default_format": "Html",
            "download_media": True
        }

    def _save_config(self) -> None:
        """Save current configuration to JSON file."""
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def set_token(self, token: str) -> None:
        """Set Discord authentication token."""
        self.config["token"] = token
        self._save_config()
        print(f"✅ Token saved to {self.config_path}")

    def export_channel(self,
                      channel_id: str,
                      output_path: Optional[str] = None,
                      after_date: Optional[str] = None,
                      before_date: Optional[str] = None,
                      message_limit: Optional[int] = None,
                      format_type: str = "Html") -> bool:
        """
        Export a Discord channel to HTML with media.

        Args:
            channel_id: Discord channel ID
            output_path: Custom output path (optional)
            after_date: Start date in YYYY-MM-DD format (optional)
            before_date: End date in YYYY-MM-DD format (optional)
            message_limit: Maximum number of messages to export (optional)
            format_type: Export format (Html, Json, Csv, Txt)

        Returns:
            bool: True if export successful
        """
        if not self.config.get("token"):
            print("❌ No Discord token configured. Run: python discord_downloader.py set-token")
            return False

        if not self.discord_exporter_path.exists():
            print("❌ DiscordChatExporter not found. Run installation script first:")
            print("   bash scripts/install_dependencies.sh")
            return False

        # Prepare output path
        if output_path is None:
            output_dir = Path(self.config["default_output_dir"])
            output_dir.mkdir(exist_ok=True)
            output_file = f"channel_{channel_id}_{Path.cwd().name}.html"
            output_path = str(output_dir / output_file)
        else:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Build command
        cmd = [
            "dotnet", str(self.discord_exporter_path),
            "export",
            "-t", self.config["token"],
            "-c", channel_id,
            "-f", format_type,
            "-o", output_path
        ]

        # Add optional flags
        if self.config.get("download_media", True):
            cmd.append("--media")

        if after_date:
            cmd.extend(["--after", after_date])

        if before_date:
            cmd.extend(["--before", before_date])

        if message_limit:
            cmd.extend(["--limit", str(message_limit)])

        print(f"🚀 Exporting channel {channel_id}...")
        print(f"📄 Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=Path.cwd(),
                check=True,
                capture_output=True,
                text=True
            )
            print("✅ Export completed successfully!")
            print(f"📁 Output saved to: {output_path}")

            # Check if media folder was created
            output_dir = Path(output_path).parent
            media_dir = output_dir / "media"
            if media_dir.exists():
                media_count = len(list(media_dir.rglob("*")))
                print(f"📎 Downloaded {media_count} media files")

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Export failed: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
            return False
        except FileNotFoundError:
            print("❌ .NET runtime not found. Please install .NET 9.0:")
            print("   sudo dnf install dotnet-runtime-9.0")
            return False

    def export_guild(self,
                    guild_id: str,
                    output_dir: Optional[str] = None,
                    format_type: str = "Html") -> bool:
        """
        Export all channels from a Discord guild (server).

        Args:
            guild_id: Discord guild/server ID
            output_dir: Custom output directory (optional)
            format_type: Export format (Html, Json, Csv, Txt)

        Returns:
            bool: True if export successful
        """
        if not self.config.get("token"):
            print("❌ No Discord token configured. Run: python discord_downloader.py set-token")
            return False

        if not self.discord_exporter_path.exists():
            print("❌ DiscordChatExporter not found. Run installation script first:")
            print("   bash scripts/install_dependencies.sh")
            return False

        # Prepare output directory
        if output_dir is None:
            output_dir = f"{self.config['default_output_dir']}/guild_{guild_id}"
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Build command
        cmd = [
            "dotnet", str(self.discord_exporter_path),
            "exportguild",
            "-t", self.config["token"],
            "-g", guild_id,
            "-f", format_type,
            "-o", output_dir
        ]

        if self.config.get("download_media", True):
            cmd.append("--media")

        print(f"🚀 Exporting entire guild {guild_id}...")
        print(f"📄 Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=Path.cwd(),
                check=True,
                capture_output=True,
                text=True
            )
            print("✅ Guild export completed successfully!")
            print(f"📁 Output saved to: {output_dir}")

            # Count exported files
            exported_files = len(list(Path(output_dir).glob("*.html")))
            print(f"📊 Exported {exported_files} channels")

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Export failed: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
            return False
        except FileNotFoundError:
            print("❌ .NET runtime not found. Please install .NET 9.0:")
            print("   sudo dnf install dotnet-runtime-9.0")
            return False

    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """
        Get information about a Discord channel.

        Args:
            channel_id: Discord channel ID

        Returns:
            dict: Channel information or None if failed
        """
        # This would require additional Discord API calls
        # For now, we'll just return basic info
        return {
            "id": channel_id,
            "type": "unknown"
        }

    def list_channels(self, guild_id: str) -> List[Dict]:
        """
        List all channels in a guild.

        Args:
            guild_id: Discord guild/server ID

        Returns:
            list: List of channel information
        """
        # This would require Discord API calls to list channels
        # For now, return placeholder
        return []


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Discord Downloader - Export Discord chats with media",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s set-token YOUR_TOKEN_HERE
  %(prog)s export-channel 123456789012345678 --output ./my_chat.html
  %(prog)s export-guild 987654321098765432 --output ./server_export/
  %(prog)s install-deps

Note: Using user tokens violates Discord's TOS. Use bot tokens for servers when possible.
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Set token command
    subparsers.add_parser('set-token', help='Configure Discord authentication token')

    # Export channel command
    export_parser = subparsers.add_parser('export-channel', help='Export a single channel')
    export_parser.add_argument('channel_id', help='Discord channel ID')
    export_parser.add_argument('--output', '-o', help='Output file path')
    export_parser.add_argument('--after', help='Start date (YYYY-MM-DD)')
    export_parser.add_argument('--before', help='End date (YYYY-MM-DD)')
    export_parser.add_argument('--limit', type=int, help='Maximum messages to export')
    export_parser.add_argument('--format', choices=['Html', 'Json', 'Csv', 'Txt'],
                              default='Html', help='Export format (default: Html)')
    export_parser.add_argument('--no-media', action='store_true',
                              help='Skip downloading media files')

    # Export guild command
    guild_parser = subparsers.add_parser('export-guild', help='Export all channels in a guild')
    guild_parser.add_argument('guild_id', help='Discord guild/server ID')
    guild_parser.add_argument('--output', '-o', help='Output directory path')
    guild_parser.add_argument('--format', choices=['Html', 'Json', 'Csv', 'Txt'],
                             default='Html', help='Export format (default: Html)')
    guild_parser.add_argument('--no-media', action='store_true',
                             help='Skip downloading media files')

    # Install dependencies command
    subparsers.add_parser('install-deps', help='Install required dependencies')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    downloader = DiscordDownloader()

    if args.command == 'install-deps':
        print("🔧 Installing dependencies...")
        script_path = Path(__file__).parent / "scripts" / "install_dependencies.sh"
        if script_path.exists():
            os.execv('/bin/bash', ['bash', str(script_path)])
        else:
            print("❌ Installation script not found!")
            return

    elif args.command == 'set-token':
        token = input("Enter your Discord token: ").strip()
        if token:
            downloader.set_token(token)
        else:
            print("❌ Token cannot be empty!")

    elif args.command == 'export-channel':
        success = downloader.export_channel(
            channel_id=args.channel_id,
            output_path=args.output,
            after_date=args.after,
            before_date=args.before,
            message_limit=args.limit,
            format_type=args.format
        )
        sys.exit(0 if success else 1)

    elif args.command == 'export-guild':
        success = downloader.export_guild(
            guild_id=args.guild_id,
            output_dir=args.output,
            format_type=args.format
        )
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()


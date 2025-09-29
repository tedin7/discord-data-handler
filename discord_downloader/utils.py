#!/usr/bin/env python3
"""
Discord Downloader - Utility functions
Helper functions for Discord token and channel management.
"""

import json
import re
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def validate_discord_token(token: str) -> bool:
    """
    Validate Discord token format.

    Args:
        token: Discord authentication token

    Returns:
        bool: True if token format is valid
    """
    if not token or not isinstance(token, str):
        return False

    # Discord tokens are typically 59 characters long
    # Format: mfa.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx or xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    token_pattern = r'^[a-zA-Z0-9_-]{50,70}$'
    return bool(re.match(token_pattern, token))


def extract_token_from_browser() -> Optional[str]:
    """
    Guide user to extract token from browser.

    Returns:
        str: Discord token if found, None otherwise
    """
    print("🔍 To get your Discord token:")
    print("1. Open Discord in a web browser (discord.com)")
    print("2. Press F12 or Ctrl+Shift+I to open Developer Tools")
    print("3. Go to the Console tab")
    print("4. Paste and run: localStorage.token")
    print("5. Copy the token value (long string)")
    print("")
    print("⚠️  WARNING: User tokens violate Discord's TOS!")
    print("💡 Consider creating a bot token instead for server channels.")
    print("")

    response = input("Enter your token (or press Enter to skip): ").strip()
    return response if response else None


def validate_channel_id(channel_id: str) -> bool:
    """
    Validate Discord channel ID format.

    Args:
        channel_id: Discord channel ID

    Returns:
        bool: True if channel ID format is valid
    """
    if not channel_id or not isinstance(channel_id, str):
        return False

    # Discord IDs are 17-19 digit numbers
    id_pattern = r'^\d{17,19}$'
    return bool(re.match(id_pattern, channel_id))


def validate_guild_id(guild_id: str) -> bool:
    """
    Validate Discord guild ID format.

    Args:
        guild_id: Discord guild/server ID

    Returns:
        bool: True if guild ID format is valid
    """
    return validate_channel_id(guild_id)  # Same format as channel IDs


def get_channel_id_from_link(link: str) -> Optional[str]:
    """
    Extract channel ID from Discord channel link.

    Args:
        link: Discord channel link (e.g., https://discord.com/channels/123456789/987654321)

    Returns:
        str: Channel ID if found, None otherwise
    """
    pattern = r'discord\.com/channels/[^/]+/(\d+)'
    match = re.search(pattern, link)
    if match:
        channel_id = match.group(1)
        return channel_id if validate_channel_id(channel_id) else None
    return None


def get_guild_id_from_link(link: str) -> Optional[str]:
    """
    Extract guild ID from Discord guild link.

    Args:
        link: Discord guild link (e.g., https://discord.com/channels/123456789)

    Returns:
        str: Guild ID if found, None otherwise
    """
    pattern = r'discord\.com/channels/(\d+)'
    match = re.search(pattern, link)
    if match:
        guild_id = match.group(1)
        return guild_id if validate_guild_id(guild_id) else None
    return None


def create_config_template(output_path: str = "config/discord_config.json") -> None:
    """
    Create a configuration template file.

    Args:
        output_path: Path for the config file
    """
    config = {
        "token": "",
        "default_output_dir": "output",
        "default_format": "Html",
        "download_media": True,
        "rate_limit_delay": 1.0,
        "max_retries": 3,
        "user_agent": "DiscordChatExporter/2.40.0"
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✅ Created config template: {output_path}")


def load_config(config_path: str = "config/discord_config.json") -> Dict:
    """
    Load configuration from file.

    Args:
        config_path: Path to config file

    Returns:
        dict: Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  Config file not found: {config_path}")
        print("Creating template...")
        create_config_template(config_path)
        return load_config(config_path)
    except json.JSONDecodeError:
        print(f"❌ Invalid config file: {config_path}")
        return {}


def print_discord_setup_guide() -> None:
    """Print comprehensive Discord setup guide."""
    print("=" * 60)
    print("🔧 DISCORD DOWNLOADER SETUP GUIDE")
    print("=" * 60)
    print()
    print("📋 PREREQUISITES:")
    print("• Fedora Linux with terminal access")
    print("• .NET 9.0 runtime installed")
    print("• DiscordChatExporter CLI installed")
    print()
    print("⚠️  IMPORTANT WARNINGS:")
    print("• Using user tokens violates Discord's Terms of Service")
    print("• Bot tokens are recommended for server channels")
    print("• Keep your token secure and never share it")
    print()
    print("🚀 QUICK START:")
    print("1. Install dependencies: python discord_downloader.py install-deps")
    print("2. Set your token: python discord_downloader.py set-token")
    print("3. Export a channel: python discord_downloader.py export-channel CHANNEL_ID")
    print()
    print("📚 DETAILED SETUP:")
    print()
    print("1. ENABLE DEVELOPER MODE IN DISCORD:")
    print("   • User Settings > Advanced > Developer Mode (toggle ON)")
    print()
    print("2. GET YOUR DISCORD TOKEN:")
    print("   • Open Discord web (discord.com)")
    print("   • Press F12 → Console tab")
    print("   • Run: localStorage.token")
    print("   • Copy the token string")
    print()
    print("3. GET CHANNEL/GUILD IDs:")
    print("   • Right-click channel/server → Copy ID")
    print("   • Or extract from Discord links")
    print()
    print("4. CREATE A BOT TOKEN (RECOMMENDED):")
    print("   • Go to https://discord.com/developers/applications")
    print("   • New Application → Bot section")
    print("   • Copy bot token")
    print("   • Invite bot to server with 'Read Message History' permission")
    print()
    print("=" * 60)


def open_discord_developer_portal() -> None:
    """Open Discord Developer Portal in default browser."""
    print("🌐 Opening Discord Developer Portal...")
    webbrowser.open("https://discord.com/developers/applications")
    print("✅ Portal opened. Create a new application and bot token.")


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        str: Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f"} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def count_files_in_directory(directory: str) -> Tuple[int, int]:
    """
    Count files and total size in a directory.

    Args:
        directory: Directory path

    Returns:
        tuple: (file_count, total_size_bytes)
    """
    path = Path(directory)
    if not path.exists():
        return 0, 0

    file_count = 0
    total_size = 0

    for file_path in path.rglob('*'):
        if file_path.is_file():
            file_count += 1
            total_size += file_path.stat().st_size

    return file_count, total_size


def clean_filename(filename: str) -> str:
    """
    Clean filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        str: Cleaned filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    cleaned = filename
    for char in invalid_chars:
        cleaned = cleaned.replace(char, '_')

    # Remove leading/trailing dots and spaces
    cleaned = cleaned.strip('. ')
    cleaned = re.sub(r'\.{2,}', '.', cleaned)  # Multiple dots to single

    return cleaned or "unnamed_file"

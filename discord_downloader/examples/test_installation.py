#!/usr/bin/env python3
"""
Discord Downloader - Installation Test Script
Tests if all dependencies are properly installed and configured.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """Run a command and report success/failure."""
    print(f"🧪 Testing {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print(f"✅ {description}: PASSED")
            return True
        else:
            print(f"❌ {description}: FAILED")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print(f"❌ {description}: FAILED - Command not found")
        return False


def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists."""
    path = Path(file_path)
    if path.exists():
        print(f"✅ {description}: FOUND")
        return True
    else:
        print(f"❌ {description}: MISSING")
        return False


def main():
    """Run installation tests."""
    print("🔍 Discord Downloader - Installation Test")
    print("=" * 50)
    print()

    all_passed = True

    # Test .NET runtime
    all_passed &= run_command(["dotnet", "--version"], ".NET Runtime Installation")

    # Test DiscordChatExporter CLI
    exporter_path = "discord_downloader/bin/discordchatexporter/DiscordChatExporter.Cli.dll"
    all_passed &= check_file_exists(exporter_path, "DiscordChatExporter CLI")

    # Test Python script
    script_path = "discord_downloader/discord_downloader.py"
    all_passed &= check_file_exists(script_path, "Main Python Script")

    # Test utils module
    utils_path = "discord_downloader/utils.py"
    all_passed &= check_file_exists(utils_path, "Utils Module")

    # Test config directory
    config_dir = "discord_downloader/config"
    all_passed &= check_file_exists(f"{config_dir}/discord_config.json", "Configuration File")

    # Test installation script
    install_script = "discord_downloader/scripts/install_dependencies.sh"
    all_passed &= check_file_exists(install_script, "Installation Script")

    print()
    print("=" * 50)

    if all_passed:
        print("🎉 All tests PASSED! Installation is complete.")
        print()
        print("🚀 Next steps:")
        print("1. Run: python discord_downloader.py set-token")
        print("2. Run: python discord_downloader.py export-channel <CHANNEL_ID>")
    else:
        print("⚠️  Some tests FAILED. Please check the errors above.")
        print()
        print("🔧 To fix installation:")
        print("   python discord_downloader.py install-deps")
        print("   # or")
        print("   bash discord_downloader/scripts/install_dependencies.sh")

    print()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())


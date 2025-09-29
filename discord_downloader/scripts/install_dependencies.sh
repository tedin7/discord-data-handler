#!/bin/bash

# Discord Downloader - Dependency Installation Script
# This script installs .NET runtime and DiscordChatExporter CLI on Fedora Linux

set -e  # Exit on any error

echo "🔧 Installing dependencies for Discord Downloader..."

# Update system packages
echo "📦 Updating system packages..."
sudo dnf update -y

# Install .NET runtime (version 9.0)
echo "🛠️  Installing .NET 9.0 runtime..."
sudo dnf install -y dotnet-runtime-9.0

# Verify .NET installation
echo "✅ Verifying .NET installation..."
if command -v dotnet &> /dev/null; then
    echo "✅ .NET version: $(dotnet --version)"
else
    echo "❌ .NET installation failed"
    exit 1
fi

# Create working directory for DiscordChatExporter
echo "📁 Setting up DiscordChatExporter..."
mkdir -p ../bin/discordchatexporter

# Download DiscordChatExporter CLI
echo "⬇️  Downloading DiscordChatExporter CLI..."
cd ../bin/discordchatexporter
wget -q https://github.com/Tyrrrz/DiscordChatExporter/releases/latest/download/DiscordChatExporter.Cli-linux-x64.zip

# Extract the archive
echo "📦 Extracting DiscordChatExporter..."
unzip -q DiscordChatExporter.Cli-linux-x64.zip

# Clean up zip file
rm DiscordChatExporter.Cli-linux-x64.zip

# Make executable (if needed)
chmod +x *.dll

echo "✅ Installation complete!"
echo "📍 DiscordChatExporter installed in: $(pwd)"
echo "🚀 You can now run: python ../discord_downloader.py --help"


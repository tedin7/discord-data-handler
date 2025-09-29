# Discord Data Handler

A comprehensive Python toolkit for Discord data management that allows you to export Discord chat history with media files and upload content back to Discord channels on Fedora Linux.

## 🚀 Features

- **Full Chat Export**: Export complete Discord channel and server chat history
- **Media Download**: Automatically download all images, videos, files, and attachments
- **Multiple Formats**: Export to HTML, JSON, CSV, or plain text
- **Easy Configuration**: Secure token management and configuration files
- **Batch Processing**: Export entire Discord servers with all channels
- **Date Filtering**: Export chats within specific date ranges
- **Rate Limit Handling**: Built-in retry logic and rate limit management

## ⚠️ Important Warnings

- **Discord TOS**: Using user tokens violates Discord's Terms of Service
- **Security**: Never share your Discord token with anyone
- **Bot Tokens**: Use bot tokens for server channels when possible
- **Rate Limits**: Large exports may take time due to Discord's rate limits

## 📋 Prerequisites

- **Fedora Linux** (tested on Fedora 40+)
- **Terminal access** with basic command-line knowledge
- **Discord account** with Developer Mode enabled

### Enable Developer Mode in Discord

1. Open Discord in your web browser or desktop app
2. Go to **User Settings** → **Advanced**
3. Toggle **Developer Mode** on

## 🔧 Installation

### Step 1: Clone or Download
```bash
git clone git@github.com:tedin7/discord-data-handler.git
cd discord-data-handler
```

### Step 2: Install Dependencies
```bash
# Install .NET runtime and DiscordChatExporter CLI
python discord_downloader/discord_downloader.py install-deps

# Or run the installation script directly
bash discord_downloader/scripts/install_dependencies.sh
```

### Step 3: Verify Installation
```bash
dotnet --version  # Should show 9.0.x or later
```

## ⚙️ Configuration

### Get Your Discord Token

#### User Token (⚠️ Violates TOS)
1. Open Discord web (discord.com) in your browser
2. Press `F12` or `Ctrl+Shift+I` to open Developer Tools
3. Go to **Console** tab
4. Paste and run: `localStorage.token`
5. Copy the token string (long alphanumeric string)

#### Bot Token (Recommended)
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a **New Application**
3. Go to **Bot** section and create a bot
4. Copy the **Bot Token**
5. Invite the bot to your server with **"Read Message History"** permission

### Configure Token
```bash
python discord_downloader/discord_downloader.py set-token
# Enter your token when prompted
```

### Get Channel/Server IDs

1. **Enable Developer Mode** in Discord (see Prerequisites)
2. **Right-click** on any channel or server
3. Select **"Copy ID"**
4. The ID will be copied to your clipboard

## 📖 Usage

### Basic Usage

```bash
# Export a single channel
python discord_downloader/discord_downloader.py export-channel CHANNEL_ID

# Export with custom output path
python discord_downloader/discord_downloader.py export-channel CHANNEL_ID --output ./my_chat_export.html

# Export entire server/guild
python discord_downloader/discord_downloader.py export-guild GUILD_ID

# Export with date range
python discord_downloader/discord_downloader.py export-channel CHANNEL_ID --after "2023-01-01" --before "2024-01-01"

# Export without downloading media files
python discord_downloader/discord_downloader.py export-channel CHANNEL_ID --no-media

# Export to JSON format instead of HTML
python discord_downloader/discord_downloader.py export-channel CHANNEL_ID --format Json
```

### Command Reference

#### `set-token`
Configure your Discord authentication token
```bash
python discord_downloader/discord_downloader.py set-token
```

#### `export-channel CHANNEL_ID [OPTIONS]`
Export a single Discord channel

**Options:**
- `--output, -o PATH`: Custom output file path
- `--after DATE`: Start date (YYYY-MM-DD format)
- `--before DATE`: End date (YYYY-MM-DD format)
- `--limit NUM`: Maximum number of messages to export
- `--format FORMAT`: Export format (Html, Json, Csv, Txt) - default: Html
- `--no-media`: Skip downloading media files

#### `export-guild GUILD_ID [OPTIONS]`
Export all channels from a Discord server/guild

**Options:**
- `--output, -o DIR`: Custom output directory
- `--format FORMAT`: Export format (Html, Json, Csv, Txt) - default: Html
- `--no-media`: Skip downloading media files

#### `install-deps`
Install required dependencies (.NET runtime and DiscordChatExporter CLI)

### Advanced Examples

```bash
# Export specific date range with message limit
python discord_downloader/discord_downloader.py export-channel 123456789012345678 \
    --after "2023-06-01" \
    --before "2023-06-30" \
    --limit 5000 \
    --output ./june_2023_export.html

# Export entire server to JSON format
python discord_downloader/discord_downloader.py export-guild 987654321098765432 \
    --format Json \
    --output ./server_data/

# Export DM conversation without media
python discord_downloader/discord_downloader.py export-channel 555666777888999000 \
    --no-media \
    --format Txt \
    --output ./dm_conversation.txt
```

## 📁 Output Structure

### Single Channel Export
```
output/
├── channel_123456789012345678_discord_export.html  # Main chat file
└── media/                                           # Downloaded files
    ├── images/
    │   ├── message_001.jpg
    │   └── message_002.png
    ├── videos/
    │   └── message_003.mp4
    └── files/
        └── document.pdf
```

### Guild Export
```
server_export/
├── general.html
├── random.html
├── announcements.html
├── media/
│   ├── general/
│   ├── random/
│   └── announcements/
└── [other channels].html
```

## 🛠️ Troubleshooting

### Common Issues

#### Installation Problems
```bash
# .NET runtime not found
sudo dnf install dotnet-runtime-9.0

# Permission denied errors
chmod +x discord_downloader/scripts/install_dependencies.sh
```

#### Export Failures
```bash
# Rate limiting (wait and retry)
# DiscordChatExporter has built-in retry logic

# Invalid token
python discord_downloader/discord_downloader.py set-token
# Re-enter your token

# Channel not found or no access
# Verify channel ID and permissions
```

#### Large Exports
- **Split by date**: Use `--after` and `--before` for large channels
- **Message limits**: Use `--limit` to avoid timeouts
- **Rate limits**: Tool automatically retries on rate limits

### Debug Mode
```bash
# The tool will show detailed error messages
# Check the command being executed for debugging
```

## 🔒 Security Best Practices

1. **Never share your token** - keep it private
2. **Use bot tokens** when possible for server exports
3. **Delete exported data** when no longer needed
4. **Regularly rotate tokens** for security
5. **Use HTTPS** when extracting tokens from browser

## 📊 Performance Tips

- **Small exports first**: Test with small channels before large exports
- **Date ranges**: Use specific date ranges to limit export size
- **Media optional**: Use `--no-media` for text-only exports
- **Format choice**: HTML includes media, JSON is more compact

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [DiscordChatExporter GitHub](https://github.com/Tyrrrz/DiscordChatExporter)
- [Discord Developer Portal](https://discord.com/developers/applications)
- [.NET Runtime Download](https://dotnet.microsoft.com/download)

## 🙏 Acknowledgments

- [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) by Tyrrrz
- Discord API for providing chat export functionality


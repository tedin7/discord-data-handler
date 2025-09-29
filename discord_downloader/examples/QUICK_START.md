# 🚀 Quick Start Guide

Get started with Discord Downloader in 3 simple steps:

## Step 1: Install Dependencies
```bash
python discord_downloader/discord_downloader.py install-deps
```

## Step 2: Set Your Token
```bash
python discord_downloader/discord_downloader.py set-token
# Enter your Discord token when prompted
```

## Step 3: Export Your First Channel
```bash
# Export a channel (replace with actual channel ID)
python discord_downloader/discord_downloader.py export-channel 123456789012345678

# Export with custom name
python discord_downloader/discord_downloader.py export-channel 123456789012345678 --output my_chat_backup.html
```

## 🎯 Common Export Commands

```bash
# Export entire server
python discord_downloader/discord_downloader.py export-guild 987654321098765432

# Export specific date range
python discord_downloader/discord_downloader.py export-channel 123456789012345678 --after "2023-01-01" --before "2023-12-31"

# Export without media (text only)
python discord_downloader/discord_downloader.py export-channel 123456789012345678 --no-media --format Txt

# Export to JSON for data analysis
python discord_downloader/discord_downloader.py export-channel 123456789012345678 --format Json
```

## 🆘 Getting IDs

### Channel ID:
1. Enable Developer Mode in Discord
2. Right-click channel → Copy ID

### Server/Guild ID:
1. Right-click server icon → Copy ID

### Token:
1. Open Discord web (discord.com)
2. F12 → Console → run: `localStorage.token`
3. Copy the token string

## 📁 Output Location
- Single channels: `output/` folder
- Server exports: `output/` folder with separate files
- Custom location: use `--output` flag

## 💡 Tips
- Start with small exports to test
- Use date ranges for large channels
- HTML format includes embedded media
- JSON format is best for data analysis


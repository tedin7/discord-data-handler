#!/bin/bash
# Example Discord Downloader Usage Script
# This script demonstrates various export scenarios

echo "🔥 Discord Downloader - Example Usage"
echo "===================================="
echo ""

# Note: Replace these IDs with your actual Discord IDs
CHANNEL_ID="123456789012345678"
GUILD_ID="987654321098765432"
TOKEN="YOUR_TOKEN_HERE"

echo "📋 Available Examples:"
echo "1. Basic channel export"
echo "2. Guild (server) export"
echo "3. Date-filtered export"
echo "4. Large channel export with limits"
echo "5. Text-only export"
echo ""

# Example 1: Basic channel export
echo "📌 Example 1: Basic channel export"
echo "python ../discord_downloader.py export-channel $CHANNEL_ID --output ./exports/basic_export.html"
echo ""

# Example 2: Export entire server
echo "📌 Example 2: Export entire server"
echo "python ../discord_downloader.py export-guild $GUILD_ID --output ./exports/server_backup/"
echo ""

# Example 3: Date-filtered export (specific month)
echo "📌 Example 3: Export messages from June 2023"
echo "python ../discord_downloader.py export-channel $CHANNEL_ID \\"
echo "    --after '2023-06-01' \\"
echo "    --before '2023-07-01' \\"
echo "    --output ./exports/june_2023.html"
echo ""

# Example 4: Large export with message limit
echo "📌 Example 4: Export first 10,000 messages"
echo "python ../discord_downloader.py export-channel $CHANNEL_ID \\"
echo "    --limit 10000 \\"
echo "    --output ./exports/large_channel_sample.html"
echo ""

# Example 5: Text-only export (no media)
echo "📌 Example 5: Export text-only (no images/videos)"
echo "python ../discord_downloader.py export-channel $CHANNEL_ID \\"
echo "    --no-media \\"
echo "    --format Txt \\"
echo "    --output ./exports/text_only_export.txt"
echo ""

# Example 6: JSON export for data analysis
echo "📌 Example 6: Export to JSON for analysis"
echo "python ../discord_downloader.py export-guild $GUILD_ID \\"
echo "    --format Json \\"
echo "    --output ./exports/server_data/"
echo ""

echo "💡 Tips:"
echo "• Replace CHANNEL_ID and GUILD_ID with actual Discord IDs"
echo "• Always use bot tokens when possible for server exports"
echo "• For large exports, consider using date ranges to split the data"
echo "• JSON format is great for data analysis and processing"
echo "• HTML format includes embedded media and is best for archival"
echo ""

echo "🔧 Setup Commands:"
echo "# Set your Discord token"
echo "python ../discord_downloader.py set-token"
echo ""
echo "# Install dependencies"
echo "python ../discord_downloader.py install-deps"
echo ""
echo "# Get help"
echo "python ../discord_downloader.py --help"


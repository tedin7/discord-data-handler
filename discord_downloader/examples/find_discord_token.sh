#!/bin/bash
# Discord Token Finder Script
# This script helps locate Discord data directories and potential token files

echo "🔍 Discord Token Finder"
echo "======================"
echo ""

# Common Discord installation paths
paths=(
    "$HOME/.config/discord"
    "$HOME/.config/Discord"
    "$HOME/.config/vesktop"
    "$HOME/.config/Vesktop"
    "$HOME/.var/app/com.discordapp.Discord/config/discord"
    "$HOME/.var/app/dev.vencord.Vesktop/config/vesktop"
    "$HOME/AppData/Roaming/discord"  # WSL
    "$HOME/.discord"
    "$HOME/.local/share/discord"
    "$HOME/snap/discord/common/.config/discord"
)

echo "🔍 Checking common Discord directories..."
found=false

for path in "${paths[@]}"; do
    if [ -d "$path" ]; then
        echo "✅ Found: $path"
        found=true

        # Look for token-related files
        echo "   🔍 Searching for token files..."
        find "$path" -type f \( -name "*token*" -o -name "*auth*" -o -name "*session*" \) 2>/dev/null | head -5

        # Check Local Storage directory
        if [ -d "$path/Local Storage" ]; then
            echo "   📁 Local Storage found - likely contains token files"
        fi
    fi
done

if [ "$found" = false ]; then
    echo "❌ No Discord directories found in common locations."
    echo "💡 Try these manual steps:"
    echo ""
    echo "1. Open Discord desktop app"
    echo "2. Press Ctrl+Shift+I (or F12) to open Developer Tools"
    echo "3. Go to Console tab"
    echo "4. Run: localStorage.token"
    echo "5. Copy the token string"
fi

echo ""
echo "🌐 Alternatively, use Discord Web (RECOMMENDED):"
echo "1. Go to https://discord.com"
echo "2. Press F12 → Console tab"
echo "3. Run: localStorage.token"
echo "4. Copy the output"

echo ""
echo "⚠️  Remember: User tokens violate Discord's TOS!"


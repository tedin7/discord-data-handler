# 🔑 How to Get Your Discord Token

## ⚠️ IMPORTANT WARNINGS

- **TOS Violation**: Using user tokens violates Discord's Terms of Service
- **Account Risk**: Your account could be banned if Discord detects self-bot usage
- **Security Risk**: Anyone with your token has full access to your account
- **Alternative**: Use bot tokens for server exports (recommended)

## 🔍 Getting User Token (⚠️ NOT RECOMMENDED)

### Method 1: Browser Developer Tools (Recommended)

1. **Open Discord Web**:
   - Go to https://discord.com in your browser
   - Log in to your account

2. **Open Developer Tools**:
   - Press `F12` or `Ctrl+Shift+I` (Linux/Windows)
   - Or right-click anywhere → "Inspect Element"

3. **Navigate to Console**:
   - Click on the "Console" tab at the top

4. **Extract Token**:
   ```javascript
   localStorage.token
   ```
   - Paste this in the Console and press Enter
   - Copy the output (long string like "mfa.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

5. **Verify Token**:
   - The token should be 50-70 characters long
   - Contains letters, numbers, and hyphens

### Method 2: Discord Desktop App (Alternative)

1. **Close Discord** completely
2. **Navigate to data folder**:
   ```bash
   # Linux
   cd ~/.config/discord/
   # or
   find ~ -name "Local Storage" -type d 2>/dev/null | head -1
   ```

3. **Find token files**:
   - Look for files containing "token"
   - Open with text editor
   - Search for your token

## 🤖 Getting Bot Token (RECOMMENDED)

### Step 1: Create Discord Application

1. **Go to Developer Portal**:
   - Visit: https://discord.com/developers/applications
   - Log in with your Discord account

2. **Create New Application**:
   - Click "New Application"
   - Enter a name (e.g., "Chat Exporter Bot")
   - Click "Create"

### Step 2: Create Bot

1. **Go to Bot Section**:
   - In your application, click "Bot" in the left menu

2. **Add Bot**:
   - Click "Add Bot"
   - Confirm when prompted

3. **Copy Bot Token**:
   - Click "Copy" under "Token"
   - Save this token securely

### Step 3: Invite Bot to Server

1. **Generate Invite Link**:
   - In Bot section, scroll down to "URL Generator"
   - Select permissions: "Read Message History"
   - Copy the generated URL

2. **Invite Bot**:
   - Paste the URL in your browser
   - Select your server
   - Click "Authorize"

3. **Verify Bot**:
   - Bot should appear in your server
   - It needs "Read Message History" permission

## 🔒 Token Security

### User Tokens:
- **Never share** your user token
- **Store securely** - consider encrypted storage
- **Rotate regularly** if compromised
- **Delete after use** for one-time exports

### Bot Tokens:
- **More secure** - bots can't be banned as easily
- **Scoped permissions** - only what you grant
- **Can be regenerated** easily
- **No TOS violation** for legitimate use

## 🧪 Test Your Token

```bash
# Test with our Discord downloader
python discord_downloader.py set-token

# Then try a small export
python discord_downloader.py export-channel YOUR_CHANNEL_ID --limit 10
```

## 🚨 If Your Token is Compromised

### User Token:
1. **Change Password**: Discord Settings → Account → Change Password
2. **Enable 2FA**: Settings → Security → Two-Factor Authentication
3. **Log out everywhere**: Settings → Advanced → Log Out All Devices

### Bot Token:
1. **Regenerate token** in Developer Portal
2. **Update your config** with new token
3. **Re-invite bot** to servers if needed

## 💡 Recommendations

1. **Use bot tokens** for server exports
2. **User tokens only** for personal DM exports
3. **Test small exports** first
4. **Keep tokens encrypted** and backed up
5. **Monitor your account** for suspicious activity

## 🔗 Useful Links

- [Discord Developer Portal](https://discord.com/developers/applications)
- [Discord Permissions Calculator](https://discord.com/developers/docs/topics/permissions)
- [Bot Token Best Practices](https://discord.com/developers/docs/topics/oauth2#bot-authorization-flow)


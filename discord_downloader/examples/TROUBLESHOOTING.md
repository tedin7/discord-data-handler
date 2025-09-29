# 🔧 Troubleshooting Guide

## Installation Issues

### .NET Runtime Not Found
**Error:** `dotnet: command not found`
**Solution:**
```bash
sudo dnf install dotnet-runtime-9.0
```

### Permission Denied
**Error:** `Permission denied` when running scripts
**Solution:**
```bash
chmod +x discord_downloader/scripts/install_dependencies.sh
chmod +x discord_downloader/discord_downloader.py
```

### DiscordChatExporter Not Found
**Error:** `DiscordChatExporter.Cli.dll not found`
**Solution:** Run installation script:
```bash
python discord_downloader/discord_downloader.py install-deps
```

## Export Issues

### Invalid Token
**Error:** Authentication failed
**Solution:**
1. Verify token is correct
2. Re-run: `python discord_downloader/discord_downloader.py set-token`
3. For user tokens: Extract fresh token from browser
4. For bot tokens: Regenerate in Discord Developer Portal

### Channel Not Found
**Error:** `Channel not found` or `No access`
**Solution:**
1. Verify channel ID is correct
2. Check if you have access to the channel
3. For servers: Use bot token with proper permissions
4. For DMs: Use user token

### Rate Limiting
**Error:** Export stops frequently
**Solution:**
- Wait 5-15 minutes and retry
- The tool has built-in retry logic
- For large exports: Use date ranges to split
- Consider `--limit` flag to reduce size

### Large Export Timeouts
**Error:** Export takes too long or times out
**Solution:**
```bash
# Split large exports by date
python discord_downloader/discord_downloader.py export-channel ID --after "2023-01-01" --before "2023-06-30"
python discord_downloader/discord_downloader.py export-channel ID --after "2023-07-01" --before "2023-12-31"

# Use message limits
python discord_downloader/discord_downloader.py export-channel ID --limit 5000
```

## Configuration Issues

### Config File Problems
**Error:** `Config file not found` or `Invalid config`
**Solution:**
1. Delete corrupted config: `rm discord_downloader/config/discord_config.json`
2. Re-run: `python discord_downloader/discord_downloader.py set-token`
3. The tool will recreate the config file

### No Output Files
**Error:** Export completes but no files created
**Solution:**
1. Check output directory permissions
2. Use `--output ./test.html` to specify custom location
3. Verify you have read permissions for the channel

## Network Issues

### Connection Errors
**Error:** Network timeout or connection refused
**Solution:**
1. Check internet connection
2. Try again later (Discord may be having issues)
3. For VPN users: Discord may block some VPNs

### Firewall Blocking
**Error:** Connection blocked
**Solution:**
1. Check firewall settings
2. Allow .NET and wget/curl connections
3. Try from different network

## Performance Issues

### Slow Exports
**Solutions:**
1. Use `--no-media` for text-only exports
2. Export specific date ranges instead of everything
3. Export during off-peak hours
4. Split large channels into smaller chunks

### High Memory Usage
**Solutions:**
1. Close other applications during export
2. Use `--limit` to reduce message count
3. Restart system if memory issues persist

## Discord-Specific Issues

### Developer Mode Not Enabled
**Problem:** Can't copy channel IDs
**Solution:**
1. Discord Settings → Advanced → Developer Mode (toggle ON)
2. Restart Discord
3. Right-click channels/servers to copy IDs

### Bot Token Issues
**Problem:** Bot can't access channels
**Solution:**
1. Invite bot to server again
2. Ensure bot has "Read Message History" permission
3. Check if bot is online in server

### User Token Revoked
**Problem:** Token suddenly stops working
**Solution:**
1. Extract fresh token from browser
2. Re-run: `python discord_downloader/discord_downloader.py set-token`
3. Consider switching to bot token

## Getting Help

### Debug Information
The tool shows detailed error messages. Include these when asking for help.

### Common Error Messages
- `"No Discord token configured"` → Run `set-token`
- `"DiscordChatExporter not found"` → Run `install-deps`
- `"Rate limited"` → Wait and retry
- `"Channel not found"` → Verify channel ID and permissions

### Community Support
- Check [DiscordChatExporter GitHub Issues](https://github.com/Tyrrrz/DiscordChatExporter/issues)
- Fedora forums for .NET installation issues
- Discord.py communities for bot token help

## Prevention Tips

1. **Test small exports first** before large ones
2. **Backup your token** - you'll need to re-extract it if lost
3. **Use date ranges** for large channels to avoid timeouts
4. **Monitor disk space** - exports can be large with media
5. **Keep software updated** - run `sudo dnf update` regularly


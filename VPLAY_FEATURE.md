# 🎥 VPlay Feature - Video Playback

## Overview
The `/vplay` feature has been successfully added to HasiiMusicBot! This allows you to play YouTube videos with both video and audio in your Telegram group voice chats.

## Available Commands

### Basic Video Play Commands
- `/vplay <query or URL>` - Play a video in voice chat
- `/vplayforce <query or URL>` - Force play a video (skips queue)
- `/cvplay <query or URL>` - Play video in linked channel
- `/cvplayforce <query or URL>` - Force play video in linked channel

### Audio Commands (existing)
- `/play <query or URL>` - Play audio only
- `/playforce <query or URL>` - Force play audio
- `/cplay <query or URL>` - Play audio in linked channel
- `/cplayforce <query or URL>` - Force play audio in linked channel

## Usage Examples

### Play a video from YouTube
```
/vplay Despacito
/vplay https://youtube.com/watch?v=kJQP7kiw5Fk
```

### Force play (skip queue)
```
/vplayforce Shape of You
```

### Play in linked channel
```
/cvplay Blinding Lights
```

## How It Works

1. **Command Detection**: The bot detects if your command starts with 'v' (vplay) or has 'v' as the second character (cvplay)
2. **Video Download**: When video mode is enabled, the bot downloads the video format (720p max) instead of audio only
3. **Video Streaming**: The bot streams both audio and video to the voice chat using PyTgCalls

## Technical Details

### Modified Files
1. **play.py** - Added vplay commands to handler, video flag detection, and video parameter passing
2. **calls.py** - Updated `play_media()` function to support video streaming
3. **\_play.py** - Added video detection logic in the checkUB decorator

### Video Stream Configuration
- **Video Quality**: HD 720p (1280x720)
- **Audio Quality**: Studio quality
- **Format**: MP4 (best quality available)
- **Download Location**: `downloads/` folder

## Requirements

Make sure your bot has these permissions in the group:
- ✅ Manage Voice Chats
- ✅ Send Messages
- ✅ Send Media
- ✅ Delete Messages

## Notes

- Video playback requires more bandwidth than audio only
- Videos are limited to 720p to balance quality and performance
- The bot automatically detects if a URL is a video and downloads accordingly
- Live streams are supported for both audio and video modes
- Video files are stored in the `downloads/` folder and reused if the same video is requested again

## Troubleshooting

### Video not playing?
- Make sure the bot has proper admin permissions
- Check if the assistant userbot has joined the voice chat
- Verify that YouTube cookies are up to date (for age-restricted content)

### Only hearing audio?
- Some Telegram clients may not support video in voice chats on older versions
- Update your Telegram app to the latest version
- Try using the desktop or web version of Telegram

### Performance issues?
- Video streaming requires more resources than audio
- Consider using `/play` for audio-only mode if experiencing lag
- Check your server's internet bandwidth

## Credits

This feature is inspired by [AnnieXMusic](https://github.com/hasindume/AnnieXMusic) bot.
Implementation adapted for HasiiMusicBot architecture.

---

**Enjoy video playback in your Telegram groups! 🎬🎵**

<div align="center">
  <img src="https://files.catbox.moe/f3i3yi.png" alt="˹ʜᴀꜱɪɪ ᴍᴜꜱɪᴄ˼" width="400"/>
  
  # 🎵 ˹ʜᴀꜱɪɪ ᴍᴜꜱɪᴄ˼
  
  <p><b>A Powerful Telegram Music Player Bot</b></p>
  
  [![Telegram](https://img.shields.io/badge/Telegram-Channel-blue?style=for-the-badge&logo=telegram)](https://t.me/TheInfinityAI)
  [![Telegram](https://img.shields.io/badge/Telegram-Support-blue?style=for-the-badge&logo=telegram)](https://t.me/Hasindu_Lakshan)
  
</div>

---

## ✨ Features

- 🎵 **High Quality Music Streaming** - Crystal clear audio with STUDIO quality
- 📻 **Live Radio Streaming** - 50+ international and local radio stations (Request)
- 🎧 **YouTube Support** - Play music from YouTube links or search
- 📝 **Queue System** - Manage multiple songs in queue
- ⚡ **Fast & Reliable** - Built with Pyrogram and PyTgCalls
- 🎛 **Admin Controls** - Pause, resume, skip, and stop controls
- 👥 **User Authorization** - Authorized users can control playback
- 📊 **Statistics** - Track bot usage and performance
- 🔄 **Auto-Leave** - Automatically leaves inactive voice chats

---

## 🚀 Deployment

### ✔️ Prerequisites

- Python 3.10+ installed
- Deno & FFmpeg installed on your system
- Required variables mentioned in sample.env

### Requirements

- Python 3.12+
- MongoDB Database
- Telegram Bot Token
- Telegram API ID & Hash
- Pyrogram String Session

### Environment Variables

Create a `.env` file with the following variables:

```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
MONGO_DB_URI=your_mongodb_uri
LOGGER_ID=your_logger_group_id
OWNER_ID=your_user_id
STRING_SESSION=your_pyrogram_session
COOKIE_URL=youtube_cookies_url (optional)
```

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/hasindu-nagolla/HasiiMusicBot
cd HasiiMusicBot
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

```bash
cp sample.env .env
# Edit .env with your values
```

4. **Run the bot**

```bash
bash start
```

---

## 📖 Commands

### User Commands

- `/play` - Play a song (YouTube URL or search query)
- `/radio` - Browse and play live radio stations
- `/queue` - View current queue
- `/ping` - Check bot status
- `/help` - Show help menu

### Admin Commands

- `/pause` - Pause current stream
- `/resume` - Resume paused stream
- `/skip` - Skip current track (also `/next`)
- `/stop` - Stop playing and clear queue (also `/end`)
- `/seek` - Seek to specific timestamp
- `/reload` - Reload admin cache

### Sudo Commands

- `/stats` - View bot statistics
- `/broadcast` - Broadcast message to all chats
- `/addsudo` - Add sudo user
- `/rmsudo` - Remove sudo user
- `/gban` - Globally ban a user across all chats
- `/ungban` - Remove global ban
- `/maintenance` - Toggle maintenance mode
- `/restart` - Restart the bot
- `/logs` - Get bot logs

---

## 🛠 Configuration

### Audio Quality Settings

The bot streams audio at **STUDIO** quality (highest available) with:

- **Codec**: Opus (best quality for music)
- **Format**: WebM container for audio downloads
- **Sample Rate**: 48kHz
- **Channels**: Stereo
- **Optimization**: Max 5 concurrent downloads, 1MB chunks

### Customization

- Modify language files in `HasiiMusic/locales/`
- Customize thumbnails and images in `config.py`
- Adjust queue limits and duration in `config.py`

---

## 📞 Support & Contact

- **Developer**: Hasindu Nagolla
- **Telegram Channel**: [@TheInfinityAI](https://t.me/TheInfinityAI)
- **Support Group**: [@Hasindu_Lakshan](https://t.me/Hasindu_Lakshan)
- **GitHub**: [hasindu-nagolla](https://github.com/hasindu-nagolla)

---

## 📝 Notes

- Make sure your bot is admin in both the group and logger group
- The assistant account will auto-join groups when needed for playback
- Keep your `.env` file secure and never share it publicly
- For YouTube downloads, cookies may be required for some videos
- Radio streams are live - no duration limits or downloads needed

---

## 🙏 Credits

Special thanks to [AnonymousX1025](https://github.com/AnonymousX1025) for the original inspiration.

---

<div align="center">
  
  ### Made with ❤️ by Hasindu Nagolla
  
  **© 2025 ˹ʜᴀꜱɪɪ ᴍᴜꜱɪᴄ˼. All rights reserved.**
  
</div>


<p align="center">
  <a href="https://t.me/musicxhasii">
    <img src="https://files.catbox.moe/und0yt.jpg" width="600">
  </a>
</p>

## 🌟 Intro about application?

**HasiiMusicBot** is a modern Telegram music bot built using Pyrogram and PyTgCalls. It streams high quality music in group voice chats. it supports various platforms like YouTube, Spotify.


## 🔑 Environment Variables

Below are the required and optional environment variables for deployment.

```env
API_ID=              # Required
API_HASH=            # Required
BOT_TOKEN=           # Required
OWNER_ID=            # Required - Telegram user ID
LOGGER_ID=           # Required - Log group/channel ID
STRING_SESSION=      # Required 
MONGO_DB_URI=        # Required 
COOKIE_URL=          # Required 

API_KEY=             # Optional
API_URL=             # Optional
```

⚠️ Use safe paste services like [Pastebin](https://pastebin.com) or [Batbin](https://batbin.me) for save cookies (YT Cookies).


### 🎧 Recommended streaming quality overrides

To get the clearest playback, drop these keys in your `.env` (or keep the same values from `sample.env`). They align with PyTgCalls’ highest quality presets and yt-dlp’s high-bitrate formats while staying compatible with most hosting setups.

```env
# Audio-only voice chats
STREAM_AUDIO_ONLY_QUALITY=studio

# Audio track inside video calls
STREAM_VIDEO_AUDIO_QUALITY=studio

# Outgoing video resolution
STREAM_VIDEO_QUALITY=fhd_1080p

# yt-dlp format preferences
YTDLP_AUDIO_FORMAT=bestaudio[abr>=256]/bestaudio/best
YTDLP_VIDEO_FORMAT=best[height<=?1080][width<=?1920]
YTDLP_PREFERRED_AUDIO_BITRATE=320
```


### ☕ VPS Setup Guide

```bash
🎵 Deploy  on VPS

### Step 1: Update & Install Packages
sudo apt update && sudo apt upgrade -y
sudo apt install git curl python3-pip python3-venv ffmpeg -y
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
npm install -g npm

### Step 2: Clone Repo
git clone repo_link
cd file_name
tmux new -s bot_name

### Step 3: Setup & Run
python3 -m venv venv
source venv/bin/activate
pip install -U pip && pip install -r requirements.txt
bash setup   # Fill environment variables
bash start   # Start bot

### Useful Commands
tmux detach         # Use Ctrl+B, then D
tmux attach-session -t tune # Attach to Running Bot session
tmux kill-session -t tune # to kill the running bot session
rm -rf TuneViaBot  # Uninstall the repo
```

  </details>
</div>

##

### 🐳 Docker Deployment

<img src="https://img.shields.io/badge/Show%20/Hide-Docker%20Steps-10b981?style=for-the-badge" alt="Toggle Docker Steps"/>

<div align="left">
  <details>

```bash
### Step 1: Clone Repo
git clone https://github.com/CertifiedCoders/TuneViaBot
cd TuneViaBot

### Step 2: Create .env File
nano .env
# Paste your environment variables here and save (Ctrl+O, Enter, Ctrl+X)

### Step 3: Build Image
docker build -t tuneviabot .

### Step 4: Run Container
docker run -d --name tune --env-file .env --restart unless-stopped tuneviabot

### Step 5: Manage Container
docker logs -f tune        # View logs (Ctrl+C to exit)
docker stop tune           # Stop container
docker start tune          # Start again
docker rm -f tune          # Remove container
docker rmi tuneviabot      # Remove image
```

  </details>
</div>



##
### ☁️ Quick Deploy

| Platform                | Deploy Link                                                                                                                                                                                               |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🔑 **Generate Session** | <a href="https://t.me/SessionBuilderbot"><img src="https://img.shields.io/badge/Session%20-Generator-blue?style=for-the-badge&logo=telegram"/></a>                                                    |
| 🌍 **Heroku Deploy**    | <a href="http://dashboard.heroku.com/new?template=https://github.com/CertifiedCoders/TuneViaBot"><img src="https://img.shields.io/badge/Deploy%20to-Heroku-purple?style=for-the-badge&logo=heroku"/></a> |




## 💬 Community & Support

<p align="center">
  <a href="https://t.me/CertifiedCoders">
    <img src="https://img.shields.io/badge/Support_Group-Telegram-0088cc?style=for-the-badge&logo=telegram&logoColor=white" />
  </a>
  <a href="https://t.me/CertifiedCodes">
    <img src="https://img.shields.io/badge/Updates_Channel-Telegram-6A5ACD?style=for-the-badge&logo=telegram&logoColor=white" />
  </a>
  <a href="https://t.me/CertifiedCoder">
    <img src="https://img.shields.io/badge/Contact_Owner-Telegram-4CAF50?style=for-the-badge&logo=telegram&logoColor=white" />
  </a>
  <a href="https://youtube.com/@rajnisha3">
    <img src="https://img.shields.io/badge/Subscribe-YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" />
  </a>
  <a href="https://instagram.com/rajnishthegreat">
    <img src="https://img.shields.io/badge/Follow-Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white" />
  </a>
  <a href="mailto:rajnishmishraaa1@gmail.com">
    <img src="https://img.shields.io/badge/Contact-Email-0078D4?style=for-the-badge&logo=gmail&logoColor=white" />
  </a>
</p>


##
### 🔖 Credits

* <b> *sᴩᴇᴄɪᴀʟ ᴛʜᴀɴᴋs ᴛᴏ <a href="https://github.com/AnonymousX1025">ᴀɴᴏɴʏ</a> ғᴏʀ <a href="https://github.com/AnonymousX1025/AnonXMusic">ᴀɴᴏɴxᴍᴜsɪᴄ</a>* </b>
* <b> *ᴄʀᴀғᴛᴇᴅ ᴡɪᴛʜ ᴘᴀssɪᴏɴ ʙʏ <a href="https://github.com/CertifiedCoders">ᴄᴇʀᴛɪғɪᴇᴅ ᴄᴏᴅᴇʀs</a>* </b>

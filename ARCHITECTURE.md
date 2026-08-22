# 🏗 Technical Architecture & Libraries

Welcome to the technical documentation for **HasiiMusicBot**. This document explains the core Python libraries used to build this bot, their roles, and how they interact to provide a seamless music streaming experience in Telegram voice chats.

---

## 📚 Core Technologies

### 1. Pyrogram (Telegram MTProto Framework)
[Pyrogram](https://docs.pyrogram.org/) is a modern, elegant, and asynchronous MTProto API framework for Telegram.
* **Role in HasiiMusicBot:** Pyrogram acts as the central brain of the bot. It is responsible for handling all incoming messages, commands (e.g., `/play`, `/skip`), inline queries, and button callbacks.
* **Implementation:** Mostly configured in `HasiiMusic/core/bot.py` and `HasiiMusic/core/telegram.py`. 
* **Assistant Account:** We utilize a Pyrogram String Session to host an "Assistant" userbot. Telegram does not allow standard bots to play audio in voice chats natively. Therefore, this Assistant Account acts on behalf of the bot to join the voice chat and stream the audio.

### 2. PyTgCalls (Voice Chat Streaming API)
[PyTgCalls](https://pytgcalls.github.io/PyTgCalls/) is a powerful asynchronous Python library for handling Telegram Group Voice Calls.
* **Role in HasiiMusicBot:** While Pyrogram handles the text and UI logic, PyTgCalls is entirely responsible for the audio processing and streaming. It connects the Assistant Account to the Telegram Voice Chat via WebRTC.
* **Implementation:** Managed centrally in the modular `HasiiMusic/core/calls/` package. It natively handles audio queues, pausing, resuming, and muting the stream directly inside the active voice chat.

### 3. yt-dlp & FFmpeg (Media Extraction & Processing)
* **yt-dlp:** We use `yt-dlp` (located in the modular `HasiiMusic/core/youtube/` package) to bypass the need to download entire videos. Instead, it extracts the direct high-quality audio stream URLs (like Opus/WebM) from YouTube and other platforms. It also utilizes robust file-locking mechanisms to safely manage parallel downloads and caching.
* **FFmpeg:** Acts as the backend engine. `PyTgCalls` utilizes FFmpeg to transcode these media streams on-the-fly into a format compatible with Telegram Voice Chats (Raw Audio/PCM).

### 4. Motor (Asynchronous MongoDB)
* **Role in HasiiMusicBot:** To maintain the asynchronous nature of the bot, we use `Motor` (in `HasiiMusic/core/mongo.py`) for all database interactions. This ensures that saving and retrieving data (like broadcast lists, banned users, and chat settings) does not block the main event loop, keeping the bot fast and responsive.

### 5. Spotify Integration & Lazy Loading
* **Role in HasiiMusicBot:** To support massive Spotify playlists without hitting API rate limits or timeouts, the bot employs a highly optimized lazy-loading architecture.
* **Implementation:** Managed in the `HasiiMusic/core/spotify/` package. When a Spotify playlist is queued, the bot instantly fetches basic metadata and lazily resolves the actual YouTube audio streams (fetching "Official Audio" for studio quality) only when the track is about to be played.

---

## 🔄 The Streaming Lifecycle (Under the Hood)

Here is the step-by-step technical flow when a user triggers a music playback command:

1. **Command Reception:** A user sends `/play [query]` in a group. Pyrogram intercepts this in the plugins directory (`plugins/playback/play.py`).
2. **Data Fetching:** The bot queries YouTube using `yt-dlp` to fetch the metadata (title, duration, thumbnail) and the optimal audio stream URL.
3. **Queue Management:** The song details are appended to the internal queue memory mapping managed in `helpers/_queue.py`.
4. **Connection:** If the Assistant Account is not already present in the group's Voice Chat, `PyTgCalls` initiates a connection and the userbot joins the call.
5. **Broadcasting:** `PyTgCalls` takes the audio stream URL, processes it through FFmpeg, and begins broadcasting the audio to the listeners in the Voice Chat.

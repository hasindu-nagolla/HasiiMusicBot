# v1.0.5 Release - GitHub Summary

**Version:** 1.0.5  
**Release Title:** 🎵 Major Feature Update - Enhanced Broadcast, Preload System & 45+ Bug Fixes

## 🚀 Quick Summary
This release brings **190 commits** with major new features, critical bug fixes, and significant enhancements. Notable changes include preload functionality for seamless playback, complete broadcast formatting preservation, and extensive stability improvements.

---

## ✨ What's New

### Major Features
- ⚡ **Preload System** - Next track preloading for zero-lag playback
- 🤖 **Bot Scanner** - `/bots` command to list all bots in groups
- 📊 **Group Data** - `/groupdata` for comprehensive group statistics

### Enhanced Features
- ✅ **Broadcast Formatting Preserved** - `/broadcast -copy` now keeps blockquotes, bold, italic, etc.
- ✅ **Extended Duration** - Song limit increased from 2.5 hours to **5 hours**
- ✅ **Admin Tools** - New `/gban`, maintenance mode, improved restart
- ✅ **Auto-Delete** - Bot messages auto-delete after 5 seconds
- ✅ **UI Redesign** - Major interface improvements

---

## 🐛 Critical Fixes (45+)

### Voice Chat & Playback
- Fixed duplicate stream end events
- Fixed race conditions in queue playback
- Fixed /vplay queue black screen
- Fixed audio lagging with FFmpeg optimization
- Fixed VC permission error handling

### Broadcast & Media
- Fixed media group (album) handling
- Fixed broadcast formatting preservation
- Fixed thumbnail generation issues

### Error Handling
- Fixed VPS crashes (multiple critical fixes)
- Fixed file handle leaks & memory issues
- Fixed FloodWait errors across all modules
- Fixed inline button errors
- Fixed permission issues

---

## 🔥 Breaking Changes

⚠️ **Bot is now English-only** - Multi-language support removed  
❌ **Removed:** LOOP button (use `/loop` command)  
❌ **Removed:** `/vplay` (merged into `/play`)  

---

## 📦 Technical Details

**Stats:**
- 50 files changed
- +3,677 lines added
- -1,011 lines removed
- 190 commits since v1.0.4

**Dependencies:**
- Updated yt-dlp to 2026.01.29
- Updated core libraries

**New Modules:**
- `core/preload.py` - Preload system
- `plugins/admin-controles/gban.py` - Global ban
- `plugins/admin-controles/maintenance.py` - Maintenance mode
- `plugins/admin-controles/restart.py` - Enhanced restart
- `plugins/features/bots.py` - Bot listing
- `plugins/features/groupdata.py` - Group analytics

---

## 📥 Installation

```bash
git clone https://github.com/hasindu-nagolla/HasiiMusicBot
cd HasiiMusicBot
pip install -r requirements.txt
# Configure .env file
bash start
```

---

## 🔗 Links

- **Full Release Notes:** See [RELEASE_NOTES_1.0.5.md](RELEASE_NOTES_1.0.5.md)
- **Support:** @HasiiMusicBot
- **Documentation:** PROJECT_STRUCTURE.md

---

**Stay tuned for more ❤️ | @HasiiMusicBot**

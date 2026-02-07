# 🎵 HasiiMusicBot v1.0.5 - Enhanced Broadcast, Preload System & 45+ Bug Fixes

## Release Overview
This is a substantial update bringing 190 commits with new features, critical bug fixes, performance improvements, and major architectural changes since v1.0.4.

**Release Stats:**
- **50 files changed** | +3,677 additions | -1,011 deletions
- **Net:** +2,666 lines of code
- **190 commits** to main since v1.0.4

---

## ✨ Major New Features

### ⚡ Preload System
- **NEW:** Next track preloading for seamless playback
- Reduces lag between songs
- Background track preparation
- Dedicated preload helper module (`_preload.py`)

### 🤖 Bot Scanner Feature
- `/bots` command to scan and list all bots in a group
- Bots displayed in a single blockquote format
- Helps admins manage bot presence in groups

### 📊 Group Data Feature
- `/groupdata` command to view comprehensive group statistics
- Member counts, group information, and analytics
- Fixed groupdata feature errors

---

## 🐛 Critical Bug Fixes

### Voice Chat & Playback
- ✅ **Fixed:** Duplicate stream end events causing playback issues
- ✅ **Fixed:** Race condition in queue playback
- ✅ **Fixed:** /vplay queue black screen issue
- ✅ **Fixed:** Race condition when stopping and immediately playing a new song
- ✅ **Fixed:** VC joined bug
- ✅ **Fixed:** NoActiveGroupCall vs CHAT_ADMIN_REQUIRED error handling
- ✅ **Fixed:** Strict VC permission check with proper logging
- ✅ **Fixed:** Voice chat error handling - distinguish disabled VC from missing permissions
- ✅ **Fixed:** Audio lagging with optimized FFmpeg buffering and streaming quality

### Broadcast System
- ✅ **Fixed:** Media group (album) handling in broadcast
- ✅ **Fixed:** AttributeError when stopping broadcast
- ✅ **Fixed:** Broadcast now preserves text formatting (blockquotes, bold, italic, etc.) with `-copy` flag

### Thumbnails & Media
- ✅ **Fixed:** cplay thumbnail issue
- ✅ **Fixed:** async/await syntax error in thumbnail generation
- ✅ **Fixed:** Media error handling

### Queue & Controls
- ✅ **Fixed:** Progress bar error
- ✅ **Fixed:** Queue management issues
- ✅ **Fixed:** /vplay duplicate functionality removed (consolidated into /play)

### Error Handling
- ✅ **Fixed:** Bot crashes on VPS (multiple critical fixes)
- ✅ **Fixed:** Indentation errors
- ✅ **Fixed:** AttributeError on bot removal
- ✅ **Fixed:** MESSAGE_AUTHOR_REQUIRED added to ignored errors
- ✅ **Fixed:** FloodWait error handling across multiple modules
- ✅ **Fixed:** Segmentation fault - made tournament timer async, fixed file handle leaks
- ✅ **Fixed:** Critical file handle leaks causing errors
- ✅ **Fixed:** Inline button errors (MESSAGE_NOT_MODIFIED, KeyError)
- ✅ **Fixed:** Help button HTML code display issues
- ✅ **Fixed:** Download file detection issues
- ✅ **Fixed:** YouTube download syntax errors
- ✅ **Fixed:** Null from_user errors
- ✅ **Fixed:** CHANNEL_INVALID errors
- ✅ **Fixed:** Permission issues across multiple modules
- ✅ **Fixed:** Auto cleanup task errors
- ✅ **Fixed:** Stats display errors

---

## 🚀 Enhancements

### Broadcast System
- `/broadcast -copy` now preserves ALL formatting (blockquotes, bold, italic, underline, strikethrough, spoilers, links)
- Media group (album) support in broadcast
- Improved error handling and retry logic
- FloodWait handling with automatic retry
- Better progress reporting

### Admin Features
- **NEW:** `/gban` - Global ban functionality (168 lines)
- **NEW:** Maintenance mode implementation (61 lines)
- **NEW:** Improved restart command (76 lines)
- **NEW:** Admin mention feature with restricted users support
- `/sudo` command improvements
- Bot admin required for sensitive operations

### UI/UX Improvements
- Major UI redesign (commit 76de333)
- Help menu improvements with proper button labels
- Swapped SUDO and GAMES button positions in help menu
- Added delete button to "added to queue" messages
- CLOSE button now appears under playback controls
- Auto-join logic for assistant when using /cplay
- Bot uses fixed emoji set
- Improved inline buttons with better error handling

### Auto-Delete & Cleanup
- Bot messages auto-delete after 5 seconds (configurable)
- Automatic cleanup when bot is removed from groups
- Automatic deletion of Telegram service messages after custom messages
- Voice chat service message features

### Playback Features
- LOOP functionality restored (61 lines)
- Shuffle command improvements (47 lines)
- Duration limit extended: **150 minutes → 300 minutes (5 hours)**
- Progress bar timer updates: 7 seconds → 20 seconds
- AUDIO ONLY support added
- Added blockquote support for text formatting

### Error Handling & Logging
- Enhanced error handling across all modules
- Better logging for debugging
- Bot runs cleanly without error spam
- TimeoutError handler added
- yt-dlp error handling improved
- Actual error messages now shown in logs

---

## 🔥 Breaking Changes

### Multi-Language Support Removed
- ⚠️ **Bot is now strictly English-only**
- Removed `/lang` command and all related configurations
- Deleted `si.json` and locale documentation
- Simplified codebase by removing language selection complexity

### Removed Features
- ❌ **Removed:** LOOP button (command still works via `/loop`)
- ❌ **Removed:** Multi-language support
- ❌ **Removed:** `/vplay` command (functionality merged into `/play`)
- ❌ **Removed:** Language switching system

---

## 📦 Infrastructure & Dependencies

### Dependency Updates
- **yt-dlp:** Updated to 2026.01.29 (latest)
- Updated requirements.txt with new dependencies
- Python package updates for stability

### Code Structure
- **New modules:**
  - `HasiiMusic/core/preload.py` (161 lines)
  - `HasiiMusic/helpers/_preload.py` (152 lines)
  - `HasiiMusic/plugins/admin-controles/gban.py` (168 lines)
  - `HasiiMusic/plugins/admin-controles/maintenance.py` (61 lines)
  - `HasiiMusic/plugins/admin-controles/restart.py` (76 lines)
  - `HasiiMusic/plugins/features/bots.py` (37 lines)
  - `HasiiMusic/plugins/features/groupdata.py` (126 lines)

- **Major refactors:**
  - `HasiiMusic/core/calls.py` (+640 lines)
  - `HasiiMusic/core/mongo.py` (+296 lines)
  - `HasiiMusic/core/youtube.py` (+236 lines)
  - `HasiiMusic/plugins/admin-controles/broadcast.py` (+275 lines)
  - `HasiiMusic/plugins/events/callbacks.py` (+337 lines)
  - `HasiiMusic/plugins/events/misc.py` (+173 lines)
  - `HasiiMusic/plugins/settings/blacklist.py` (+232 lines)

### Configuration
- Updated `config.py` with new configuration options
- Updated `sample.env` with correct environment variables
- Updated `.gitignore` to protect private features

---

## 🎯 Performance Improvements

- **FFmpeg optimization:** Better buffering and streaming quality
- **Memory optimization:** Fixed leaks, better resource management
- **Async improvements:** Tournament timer, file operations
- **Preload system:** Reduces track switching lag
- **Code cleanup:** Abstract preload feature, better error handling
- **Database optimization:** Improved MongoDB operations

---

## 🔐 Security & Stability

- Enhanced permission checking for voice chat operations
- Bot admin verification for sensitive commands
- Improved error handling prevents crashes
- Better handling of unauthorized operations
- Fixed multiple VPS crash scenarios

---

## 📝 Developer Notes

### Testing Recommendations
1. Test broadcast with formatted messages using `-copy` flag
2. Validate preload system with queue playback
3. Check all error handlers with edge cases
4. Test VPS deployment and long-running stability

### Migration Guide
- **Language files:** If you had custom language files, they're no longer supported. Bot is English-only now.
- **Loop button:** Use `/loop` command instead of the removed button.
- **/vplay:** Use `/play` for all playback (video play merged into play command).

---

## 🙏 Credits & Acknowledgments

- Based on AnonXMusic v3.0.1 features
- Community bug reports and testing
- All contributors who reported issues

---

## 📊 Statistics Summary

| Category | Count |
|----------|-------|
| **Commits** | 190 |
| **Files Changed** | 50 |
| **Lines Added** | +3,677 |
| **Lines Removed** | -1,011 |
| **Net Change** | +2,666 |
| **New Features** | 3 major |
| **Bug Fixes** | 45+ |
| **Enhancements** | 30+ |

---

## 🔗 Resources

- **Documentation:** See PROJECT_STRUCTURE.md for updated structure
- **Support:** @HasiiMusicBot

---

**Stay tuned for more ❤️ | @HasiiMusicBot**

*Released: February 7, 2026*

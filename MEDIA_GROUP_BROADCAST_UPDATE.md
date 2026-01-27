# Media Group (Album) Broadcast Support

## What Was Fixed

Previously, when using `/broadcast` to forward a **set of images/media** (album/media group), only the **first image** was broadcasted to all groups. Now the bot correctly broadcasts **all media in the album together**.

## Changes Made

### File: `HasiiMusic/plugins/admin-controles/broadcast.py`

1. **Added Media Group Detection**
   - Detects when replied message is part of a media group (album)
   - Automatically collects all media in the group

2. **Added `_get_media_group()` Function**
   - Searches for all messages with the same `media_group_id`
   - Returns sorted list of media messages in the album

3. **Updated Broadcast Logic**
   - **Priority 1**: If media group exists → send entire album
   - **Priority 2**: If single media → send single media
   - **Priority 3**: If text only → send text

4. **Support for Both Modes**
   - **Forward mode** (default): Forwards entire album with forward tag
   - **Copy mode** (`-copy` flag): Sends album without forward tag using `send_media_group()`

5. **FloodWait Retry Support**
   - Retry logic now handles media groups properly
   - Maintains album integrity even after flood wait

## How to Use

### Forward Album (with forward tag)
```
/broadcast (reply to any photo in an album)
```

### Send Album as Copy (no forward tag)
```
/broadcast -copy (reply to any photo in an album)
```

### Send Album to Groups and Users
```
/broadcast -user (reply to any photo in an album)
```

### Send Album and Pin
```
/broadcast -pin (reply to any photo in an album)
```

## Technical Details

- Uses `message.media_group_id` to detect albums
- Searches ±20 messages to find all media in the group
- Supports photos, videos, documents, and audio in albums
- Maintains correct order of media by sorting by message ID
- First media's caption is used (or provided text overrides it)
- Pinning works on the first message in the album

## Supported Media Types in Albums

✅ Photos  
✅ Videos  
✅ Documents  
✅ Audio files

## Notes

- Reply to **any photo/media in the album**, not necessarily the first one
- The bot will automatically find and collect all media in that album
- If fetching the media group fails, it falls back to sending just the replied message
- All existing flags (`-user`, `-nochat`, `-pin`, `-pinloud`, `-copy`) work with albums

---

**Date**: January 27, 2026  
**Status**: ✅ Implemented and Ready to Use

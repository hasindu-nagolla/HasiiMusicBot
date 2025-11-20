# ==============================================================================
# __main__.py - Main Entry Point for HasiiMusicBot
# ==============================================================================
# This is the main file that starts the bot. It performs the following:
# 1. Connects to the database
# 2. Starts the bot client
# 3. Starts assistant (userbot) clients
# 4. Loads all plugin modules
# 5. Initializes YouTube cookies if configured
# 6. Keeps the bot running until manually stopped
# ==============================================================================

import asyncio
import importlib

from pyrogram import idle

from HasiiMusic import (tune, app, config, db,
                   logger, stop, userbot, yt)
from HasiiMusic.plugins import all_modules


async def main():
    # Step 1: Connect to MongoDB database
    await db.connect()
    
    # Step 2: Start the main bot client
    await app.boot()
    
    # Step 3: Start assistant/userbot clients (for joining voice chats)
    await userbot.boot()
    
    # Step 4: Initialize voice call handler
    await tune.boot()

    # Step 5: Load all plugin modules (commands like /play, /pause, etc.)
    for module in all_modules:
        importlib.import_module(f"HasiiMusic.plugins.{module}")
    logger.info(f"🔌 Loaded {len(all_modules)} plugin modules.")

    # Step 6: Download YouTube cookies if URLs are provided (for age-restricted videos)
    if config.COOKIES_URL:
        await yt.save_cookies(config.COOKIES_URL)

    # Step 7: Load sudo users and blacklisted users from database
    sudoers = await db.get_sudoers()
    app.sudoers.update(sudoers)  # Add sudo users to filter
    app.bl_users.update(await db.get_blacklisted())  # Add blacklisted users to filter
    logger.info(f"👑 Loaded {len(app.sudoers)} sudo users.")
    logger.info("\n🎉 Bot started successfully! Ready to play music! 🎵\n")

    # Step 8: Keep the bot running (press Ctrl+C to stop)
    await idle()
    
    # Step 9: Cleanup and shutdown when bot is stopped
    await stop()


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass

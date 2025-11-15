import asyncio
import importlib

from pyrogram import idle

from HasiiMusic import (anon, app, config, db,
                   logger, stop, userbot, yt)
from HasiiMusic.plugins import all_modules


async def main():
    await db.connect()
    await app.boot()
    await userbot.boot()
    await anon.boot()

    for module in all_modules:
        importlib.import_module(f"HasiiMusic.plugins.{module}")
    logger.info(f"🔌 Loaded {len(all_modules)} modules.")

    if config.COOKIES_URL:
        await yt.save_cookies(config.COOKIES_URL)

    sudoers = await db.get_sudoers()
    app.sudoers.update(sudoers)
    app.bl_users.update(await db.get_blacklisted())
    logger.info(f"👑 Loaded {len(app.sudoers)} sudo users.")
    logger.info("\n🎉 Bot started successfully! Ready to play music! 🎵\n")

    await idle()
    await stop()


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass

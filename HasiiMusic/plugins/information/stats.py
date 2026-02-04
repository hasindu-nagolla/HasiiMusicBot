# ==============================================================================
# stats.py - Bot Statistics Command (Sudo Only)
# ==============================================================================
# This plugin shows comprehensive bot statistics and system information.
#
# Commands:
# - /stats - Show detailed bot statistics
#
# Displays:
# - Total users and groups using the bot
# - System info (OS, Python version, Pyrogram version)
# - Bot uptime
# - Memory and CPU usage
# - Number of loaded plugins
#
# Only sudo users can use this command.
# ==============================================================================

# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import os
import platform
import sys

import psutil
from pyrogram import __version__, filters, types
from pytgcalls import __version__ as pytgver

from HasiiMusic import app, config, db, lang, userbot
from HasiiMusic.plugins import all_modules


@app.on_message(filters.command(["stats"]) & ~app.bl_users)
@lang.language()
async def _stats(_, m: types.Message):
    # Check if user is sudo
    if m.from_user.id not in app.sudoers:
        return
    
    sent = await m.reply_photo(
        photo=config.PING_IMG,
        caption=m.lang["stats_fetching"],
    )

    pid = os.getpid()
    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_count = psutil.cpu_count()
    
    # Get memory info
    mem = psutil.virtual_memory()
    used_mem = round(mem.used / (1024 ** 3), 2)  # Convert to GB
    total_mem = round(mem.total / (1024 ** 3), 2)
    
    # Get disk info
    disk = psutil.disk_usage("/")
    used_disk = round(disk.used / (1024 ** 3), 2)  # Convert to GB
    total_disk = round(disk.total / (1024 ** 3), 2)
    
    _utext = m.lang["stats_user"].format(
        app.name,
        len(userbot.clients),
        config.AUTO_LEAVE,
        len(db.blacklisted),
        len(app.bl_users),
        len(app.sudoers),
        len(await db.get_chats()),
        len(await db.get_users()),
    )
    
    # Add system stats for sudo users
    _utext += m.lang["stats_sudo"].format(
        len(all_modules),
        platform.system(),
        f"{used_mem}GB | {total_mem}GB",
        f"{cpu_percent}% ({cpu_count} cores)",
        f"{used_disk}GB | {total_disk}GB",
        sys.version.split()[0],
        __version__,
        pytgver,
    )
    
    await sent.edit_caption(_utext)

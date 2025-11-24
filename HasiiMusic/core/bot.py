"""
# ==============================================================================
# bot.py - Main Bot Client Manager
# ==============================================================================
# This file defines the main Bot class that handles the Telegram bot client.
# Features:
# - Extends Pyrogram Client with custom bot functionality
# - Manages bot authentication and connection
# - Handles bot startup and shutdown procedures
# - Provides owner, logger, and sudo user filters
# - Stores bot information (ID, name, username, mention)
# ==============================================================================

"""Bot core module for HasiiMusicBot.

This module defines the main Bot class that extends Pyrogram's Client
with custom functionality for music bot operations.
"""

import pyrogram
from typing import Optional

from HasiiMusic import config, logger


class Bot(pyrogram.Client):
    """
    Main bot client class extending Pyrogram's Client.
    
    This class initializes the Telegram bot with proper configuration
    and provides methods for starting and stopping the bot.
    
    Attributes:
        owner (int): Owner's user ID
        logger (int): Logger group/channel ID
        bl_users (Filter): Filter for blacklisted users
        sudoers (Filter): Filter for sudo users (owner)
        id (int): Bot's user ID (set after boot)
        name (str): Bot's first name (set after boot)
        username (str): Bot's username (set after boot)
        mention (str): Bot's mention tag (set after boot)
    """
    
    def __init__(self):
        """Initialize the bot client with configuration settings."""
        super().__init__(
            name="HasiiMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            parse_mode=pyrogram.enums.ParseMode.HTML,
            max_concurrent_transmissions=7,
            link_preview_options=pyrogram.types.LinkPreviewOptions(is_disabled=True),
        )
        
        self.owner: int = config.OWNER_ID
        self.logger: int = config.LOGGER_ID
        self.bl_users: pyrogram.filters.Filter = pyrogram.filters.user()
        self.sudoers: pyrogram.filters.Filter = pyrogram.filters.user(self.owner)
        
        # These will be set after boot()
        self.id: Optional[int] = None
        self.name: Optional[str] = None
        self.username: Optional[str] = None
        self.mention: Optional[str] = None

    async def boot(self) -> None:
        """
        Start the bot and perform initial setup.
        
        This method:
        - Starts the Pyrogram client
        - Retrieves bot information
        - Verifies access to logger group
        - Checks bot admin status in logger group
        
        Raises:
            SystemExit: If bot cannot access logger group or is not an admin.
        """
        await super().start()
        
        # Set bot information
        self.id = self.me.id
        self.name = self.me.first_name
        self.username = self.me.username
        self.mention = self.me.mention
        
        # Verify logger group access
        try:
            await self.send_message(self.logger, "🤖 Bot Started")
            member = await self.get_chat_member(self.logger, self.id)
        except Exception as ex:
            raise SystemExit(
                f"❌ Bot failed to access logger group: {self.logger}\n"
                f"Reason: {ex}\n"
                f"Please ensure the bot is added to the logger group."
            )
        
        # Verify admin status
        if member.status != pyrogram.enums.ChatMemberStatus.ADMINISTRATOR:
            raise SystemExit(
                f"❌ Bot is not an administrator in logger group: {self.logger}\n"
                f"Please promote the bot to administrator with necessary permissions."
            )
        
        logger.info(f"🤖 Bot started successfully as @{self.username}")

    async def exit(self) -> None:
        """
        Gracefully stop the bot client.
        
        This method stops the Pyrogram client and logs the shutdown.
        """
        await super().stop()
        logger.info("🤖 Bot client stopped.")

# ==============================================================================
# userbot.py - Assistant/Userbot Client Manager
# ==============================================================================
# This file manages assistant accounts (userbots) that join voice chats to play music.
# Assistants are user accounts (not bots) that can join and stream audio/video.
# You can configure up to 3 assistants using SESSION1, SESSION2, SESSION3 variables.
# ==============================================================================

from pyrogram import Client

from HasiiMusic import config, logger


class Userbot(Client):
    def __init__(self):
        """
        Initialize userbot with multiple assistant clients.
        
        Creates up to 3 assistant clients based on available session strings.
        Each assistant can independently join voice chats and stream music.
        More assistants = ability to serve more groups simultaneously.
        """
        self.clients = []  # List to store all active assistant clients
        
        # Map of client names to their session string config keys
        clients = {"one": "SESSION1", "two": "SESSION2", "three": "SESSION3"}
        
        # Create a Pyrogram client for each configured session
        for key, string_key in clients.items():
            name = f"HasiiTuneUB{key[-1]}"  # Unique name: HasiiTuneUB1, HasiiTuneUB2, etc.
            session = getattr(config, string_key)  # Get session string from config
            
            # Create and attach the client as an attribute (self.one, self.two, self.three)
            setattr(
                self,
                key,
                Client(
                    name=name,
                    api_id=config.API_ID,
                    api_hash=config.API_HASH,
                    session_string=session,  # Pyrogram session string
                ),
            )

    async def boot_client(self, num: int, ub: Client):
        """
        Boot a client and perform initial setup.
        Args:
            num (int): The client number to boot (1, 2, or 3).
            ub (Client): The userbot client instance.
        Raises:
            SystemExit: If the client fails to send a message in the log group.
        """
        clients = {
            1: self.one,
            2: self.two,
            3: self.three,
        }
        client = clients[num]
        try:
            await client.start()
        except Exception as e:
            logger.error(f"❌ Assistant {num} failed to start: {e}")
            return  # Don't raise SystemExit, just skip this assistant
        
        try:
            await client.send_message(config.LOGGER_ID, f"Assistant {num} Started")
        except Exception as e:
            logger.warning(f"⚠️ Assistant {num} couldn't send message to logger: {e}")
            # Continue anyway - this is not critical

        client.id = client.me.id if hasattr(client, 'me') and client.me else None
        client.name = client.me.first_name if hasattr(client, 'me') and client.me else f"Assistant{num}"
        client.username = client.me.username if hasattr(client, 'me') and client.me else None
        client.mention = client.me.mention if hasattr(client, 'me') and client.me else client.name
        self.clients.append(client)
        logger.info(f"👤 Assistant {num} started as @{client.username}")

    async def boot(self):
        """
        Asynchronously starts the assistants.
        """
        if config.SESSION1:
            await self.boot_client(1, self.one)
        if config.SESSION2:
            await self.boot_client(2, self.two)
        if config.SESSION3:
            await self.boot_client(3, self.three)

    async def exit(self):
        """
        Asynchronously stops the assistants.
        """
        if config.SESSION1:
            await self.one.stop()
        if config.SESSION2:
            await self.two.stop()
        if config.SESSION3:
            await self.three.stop()
        logger.info("Assistants stopped.")

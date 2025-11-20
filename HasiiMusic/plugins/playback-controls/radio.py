# ==============================================================================
# radio.py - Live Radio Streaming Plugin
# ==============================================================================
# This plugin allows users to stream live radio stations in voice chats.
# Features:
# - 50+ international and local radio stations
# - Pagination for easy station selection
# - Live timer display during playback
# - Admin-only controls (skip, close)
# - Support for both regular and channel play modes
# ==============================================================================

import asyncio
import logging
import time

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from HasiiMusic import tune, app, config, db, lang, queue
from HasiiMusic.helpers import buttons, utils
from HasiiMusic.helpers._admins import is_admin

# Set up logging
LOGGER = logging.getLogger(__name__)

# Dictionary of radio stations with their stream URLs
RADIO_STATION = {
    "SirasaFM": "http://live.trusl.com:1170/;",
    "HelaNadaFM": "https://stream-176.zeno.fm/9ndoyrsujwpvv",
    "Radio Plus Hitz": "https://altair.streamerr.co/stream/8054",
    "English": "https://hls-01-regions.emgsound.ru/11_msk/playlist.m3u8",
    "HiruFM": "https://radio.lotustechnologieslk.net:2020/stream/hirufmgarden?1707015384",
    "RedFM": "https://shaincast.caster.fm:47830/listen.mp3",
    "RanFM": "https://207.148.74.192:7874/ran.mp3",
    "YFM": "http://live.trusl.com:1180/;",
    "+212": "http://stream.radio.co/sf55ced545/listen",
    "Deep House Music": "http://live.dancemusic.ro:7000/",
    "Radio Italia": "https://energyitalia.radioca.st",
    "The Best Music": "http://s1.slotex.pl:7040/",
    "HITZ FM": "https://stream-173.zeno.fm/uyx7eqengijtv",
    "Prime Radio HD": "https://stream-153.zeno.fm/oksfm5djcfxvv",
    "1Mix Radio": "https://stream-154.zeno.fm/xdf9ba0vyz8uv",
    "RFI Tieng Viet": "https://rfivietnamien96k.ice.infomaniak.ch/rfivietnamien-96k.mp3",
    "Phat": "https://phat.stream.laut.fm/phat",
    "Dai Phat Thanh VN": "http://c13.radioboss.fm:8127/stream",
    "Pulse EDM": "https://naxos.cdnstream.com/1373_128",
    "Base Music": "https://base-music.stream.laut.fm/base-music",
    "Ultra Music": "http://prem4.di.fm/umfradio_hi?20a1d1bf879e76&_ic2=1733161375677",
    "Na Dahasa FM": "https://stream-155.zeno.fm/z7q96fbw7rquv",
    "Parani Gee": "http://cast2.citrus3.com:8288/;",
    "SunFM": "https://radio.lotustechnologieslk.net:2020/stream/sunfmgarden",
    "EDM MEGASHUFFLE": "https://maggie.torontocast.com:9030/stream",
}


def radio_buttons(page=0, per_page=5):
    """Generate pagination buttons for radio stations."""
    stations = sorted(RADIO_STATION.keys())
    total_pages = (len(stations) - 1) // per_page + 1
    start = page * per_page
    end = start + per_page
    current_stations = stations[start:end]

    buttons_list = [
        [InlineKeyboardButton(name, callback_data=f"station_{name}")]
        for name in current_stations
    ]

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            "◀️ Back", callback_data=f"page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(
            "Next ▶️", callback_data=f"page_{page+1}"))

    if nav_buttons:
        buttons_list.append(nav_buttons)

    buttons_list.append([InlineKeyboardButton(
        "ℹ️ Help", callback_data=f"radio_help_{page}")])

    return InlineKeyboardMarkup(buttons_list)


async def is_admin_or_anonymous(chat_id, user_id):
    """Check if user is admin or anonymous admin."""
    if user_id == 1087968824:  # Anonymous admin ID
        return True
    member = await app.get_chat_member(chat_id, user_id)
    return member.status in ["administrator", "creator"]


async def update_timer(chat_id, message_id, station_name, start_time):
    """Update the timer on the radio message."""
    last_timer = None
    while True:
        try:
            elapsed = int(time.time() - start_time)
            mins, secs = divmod(elapsed, 60)
            timer = f"{mins:02d}:{secs:02d}"

            # Only update if timer has changed
            if timer != last_timer:
                await app.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=f"📻 Now playing: {station_name}\n⏱️ Time: {timer}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(
                            f"🎵 {station_name}", callback_data="noop")],
                        [
                            InlineKeyboardButton(
                                "🔀 Stations", callback_data="skip_radio"),
                            InlineKeyboardButton(
                                "❌ Close", callback_data="close_message")
                        ]
                    ])
                )
                last_timer = timer
        except Exception as e:
            # Silently ignore MESSAGE_NOT_MODIFIED and similar errors
            if "MESSAGE_NOT_MODIFIED" not in str(e):
                LOGGER.debug(f"Timer update error: {e}")
            break
        await asyncio.sleep(1)


@app.on_message(
    filters.command(["radio", "cradio"])
    & filters.group
    & ~app.bl_users
)
@lang.language()
async def radio_handler(_, m: Message) -> None:
    """Handle radio command."""
    chat_id = m.chat.id
    cplay = m.command[0] == "cradio"

    if cplay:
        channel_id = await db.get_cmode(m.chat.id)
        if channel_id is None:
            return await m.reply_text(
                "❌ Channel play is not enabled.\n\n"
                "To enable for linked channel:\n"
                "`/channelplay linked`\n\n"
                "To enable for any channel:\n"
                "`/channelplay [channel_id]`"
            )
        try:
            chat = await app.get_chat(channel_id)
            chat_id = chat.id
        except:
            return await m.reply_text(
                "❌ Channel not found or bot is not in the channel.\n"
                "Please make sure the channel ID is correct and the bot is added correctly."
            )

    await m.reply_text(
        "📻 Select a radio station to play:",
        reply_markup=radio_buttons(page=0),
    )


@app.on_callback_query(filters.regex(r"^page_"))
async def on_page_change(_, callback_query):
    """Handle pagination."""
    page = int(callback_query.data.split("_")[1])
    await callback_query.message.edit_reply_markup(radio_buttons(page=page))


@app.on_callback_query(filters.regex(r"^station_"))
async def on_station_select(_, callback_query):
    """Handle station selection and start playback."""
    station_name = callback_query.data.split("station_")[1]
    RADIO_URL = RADIO_STATION.get(station_name)

    if not RADIO_URL:
        return await callback_query.answer("❌ Invalid station name.", show_alert=True)

    chat_id = callback_query.message.chat.id

    # Check if radio is already playing - only admins can switch
    if await db.get_call(chat_id):
        # Check if user is admin
        if not await is_admin(chat_id, callback_query.from_user.id):
            return await callback_query.answer(
                "❌ Only admins can change the station while radio is playing.\n"
                "Please wait for the current session to end.",
                show_alert=True
            )

    await callback_query.answer("🔄 Switching station...")

    mention = callback_query.from_user.mention if callback_query.from_user.id != 1087968824 else "Anonymous Admin"

    # Delete the station selection message if it exists
    try:
        await callback_query.message.delete()
    except:
        pass

    mystic = await app.send_photo(
        chat_id=chat_id,
        photo=config.START_IMG,
        caption=f"📻 Now playing: {station_name}\n⏱️ Time: 00:00",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🎵 {station_name}", callback_data="noop")],
            [
                InlineKeyboardButton("🔀 Stations", callback_data="skip_radio"),
                InlineKeyboardButton("❌ Close", callback_data="close_message")
            ]
        ])
    )

    start_time = time.time()
    asyncio.create_task(update_timer(
        chat_id, mystic.id, station_name, start_time))

    # Create a file object for radio stream
    class RadioFile:
        def __init__(self, url, title):
            self.url = url
            self.title = title
            self.is_live = True
            self.duration = "Live Stream"
            self.duration_sec = 0
            self.file_path = url  # Use URL as file path for streaming
            self.id = url
            self.message_id = mystic.id
            self.user = mention
            self.thumb = config.START_IMG
            self.video = False  # Audio only for radio

    file = RadioFile(RADIO_URL, f"📻 {station_name}")

    # Check if already playing - switch to new station immediately
    if await db.get_call(chat_id):
        # Clear queue and stop current playback
        queue.clear(chat_id)
        try:
            await tune.stop_stream(chat_id)
        except:
            pass

    # Add new station to queue
    position = queue.add(chat_id, file)

    # Play the stream
    try:
        await tune.play_media(chat_id=chat_id, message=mystic, media=file)
    except Exception as e:
        await mystic.edit_caption(f"❌ Error playing radio:\n{str(e)}")
        LOGGER.error(f"Radio play error: {e}")


@app.on_callback_query(filters.regex(r"^skip_radio"))
async def skip_radio_callback(_, callback_query):
    """Handle skip radio button - show station list."""
    # Anyone can browse stations, not just admins
    await callback_query.answer()
    await callback_query.message.reply_text(
        "📻 Select another radio station:",
        reply_markup=radio_buttons(page=0)
    )


@app.on_callback_query(filters.regex(r"^close_message"))
async def close_message_callback(_, callback_query):
    """Handle close button."""
    try:
        # Check if user has permission to delete
        member = await app.get_chat_member(callback_query.message.chat.id, callback_query.from_user.id)
        if member.status in ["administrator", "creator"] or callback_query.from_user.id == 1087968824:
            await callback_query.message.delete()
            await callback_query.answer()
        else:
            await callback_query.answer("❌ Only group admins can close this message.", show_alert=True)
    except Exception as e:
        await callback_query.answer(f"❌ Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^radio_help_"))
async def on_radio_help(_, callback_query):
    """Show help message."""
    await callback_query.answer()
    page = int(callback_query.data.split("_")[2])
    help_text = (
        "📻 Radio Plugin Help\n\n"
        "English:\n"
        "• Type `/radio`: Open station list\n"
        "• Select a station using buttons\n"
        "• Use `/stop`: Stop playback\n"
        "සිංහල:\n"
        "• සිංදු අහන්න පටන් ගන්න `/radio` ටයිප් කරලා ස්ටේෂන් එකක් තෝරගන්න.\n"
        "• වෙන චැනල් එකක් ඕනෙනම් Stations බටන් එක ඔබන්න.\n"
        "• අහලා ඉවරනම් `/stop` කරන්න.\n"
    )
    await callback_query.message.edit_text(
        help_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Stations",
                                  callback_data=f"back_to_stations_{page}")]
        ])
    )


@app.on_callback_query(filters.regex(r"^back_to_stations_"))
async def on_back_to_stations(_, callback_query):
    """Return to station list."""
    await callback_query.answer()
    page = int(callback_query.data.split("_")[-1])
    await callback_query.message.edit_text(
        "📻 Select a radio station to play:",
        reply_markup=radio_buttons(page=page)
    )


@app.on_callback_query(filters.regex(r"^noop"))
async def on_noop(_, callback_query):
    """Handle no-operation button."""
    await callback_query.answer("🎵 Enjoying the music!", show_alert=False)

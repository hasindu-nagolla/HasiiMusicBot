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

from pyrogram import enums, errors, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from HasiiMusic import tune, app, config, db, lang, queue
from HasiiMusic.helpers import buttons, utils

# Set up logging
LOGGER = logging.getLogger(__name__)

# Dictionary of radio stations with their stream URLs
RADIO_STATION = {
    # --- Sri Lankan Radio Stations ---
    "SLBC Radio": "http://220.247.227.20:8000/RSLstream",
    "Siyatha FM": "https://srv01.onlineradio.voaplus.com/siyathafm",
    "ITN FM": "https://cp12.serverse.com/proxy/itnfm/stream",
    "Rhythm FM": "https://srv01.onlineradio.voaplus.com/rhythmfm",
    "Kothmale FM": "https://s46.myradiostream.com:11156/listen.mp3",
    "Colour Radio": "https://stream.zeno.fm/uo3gmts0ilivv",
    "Free FM": "https://stream.zeno.fm/1tcs4fbw7rquv",
    "Seth FM": "https://listen.radioking.com/radio/384487/stream/435781",
    "V FM": "https://dc1.serverse.com/proxy/fmlanka/stream",
    "Sirasa FM": "http://live.trusl.com:1170/",                                          # ✅
    "Hiru FM": "https://radio.lotustechnologieslk.net:2020/stream/hirufmgarden",         # ✅
    "Y FM": "http://live.trusl.com:1180/",                                               # ✅
    "Shaa FM": "https://radio.lotustechnologieslk.net:2020/stream/shaafmgarden",         # ✅
    "Gold FM": "https://radio.lotustechnologieslk.net:2020/stream/goldfmgarden",         # ✅
    "Sooriyan FM": "https://radio.lotustechnologieslk.net:2020/stream/sooriyanfmgarden",  # ✅
    "bestcoast.fm": "https://streams.radio.co/sea5dddd6b/listen",                        # ✅
    "Yes FM": "http://live.trusl.com:1160/",                                             # ✅
    "Sitha FM": "https://stream.streamgenial.stream/cdzzrkrv0p8uv",                      # ✅
    "Hiru FM Garden": "https://radio.lotustechnologieslk.net:2020/stream/hirufmgarden",  # ✅
    "Sun FM": "https://radio.lotustechnologieslk.net:2020/stream/sunfmgarden",           # ✅
    "Shree FM": "https://streamingv2.shoutcast.com/shreefm945",                          # ✅
    "Red FM": "https://shaincast.caster.fm:47830/listen.mp3",                            # ✅
    "Ran FM": "https://207.148.74.192:7874/ran.mp3",                                     # ✅
    "Neth FM": "https://cp11.serverse.com/proxy/nethfm/stream",                          # ✅
    "Kiss FM": "https://srv01.onlineradio.voaplus.com/kissfm",                           # ✅
    "Rangiri FM": "https://stream.streamgenial.stream/hwafmr3f4p8uv",                    # ✅
    "Lakhanada Radio": "https://cp12.serverse.com/proxy/itnfm?mp=/stream",               # ✅
    "HITZ FM": "https://stream-173.zeno.fm/uyx7eqengijtv",                               # ✅
    "Na Dahasa FM": "https://stream-155.zeno.fm/z7q96fbw7rquv",                          # ✅
    "Parani Gee": "http://cast2.citrus3.com:8288/",                                      # ✅
    "Deep House Music": "http://live.dancemusic.ro:7000/",                               # ✅
    "Base Music": "https://base-music.stream.laut.fm/base-music",                        # ✅
    "Pulse EDM": "https://naxos.cdnstream.com/1373_128",                                 # ✅

}


def radio_buttons(page=0, per_page=10):
    """Generate pagination buttons for radio stations."""
    stations = sorted(RADIO_STATION.keys())
    total_pages = (len(stations) - 1) // per_page + 1
    start = page * per_page
    end = start + per_page
    current_stations = stations[start:end]

    # Create buttons in rows of 2
    buttons_list = []
    for i in range(0, len(current_stations), 2):
        row = []
        # Add first button in the row
        row.append(InlineKeyboardButton(
            current_stations[i], callback_data=f"station_{current_stations[i]}"))
        # Add second button if it exists
        if i + 1 < len(current_stations):
            row.append(InlineKeyboardButton(
                current_stations[i + 1], callback_data=f"station_{current_stations[i + 1]}"))
        buttons_list.append(row)

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


async def has_radio_control_permission(chat_id, user_id):
    """
    Check if user has permission to control radio.
    Allowed users:
    - Bot owner
    - Sudo users
    - Authorized users in the chat
    - Chat admins
    - Anonymous admins
    """
    # Check if anonymous admin
    if user_id == 1087968824:
        return True

    # Check if bot owner
    if user_id == config.OWNER_ID:
        return True

    # Check if sudo user
    if user_id in app.sudoers:
        return True

    # Check if authorized user in this chat
    if await db.is_auth(chat_id, user_id):
        return True

    # Check if chat admin
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False


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
                    caption=f"📻 𝗡𝗼𝘄 𝗽𝗹𝗮𝘆𝗶𝗻𝗴: {station_name}\n⏱️ 𝗧𝗶𝗺𝗲: {timer}",
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
                "❌ 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗽𝗹𝗮𝘆 𝗶𝘀 𝗻𝗼𝘁 𝗲𝗻𝗮𝗯𝗹𝗲𝗱.\n\n"
                "𝗧𝗼 𝗲𝗻𝗮𝗯𝗹𝗲 𝗳𝗼𝗿 𝗹𝗶𝗻𝗸𝗲𝗱 𝗰𝗵𝗮𝗻𝗻𝗲𝗹:\n"
                "`/channelplay linked`\n\n"
                "𝗧𝗼 𝗲𝗻𝗮𝗯𝗹𝗲 𝗳𝗼𝗿 𝗮𝗻𝘆 𝗰𝗵𝗮𝗻𝗻𝗲𝗹:\n"
                "`/channelplay [channel_id]`"
            )
        try:
            chat = await app.get_chat(channel_id)
            chat_id = chat.id
        except:
            return await m.reply_text(
                "❌ 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱 𝗼𝗿 𝗯𝗼𝘁 𝗶𝘀 𝗻𝗼𝘁 𝗶𝗻 𝘁𝗵𝗲 𝗰𝗵𝗮𝗻𝗻𝗲𝗹.\n"
                "𝗣𝗹𝗲𝗮𝘀𝗲 𝗺𝗮𝗸𝗲 𝘀𝘂𝗿𝗲 𝘁𝗵𝗲 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝗜𝗗 𝗶𝘀 𝗰𝗼𝗿𝗿𝗲𝗰𝘁 𝗮𝗻𝗱 𝘁𝗵𝗲 𝗯𝗼𝘁 𝗶𝘀 𝗮𝗱𝗱𝗲𝗱 𝗰𝗼𝗿𝗿𝗲𝗰𝘁𝗹𝘆."
            )

    await m.reply_text(
        "📻 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮 𝗿𝗮𝗱𝗶𝗼 𝘀𝘁𝗮𝘁𝗶𝗼𝗻 𝘁𝗼 𝗽𝗹𝗮𝘆:",
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
        return await callback_query.answer("❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝘀𝘁𝗮𝘁𝗶𝗼𝗻 𝗻𝗮𝗺𝗲.", show_alert=True)

    chat_id = callback_query.message.chat.id

    # Check if radio is already playing - only authorized users can switch
    if await db.get_call(chat_id):
        # Check if user has permission
        if not await has_radio_control_permission(chat_id, callback_query.from_user.id):
            return await callback_query.answer(
                "❌ 𝗢𝗻𝗹𝘆 𝗮𝗱𝗺𝗶𝗻𝘀, 𝗯𝗼𝘁 𝗼𝘄𝗻𝗲𝗿, 𝘀𝘂𝗱𝗼 𝘂𝘀𝗲𝗿𝘀, 𝗼𝗿 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘂𝘀𝗲𝗿𝘀 𝗰𝗮𝗻 𝗰𝗵𝗮𝗻𝗴𝗲 𝘁𝗵𝗲 𝘀𝘁𝗮𝘁𝗶𝗼𝗻 𝘄𝗵𝗶𝗹𝗲 𝗿𝗮𝗱𝗶𝗼 𝗶𝘀 𝗽𝗹𝗮𝘆𝗶𝗻𝗴.\n"
                "𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁 𝗳𝗼𝗿 𝘁𝗵𝗲 𝗰𝘂𝗿𝗿𝗲𝗻𝘁 𝘀𝗲𝘀𝘀𝗶𝗼𝗻 𝘁𝗼 𝗲𝗻𝗱.",
                show_alert=True
            )

    # If assistant is not in the group, invite them before playing
    if chat_id not in db.active_calls:
        client = await db.get_client(chat_id)
        try:
            member = await app.get_chat_member(chat_id, client.id)
            if member.status in [
                enums.ChatMemberStatus.BANNED,
                enums.ChatMemberStatus.RESTRICTED,
            ]:
                try:
                    await app.unban_chat_member(chat_id=chat_id, user_id=client.id)
                except:
                    return await callback_query.answer(
                        f"❌ 𝗔𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁 {client.mention} 𝗶𝘀 𝗯𝗮𝗻𝗻𝗲𝗱!\n"
                        f"𝗨𝗻𝗯𝗮𝗻 𝗮𝗻𝗱 𝘁𝗿𝘆 𝗮𝗴𝗮𝗶𝗻.",
                        show_alert=True
                    )
        except errors.ChatAdminRequired:
            return await callback_query.answer(
                "❌ 𝗠𝗮𝗸𝗲 𝗺𝗲 𝗮𝗱𝗺𝗶𝗻 𝘁𝗼 𝗶𝗻𝘃𝗶𝘁𝗲 𝗮𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁!",
                show_alert=True
            )
        except errors.UserNotParticipant:
            # Assistant not in group - invite them
            if callback_query.message.chat.username:
                invite_link = callback_query.message.chat.username
                try:
                    await client.resolve_peer(invite_link)
                except:
                    pass
            else:
                try:
                    invite_link = (await app.get_chat(chat_id)).invite_link
                    if not invite_link:
                        invite_link = await app.export_chat_invite_link(chat_id)
                except errors.ChatAdminRequired:
                    return await callback_query.answer(
                        "❌ 𝗠𝗮𝗸𝗲 𝗺𝗲 𝗮𝗱𝗺𝗶𝗻 𝘁𝗼 𝗶𝗻𝘃𝗶𝘁𝗲 𝗮𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁!",
                        show_alert=True
                    )
                except Exception as ex:
                    return await callback_query.answer(
                        f"❌ 𝗘𝗿𝗿𝗼𝗿: {type(ex).__name__}",
                        show_alert=True
                    )

            await callback_query.answer("🔄 𝗜𝗻𝘃𝗶𝘁𝗶𝗻𝗴 𝗮𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁...")
            await asyncio.sleep(1)

            try:
                await client.join_chat(invite_link)
            except errors.UserAlreadyParticipant:
                pass
            except errors.InviteRequestSent:
                try:
                    await app.approve_chat_join_request(chat_id, client.id)
                except Exception as ex:
                    return await callback_query.answer(
                        f"❌ 𝗘𝗿𝗿𝗼𝗿: {type(ex).__name__}",
                        show_alert=True
                    )
            except Exception as ex:
                return await callback_query.answer(
                    f"❌ 𝗘𝗿𝗿𝗼𝗿: {type(ex).__name__}",
                    show_alert=True
                )

            await client.resolve_peer(chat_id)

    await callback_query.answer("🔄 𝗦𝘄𝗶𝘁𝗰𝗵𝗶𝗻𝗴 𝘀𝘁𝗮𝘁𝗶𝗼𝗻...")

    mention = callback_query.from_user.mention if callback_query.from_user.id != 1087968824 else "𝗔𝗻𝗼𝗻𝘆𝗺𝗼𝘂𝘀 𝗔𝗱𝗺𝗶𝗻"

    # Keep the station selection message visible - don't delete it
    # Users can continue selecting stations from the same button list

    mystic = await app.send_photo(
        chat_id=chat_id,
        photo=config.RADIO_IMG,
        caption=f"📻 𝗡𝗼𝘄 𝗽𝗹𝗮𝘆𝗶𝗻𝗴: {station_name}\n⏱️ 𝗧𝗶𝗺𝗲: 00:00",
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
            self.duration = "𝗟𝗶𝘃𝗲 𝗦𝘁𝗿𝗲𝗮𝗺"
            self.duration_sec = 0
            self.file_path = url  # Use URL as file path for streaming
            self.id = url
            self.message_id = mystic.id
            self.user = mention
            self.thumb = config.RADIO_IMG
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
        await mystic.edit_caption(f"❌ 𝗘𝗿𝗿𝗼𝗿 𝗽𝗹𝗮𝘆𝗶𝗻𝗴 𝗿𝗮𝗱𝗶𝗼:\n{str(e)}")
        LOGGER.error(f"Radio play error: {e}")


@app.on_callback_query(filters.regex(r"^skip_radio"))
async def skip_radio_callback(_, callback_query):
    """Handle skip radio button - show station list."""
    # Anyone can browse stations, not just admins
    await callback_query.answer()
    await callback_query.message.reply_text(
        "📻 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮𝗻𝗼𝘁𝗵𝗲𝗿 𝗿𝗮𝗱𝗶𝗼 𝘀𝘁𝗮𝘁𝗶𝗼𝗻:",
        reply_markup=radio_buttons(page=0)
    )


@app.on_callback_query(filters.regex(r"^close_message"))
async def close_message_callback(_, callback_query):
    """Handle close button."""
    try:
        # Check if user has permission to delete
        if await has_radio_control_permission(callback_query.message.chat.id, callback_query.from_user.id):
            await callback_query.message.delete()
            await callback_query.answer()
        else:
            await callback_query.answer(
                "❌ 𝗢𝗻𝗹𝘆 𝗮𝗱𝗺𝗶𝗻𝘀, 𝗯𝗼𝘁 𝗼𝘄𝗻𝗲𝗿, 𝘀𝘂𝗱𝗼 𝘂𝘀𝗲𝗿𝘀, 𝗼𝗿 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘂𝘀𝗲𝗿𝘀 𝗰𝗮𝗻 𝗰𝗹𝗼𝘀𝗲 𝘁𝗵𝗶𝘀 𝗺𝗲𝘀𝘀𝗮𝗴𝗲.",
                show_alert=True
            )
    except Exception as e:
        await callback_query.answer(f"❌ 𝗘𝗿𝗿𝗼𝗿: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^radio_help_"))
async def on_radio_help(_, callback_query):
    """Show help message."""
    await callback_query.answer()
    page = int(callback_query.data.split("_")[2])
    help_text = (
        "<blockquote>📻 𝗥𝗮𝗱𝗶𝗼 𝗣𝗹𝘂𝗴𝗶𝗻 𝗛𝗲𝗹𝗽</blockquote>\n\n"
        "<blockquote><b>𝗘𝗻𝗴𝗹𝗶𝘀𝗵:</b>\n"
        "• 𝗧𝘆𝗽𝗲 `/radio`𝘁𝗼 𝗢𝗽𝗲𝗻 𝘀𝘁𝗮𝘁𝗶𝗼𝗻 𝗹𝗶𝘀𝘁\n"
        "• 𝗨𝘀𝗲 `/stop`𝘁𝗼 𝗦𝘁𝗼𝗽 𝗽𝗹𝗮𝘆𝗯𝗮𝗰𝗸 </blockquote>"
        "<blockquote><b>සිංහල:</b>\n"
        "<b>• `/radio` ටයිප් කරලා ස්ටේෂන් එකක් තෝරගන්න.</b>\n"
        "<b>• අහලා ඉවරනම් `/stop` කරන්න.</b> </blockquote>"
    )
    await callback_query.message.edit_text(
        help_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 𝗕𝗮𝗰𝗸 𝘁𝗼 𝗦𝘁𝗮𝘁𝗶𝗼𝗻𝘀",
                                  callback_data=f"back_to_stations_{page}")]
        ])
    )


@app.on_callback_query(filters.regex(r"^back_to_stations_"))
async def on_back_to_stations(_, callback_query):
    """Return to station list."""
    await callback_query.answer()
    page = int(callback_query.data.split("_")[-1])
    await callback_query.message.edit_text(
        "📻 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮 𝗿𝗮𝗱𝗶𝗼 𝘀𝘁𝗮𝘁𝗶𝗼𝗻 𝘁𝗼 𝗽𝗹𝗮𝘆:",
        reply_markup=radio_buttons(page=page)
    )


@app.on_callback_query(filters.regex(r"^noop"))
async def on_noop(_, callback_query):
    """Handle no-operation button."""
    await callback_query.answer("🎵 𝗘𝗻𝗷𝗼𝘆𝗶𝗻𝗴 𝘁𝗵𝗲 𝗺𝘂𝘀𝗶𝗰!", show_alert=False)

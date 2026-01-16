# ==============================================================================
# _play.py - Play Command Helper & Validator
# ==============================================================================
# This file contains the @checkUB decorator used by play commands.
# Validates:
# - User permissions (only real users, not anonymous admins)
# - Chat type (only supergroups)
# - Command syntax (query or reply required)
# - Queue limits
# - YouTube URL validity
#
# This decorator ensures all play commands have proper validation before execution.
# ==============================================================================

import asyncio

from pyrogram import enums, errors, types

from HasiiMusic import app, config, db, queue, yt


def checkUB(play):
    async def wrapper(_, m: types.Message):
        async def safe_reply(text):
            """Safely send reply, return None if chat doesn't allow messages"""
            try:
                return await m.reply_text(text)
            except (errors.ChatWriteForbidden, errors.ChatSendPlainForbidden):
                # Chat doesn't allow text messages - silently return
                return None
            except Exception:
                return None
        
        if not m.from_user:
            await safe_reply(m.lang["play_user_invalid"])
            return

        if m.chat.type != enums.ChatType.SUPERGROUP:
            await safe_reply(m.lang["play_chat_invalid"])
            return await app.leave_chat(m.chat.id)

        if not m.reply_to_message and (
            len(m.command) < 2 or (len(m.command)
                                   == 2 and m.command[1] == "-f")
        ):
            await safe_reply(m.lang["play_usage"])
            return

        if len(queue.get_queue(m.chat.id)) >= config.QUEUE_LIMIT:
            await safe_reply(m.lang["play_queue_full"].format(config.QUEUE_LIMIT))
            return

        force = m.command[0].endswith("force") or (
            len(m.command) > 1 and "-f" in m.command[1]
        )
        cplay = m.command[0][0] == "c"
        
        url = yt.url(m)
        # Only validate URL if not replying to media (Telegram files have t.me URLs)
        if url and not m.reply_to_message and not yt.valid(url):
            return await m.reply_text(m.lang["play_unsupported"])

        play_mode = await db.get_play_mode(m.chat.id)
        if play_mode or force:
            adminlist = await db.get_admins(m.chat.id)
            if (
                m.from_user.id not in adminlist
                and not await db.is_auth(m.chat.id, m.from_user.id)
                and not m.from_user.id in app.sudoers
            ):
                await safe_reply(m.lang["play_admin"])
                return

        if m.chat.id not in db.active_calls:
            client = await db.get_client(m.chat.id)
            try:
                member = await app.get_chat_member(m.chat.id, client.id)
                if member.status in [
                    enums.ChatMemberStatus.BANNED,
                    enums.ChatMemberStatus.RESTRICTED,
                ]:
                    try:
                        await app.unban_chat_member(
                            chat_id=m.chat.id, user_id=client.id
                        )
                    except:
                        await safe_reply(
                            m.lang["play_banned"].format(
                                app.name,
                                client.id,
                                client.mention,
                                f"@{client.username}" if client.username else None,
                            )
                        )
                        return
            except errors.ChatAdminRequired:
                await safe_reply(
                    f"<blockquote><b>🔐 Bot Admin Required</b></blockquote>\n\n"
                    f"<blockquote>To play music in this chat, I need to be an <b>administrator</b>.\n\n"
                    f"<b>Required permissions:</b>\n"
                    f"• Manage Voice Chats\n"
                    f"• Invite Users via Link\n"
                    f"• Delete Messages\n\n"
                    f"Please promote me as admin with the required permissions.</blockquote>"
                )
                return
            except errors.UserNotParticipant:
                if m.chat.username:
                    invite_link = m.chat.username
                    try:
                        await client.resolve_peer(invite_link)
                    except:
                        pass
                else:
                    try:
                        invite_link = (await app.get_chat(m.chat.id)).invite_link
                        if not invite_link:
                            invite_link = await app.export_chat_invite_link(m.chat.id)
                    except errors.ChatAdminRequired:
                        await safe_reply(
                            f"<blockquote><b>🔐 Bot Admin Required</b></blockquote>\n\n"
                            f"<blockquote>To play music in this chat, I need to be an <b>administrator</b>.\n\n"
                            f"<b>Required permissions:</b>\n"
                            f"• Manage Voice Chats\n"
                            f"• Invite Users via Link\n"
                            f"• Delete Messages\n\n"
                            f"Please promote me as admin with the required permissions.</blockquote>"
                        )
                        return
                    except Exception as ex:
                        await safe_reply(
                            m.lang["play_invite_error"].format(
                                type(ex).__name__)
                        )
                        return

                umm = await safe_reply(m.lang["play_invite"].format(app.name))
                if umm:
                    await asyncio.sleep(2)
                try:
                    await client.join_chat(invite_link)
                except errors.UserAlreadyParticipant:
                    pass
                except errors.InviteRequestSent:
                    try:
                        await client.approve_chat_join_request(m.chat.id, client.id)
                    except Exception as ex:
                        if umm:
                            try:
                                await umm.edit_text(
                                    m.lang["play_invite_error"].format(
                                        type(ex).__name__)
                                )
                            except:
                                pass
                        return
                except Exception as ex:
                    if umm:
                        try:
                            await umm.edit_text(
                                m.lang["play_invite_error"].format(type(ex).__name__)
                            )
                        except:
                            pass
                    return

                if umm:
                    try:
                        await umm.delete()
                    except:
                        pass
                await client.resolve_peer(m.chat.id)

        try:
            await m.delete()
        except:
            pass

        return await play(_, m, force, url, cplay)

    return wrapper

# ==============================================================================
# _inline.py - Inline Keyboard Button Builder
# ==============================================================================
# This file provides helper functions to create inline keyboard buttons.
# Used to build:
# - Playback control buttons (play, pause, skip, stop, etc.)
# - Language selection menus
# - Help menus and navigation
# - Download cancel buttons
# - Settings buttons
# ==============================================================================

from pyrogram import types

from HasiiMusic import app, config, lang



class Inline:
    def __init__(self):
        self.ikm = types.InlineKeyboardMarkup
        self.ikb = types.InlineKeyboardButton

    def cancel_dl(self, text) -> types.InlineKeyboardMarkup:
        return self.ikm([[self.ikb(text=text, callback_data=f"cancel_dl")]])

    def controls(
        self,
        chat_id: int,
        status: str = None,
        timer: str = None,
        remove: bool = False,
    ) -> types.InlineKeyboardMarkup:
        keyboard = []
        if status:
            keyboard.append(
                [self.ikb(
                    text=status, callback_data=f"controls status {chat_id}")]
            )
        elif timer:
            keyboard.append(
                [self.ikb(
                    text=timer, callback_data=f"controls status {chat_id}")]
            )

        if not remove:
            # Seek buttons row
            keyboard.append(
                [
                    self.ikb(
                        text="« 10", callback_data=f"controls seek_back_10 {chat_id}"),
                    self.ikb(
                        text="« 30", callback_data=f"controls seek_back_30 {chat_id}"),
                    self.ikb(
                        text="30 »", callback_data=f"controls seek_forward_30 {chat_id}"),
                    self.ikb(
                        text="10 »", callback_data=f"controls seek_forward_10 {chat_id}"),
                ]
            )
            # Main control buttons row
            keyboard.append(
                [
                    self.ikb(
                        text="▷", callback_data=f"controls resume {chat_id}"),
                    self.ikb(
                        text="II", callback_data=f"controls pause {chat_id}"),
                    self.ikb(
                        text="↻", callback_data=f"controls replay {chat_id}"),
                    self.ikb(
                        text="‣‣I", callback_data=f"controls skip {chat_id}"),
                    self.ikb(
                        text="▢", callback_data=f"controls stop {chat_id}"),
                ]
            )
            # Delete button as full-width button at bottom
            keyboard.append(
                [
                    self.ikb(
                        text="ᴅᴇʟᴇᴛᴇ", callback_data=f"controls close {chat_id}"),
                ]
            )
        return self.ikm(keyboard)

    def help_markup(
        self, _lang: dict, back: bool = False
    ) -> types.InlineKeyboardMarkup:
        if back:
            rows = [
                [
                    self.ikb(text=_lang["back"], callback_data="help back"),
                    self.ikb(text=_lang["close"], callback_data="help close"),
                ]
            ]
        else:
            cbs = ["admins", "auth", "blist", "sudo",
                   "ping", "play", "queue", "stats", "games"]
            buttons = [
                self.ikb(text=_lang[f"help_btn_{cb}"], callback_data=f"help {cb}")
                for cb in cbs
            ]
            rows = [buttons[i: i + 3] for i in range(0, len(buttons), 3)]

        return self.ikm(rows)


    def ping_markup(self, text: str) -> types.InlineKeyboardMarkup:
        return self.ikm([[self.ikb(text=text, url=config.SUPPORT_CHAT)]])

    def play_queued(
        self, chat_id: int, item_id: str, _text: str
    ) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                [
                    self.ikb(
                        text="▷", callback_data=f"controls resume {chat_id}"),
                    self.ikb(
                        text="∣ ∣", callback_data=f"controls pause {chat_id}"),
                    self.ikb(
                        text=">>", callback_data=f"controls skip {chat_id}"),
                    self.ikb(
                        text="▣", callback_data=f"controls stop {chat_id}"),
                ],
                [
                    self.ikb(
                        text="ᴅᴇʟᴇᴛᴇ", callback_data=f"controls close {chat_id}"),
                ]
            ]
        )

    def queue_markup(
        self, chat_id: int, _text: str, playing: bool
    ) -> types.InlineKeyboardMarkup:
        _action = "pause" if playing else "resume"
        return self.ikm(
            [[self.ikb(
                text=_text, callback_data=f"controls {_action} {chat_id} q")]]
        )

    def settings_markup(
        self, lang: dict, admin_only: bool, language: str, chat_id: int
    ) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                [
                    self.ikb(
                        text=lang["play_mode"] + " ➜",
                        callback_data=f"controls status {chat_id}",
                    ),
                    self.ikb(text=admin_only, callback_data="playmode"),
                ],
                [
                    self.ikb(
                        text=lang["language"] + " ➜",
                        callback_data=f"controls status {chat_id}",
                    ),
                    self.ikb(text=lang_codes[language],
                             callback_data="language"),
                ],
            ]
        )

    def start_key(
        self, lang: dict, private: bool = False
    ) -> types.InlineKeyboardMarkup:
        rows = [
            [
                self.ikb(
            ],
        ]
        if private:
            rows += [
                [
                    self.ikb(
                        text=lang["source"],
                        url="https://hasiimusic.hasindunagolla.live/",
                    )
                ]
            ]
        else:
            rows += [[self.ikb(text=lang["language"],
                               callback_data="language")]]
        return self.ikm(rows)

    def yt_key(self, link: str) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                ],
            ]
        )

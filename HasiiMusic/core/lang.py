# ==============================================================================
# lang.py - Multi-Language Support System
# ==============================================================================
# This file manages translations for the bot in multiple languages.
# - Translation files are stored in HasiiMusic/locales/ as JSON files (en.json, si.json)
# - Each chat can have its own language preference stored in the database
# - The @language() decorator automatically injects translations into message handlers
# ==============================================================================

import json
from functools import wraps
from pathlib import Path

from HasiiMusic import db, logger

# supported languages and their display names
lang_codes = {
    "en": "🇺🇸 English",
    "si": "🇱🇰 සිංහල",
    "ta": "🇮🇳 தமிழ்",
    "hi": "🇮🇳 हिन्दी",
    "ms": "🇲🇾 Bahasa Melayu",
    "tl": "🇵🇭 Filipino",
    "ru": "🇷🇺 Русский"
}


class LangDict(dict):
    # dictionary with a fallback for missing keys
    def __init__(self, primary_dict, fallback_dict):
        super().__init__(primary_dict)
        self.fallback = fallback_dict

    def __getitem__(self, key):
        try:
            val = super().__getitem__(key)
            if not val:  # use the fallback if the value is empty
                return self.fallback.get(key, key)
            return val
        except KeyError:
            return self.fallback.get(key, key)


class Language:
    #Handles multiple languages using JSON translation files.

    def __init__(self):
        # set up the language system and load translation files
        self.lang_codes = lang_codes
        # Directory containing translation files
        self.lang_dir = Path("HasiiMusic/locales")
        self.languages = self.load_files()  # Load all language files into memory

    def load_files(self):
        """Load all language JSON files from the locales directory."""
        languages = {}
        for lang_code in self.lang_codes.keys():
            lang_file = self.lang_dir / f"{lang_code}.json"  # Path to language file
            if lang_file.exists():
                try:
                    with open(lang_file, "r", encoding="utf-8") as file:
                        languages[lang_code] = json.load(file)  # Load translations into dict
                except Exception as e:
                    logger.error(f"Failed to load language {lang_code}: {e}")
            else:
                logger.warning(f"Language file not found: {lang_file}")
        
        # make sure English is always available
        if "en" not in languages:
            languages["en"] = {}
            
        logger.info(f"🌐 Loaded languages: {', '.join(languages.keys())}")
        return languages

    async def get_lang(self, chat_id: int) -> dict:
        # get the translations for a chat
        lang_code = await db.get_lang(chat_id)
        if lang_code not in self.languages:
            lang_code = "en"
            
        if lang_code == "en":
            return self.languages["en"]
            
        return LangDict(self.languages[lang_code], self.languages["en"])

    def language(self):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                fallen = next(
                    (
                        arg
                        for arg in args
                        if hasattr(arg, "chat") or hasattr(arg, "message")
                    ),
                    None,
                )

                if hasattr(fallen, "chat"):
                    chat = fallen.chat
                elif hasattr(fallen, "message"):
                    chat = fallen.message.chat

                if chat.id in db.blacklisted:
                    return await chat.leave()

                lang_code = await db.get_lang(chat.id)
                if lang_code not in self.languages:
                    lang_code = "en"

                if lang_code == "en":
                    lang_dict = self.languages["en"]
                else:
                    lang_dict = LangDict(self.languages[lang_code], self.languages["en"])

                setattr(fallen, "lang", lang_dict)
                return await func(*args, **kwargs)

            return wrapper

        return decorator

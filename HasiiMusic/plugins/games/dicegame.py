# ==============================================================================
# dicegame.py - Mini Games
# ==============================================================================
# Telegram's built-in animated dice games (/dice, /dart, /basket, etc).
# ==============================================================================

from pyrogram import filters
from HasiiMusic import app, lang

# Dice 🎲
@app.on_message(filters.command("dice"))
@lang.language()
async def roll_dice(bot, message):
    try:
        await message.delete()
    except Exception:
        pass
    try:
        x = await bot.send_dice(message.chat.id, "🎲")
        m = x.dice.value
        await message.reply_text(message.lang["dice_rolled"].format(message.from_user.mention, m))
    except Exception as e:
        if "FLOOD_WAIT" not in str(e):
            try:
                await message.reply_text(message.lang["dice_error"].format(str(e)))
            except:
                pass


@app.on_message(filters.dice)
@lang.language()
async def dice_emoji_handler(bot, message):
    try:
        m = message.dice.value
        emoji = message.dice.emoji
        await message.reply_text(message.lang["dice_scored"].format(emoji, message.from_user.mention, m))
    except Exception as e:
        if "FLOOD_WAIT" not in str(e):
            try:
                await message.reply_text(message.lang["dice_error"].format(str(e)))
            except:
                pass


# Jackpot 🎰
@app.on_message(filters.command("jackpot"))
@lang.language()
async def spin_jackpot(bot, message):
    try:
        await message.delete()
    except Exception:
        pass
    try:
        x = await bot.send_dice(message.chat.id, "🎰")
        m = x.dice.value
        await message.reply_text(message.lang["dice_jackpot"].format(message.from_user.mention, m))
    except Exception as e:
        if "FLOOD_WAIT" not in str(e):
            try:
                await message.reply_text(message.lang["dice_error"].format(str(e)))
            except:
                pass


# Darts 🎯
@app.on_message(filters.command("dart"))
@lang.language()
async def dart_game(bot, message):
    try:
        await message.delete()
    except Exception:
        pass
    try:
        x = await bot.send_dice(message.chat.id, "🎯")
        m = x.dice.value
        await message.reply_text(message.lang["dice_dart"].format(message.from_user.mention, m))
    except Exception as e:
        if "FLOOD_WAIT" not in str(e):
            try:
                await message.reply_text(message.lang["dice_error"].format(str(e)))
            except:
                pass


# Basketball 🏀
@app.on_message(filters.command("basket"))
@lang.language()
async def basket_game(bot, message):
    try:
        await message.delete()
    except Exception:
        pass
    try:
        x = await bot.send_dice(message.chat.id, "🏀")
        m = x.dice.value
        await message.reply_text(message.lang["dice_basket"].format(message.from_user.mention, m))
    except Exception as e:
        if "FLOOD_WAIT" not in str(e):
            try:
                await message.reply_text(message.lang["dice_error"].format(str(e)))
            except:
                pass


# Bowling Ball 🎳
@app.on_message(filters.command("ball"))
@lang.language()
async def ball_game(bot, message):
    try:
        await message.delete()
    except Exception:
        pass
    try:
        x = await bot.send_dice(message.chat.id, "🎳")
        m = x.dice.value
        await message.reply_text(message.lang["dice_ball"].format(message.from_user.mention, m))
    except Exception as e:
        if "FLOOD_WAIT" not in str(e):
            try:
                await message.reply_text(message.lang["dice_error"].format(str(e)))
            except:
                pass


# Football ⚽
@app.on_message(filters.command("football"))
@lang.language()
async def football_game(bot, message):
    try:
        await message.delete()
    except Exception:
        pass
    try:
        x = await bot.send_dice(message.chat.id, "⚽")
        m = x.dice.value
        await message.reply_text(message.lang["dice_football"].format(message.from_user.mention, m))
    except Exception as e:
        if "FLOOD_WAIT" not in str(e):
            try:
                await message.reply_text(message.lang["dice_error"].format(str(e)))
            except:
                pass


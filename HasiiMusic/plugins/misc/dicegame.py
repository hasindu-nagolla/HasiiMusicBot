# ==============================================================================
# dicegame.py - Telegram Dice Game Commands
# ==============================================================================
# Fun emoji dice games using Telegram's built-in dice feature.
# Commands: /dice, /dart, /basket, /jackpot, /ball, /football
# Can also be triggered by sending the emoji directly: 🎲, 🎯, 🏀, 🎰, 🎳, ⚽
# Now integrated with Tournament Arena for competitive gameplay!
# ==============================================================================

from pyrogram import filters
from HasiiMusic import app
from HasiiMusic.helpers._tournament import TournamentHelper

# Helper function to record score in tournament
async def record_tournament_score(chat_id: int, user_id: int, score: int, game_type: str):
    """Record score in active tournament if exists"""
    try:
        if chat_id < 0:  # Only in groups
            await TournamentHelper.add_score(chat_id, user_id, score, game_type)
    except Exception as e:
        print(f"Error recording tournament score: {e}")

# Dice 🎲
@app.on_message(filters.command("dice"))
async def roll_dice(bot, message):
    try:
        x = await bot.send_dice(message.chat.id, "🎲")
        m = x.dice.value
        await message.reply_text(f"🎲 Hey {message.from_user.mention}, your score is: {m}", quote=True)
        
        # Record in tournament
        await record_tournament_score(message.chat.id, message.from_user.id, m, "dice")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@app.on_message(filters.dice)
async def dice_emoji_handler(bot, message):
    try:
        m = message.dice.value
        game_type_map = {
            "🎲": "dice",
            "🎯": "dart",
            "🏀": "basket",
            "🎰": "jackpot",
            "🎳": "ball",
            "⚽": "football"
        }
        
        emoji = message.dice.emoji
        game_type = game_type_map.get(emoji, "unknown")
        
        if emoji == "🎲":
            await message.reply_text(f"🎲 Hey {message.from_user.mention}, your score is: {m}", quote=True)
        elif emoji == "🎯":
            await message.reply_text(f"🎯 Hey {message.from_user.mention}, your score is: {m}", quote=True)
        elif emoji == "🏀":
            await message.reply_text(f"🏀 Hey {message.from_user.mention}, your score is: {m}", quote=True)
        elif emoji == "🎰":
            await message.reply_text(f"🎰 Hey {message.from_user.mention}, your score is: {m}", quote=True)
        elif emoji == "🎳":
            await message.reply_text(f"🎳 Hey {message.from_user.mention}, your score is: {m}", quote=True)
        elif emoji == "⚽":
            await message.reply_text(f"⚽ Hey {message.from_user.mention}, your score is: {m}", quote=True)
        
        # Record in tournament
        if game_type != "unknown":
            await record_tournament_score(message.chat.id, message.from_user.id, m, game_type)
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Dart 🎯
@app.on_message(filters.command("dart"))
async def throw_dart(bot, message):
    try:
        x = await bot.send_dice(message.chat.id, "🎯")
        m = x.dice.value
        await message.reply_text(f"🎯 Hey {message.from_user.mention}, your score is: {m}", quote=True)
        
        # Record in tournament
        await record_tournament_score(message.chat.id, message.from_user.id, m, "dart")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Basketball 🏀
@app.on_message(filters.command("basket"))
async def shoot_basket(bot, message):
    try:
        x = await bot.send_dice(message.chat.id, "🏀")
        m = x.dice.value
        await message.reply_text(f"🏀 Hey {message.from_user.mention}, your score is: {m}", quote=True)
        
        # Record in tournament
        await record_tournament_score(message.chat.id, message.from_user.id, m, "basket")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Jackpot 🎰
@app.on_message(filters.command("jackpot"))
async def spin_jackpot(bot, message):
    try:
        x = await bot.send_dice(message.chat.id, "🎰")
        m = x.dice.value
        await message.reply_text(f"🎰 Hey {message.from_user.mention}, your score is: {m}", quote=True)
        
        # Record in tournament
        await record_tournament_score(message.chat.id, message.from_user.id, m, "jackpot")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Bowling Ball 🎳
@app.on_message(filters.command("ball"))
async def roll_ball(bot, message):
    try:
        x = await bot.send_dice(message.chat.id, "🎳")
        m = x.dice.value
        await message.reply_text(f"🎳 Hey {message.from_user.mention}, your score is: {m}", quote=True)
        
        # Record in tournament
        await record_tournament_score(message.chat.id, message.from_user.id, m, "ball")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Football ⚽
@app.on_message(filters.command("football"))
async def kick_football(bot, message):
    try:
        x = await bot.send_dice(message.chat.id, "⚽")
        m = x.dice.value
        await message.reply_text(f"⚽ Hey {message.from_user.mention}, your score is: {m}", quote=True)
        
        # Record in tournament
        await record_tournament_score(message.chat.id, message.from_user.id, m, "football")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")


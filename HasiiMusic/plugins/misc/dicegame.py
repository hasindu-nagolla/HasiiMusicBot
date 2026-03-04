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
    """Record score in active turn-based tournament"""
    try:
        if chat_id < 0:  # Only in groups
            success, round_complete = await TournamentHelper.add_score(chat_id, user_id, score, game_type)
            return success, round_complete
    except Exception as e:
        print(f"Error recording tournament score: {e}")
    return False, False

# Dice 🎲
@app.on_message(filters.command("dice"))
async def roll_dice(bot, message):
    # Auto-delete command message
    try:
        await message.delete()
    except Exception:
        pass
    
    try:
        x = await bot.send_dice(message.chat.id, "🎲")
        m = x.dice.value
        
        # Try to record in tournament
        success, round_complete = await record_tournament_score(message.chat.id, message.from_user.id, m, "dice")
        
        if success:
            await message.reply_text(
                f"🎲 {message.from_user.mention} rolled: {m}\n"
                f"✅ Score recorded!",
                quote=True
            )
            if round_complete:
                await message.reply_text("🎉 Round complete! Waiting for admin...")
        else:
            await message.reply_text(f"🎲 {message.from_user.mention} rolled: {m}", quote=True)
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
        
        # Try to record in tournament
        if game_type != "unknown":
            success, round_complete = await record_tournament_score(message.chat.id, message.from_user.id, m, game_type)
            
            if success:
                await message.reply_text(
                    f"{emoji} {message.from_user.mention} scored: {m}\n"
                    f"✅ Turn recorded!",
                    quote=True
                )
                
                if round_complete:
                    # Round is complete, ask admin to continue
                    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    
                    # Get scoreboard
                    scoreboard_data = await TournamentHelper.get_scoreboard(message.chat.id)
                    from HasiiMusic.plugins.features.tournament_admin import format_scoreboard
                    scoreboard_text = await format_scoreboard(scoreboard_data, {}, started=True)
                    
                    keyboard = InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("✅ Next Round", callback_data="tour_next_round"),
                            InlineKeyboardButton("🏁 End Game", callback_data="tour_end")
                        ]
                    ])
                    
                    await message.reply_text(
                        f"🎉 <b>ROUND COMPLETE!</b>\n\n"
                        f"{scoreboard_text}\n\n"
                        f"🎮 Admin, do you want to play another round?",
                        reply_markup=keyboard
                    )
                else:
                    # Turn advanced to next player, notify them
                    try:
                        tournament = await TournamentHelper.get_active_tournament(message.chat.id)
                        
                        if tournament and tournament.get("current_turn_user_id"):
                            next_user_id = tournament["current_turn_user_id"]
                            next_user = await app.get_users(next_user_id)
                            
                            # Get game emoji
                            game_type = tournament["game_type"]
                            game_emoji = {
                                "dice": "🎲",
                                "dart": "🎯",
                                "basket": "🏀",
                                "jackpot": "🎰",
                                "ball": "🎳",
                                "football": "⚽",
                                "all": "🎮"
                            }.get(game_type, "🎮")
                            
                            await message.reply_text(
                                f"🎯 {next_user.mention} <b>Your turn!</b>\n"
                                f"⏱ You have 30 seconds to send {game_emoji}!"
                            )
                    except Exception as notify_error:
                        print(f"Error notifying next player: {notify_error}")
                return
        
        # Not in tournament or not their turn - just show score
        await message.reply_text(f"{emoji} {message.from_user.mention} scored: {m}", quote=True)
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Jackpot 🎰
@app.on_message(filters.command("jackpot"))
async def spin_jackpot(bot, message):
    # Auto-delete command message
    try:
        await message.delete()
    except Exception:
        pass
    
    try:
        x = await bot.send_dice(message.chat.id, "🎰")
        m = x.dice.value
        
        # Try to record in tournament
        success, round_complete = await record_tournament_score(message.chat.id, message.from_user.id, m, "jackpot")
        
        if success:
            await message.reply_text(
                f"🎰 {message.from_user.mention} scored: {m}\n"
                f"✅ Score recorded!",
                quote=True
            )
            if round_complete:
                await message.reply_text("🎉 Round complete! Waiting for admin...")
        else:
            await message.reply_text(f"🎰 Hey {message.from_user.mention}, your score is: {m}", quote=True)
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Darts 🎯
@app.on_message(filters.command("dart"))
async def throw_dart(bot, message):
    # Auto-delete command message
    try:
        await message.delete()
    except Exception:
        pass
    
    try:
        x = await bot.send_dice(message.chat.id, "🎯")
        m = x.dice.value
        
        # Try to record in tournament
        success, round_complete = await record_tournament_score(message.chat.id, message.from_user.id, m, "dart")
        
        if success:
            await message.reply_text(
                f"🎯 {message.from_user.mention} scored: {m}\n"
                f"✅ Score recorded!",
                quote=True
            )
            if round_complete:
                await message.reply_text("🎉 Round complete! Waiting for admin...")
        else:
            await message.reply_text(f"🎯 Hey {message.from_user.mention}, your score is: {m}", quote=True)
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Basketball 🏀
@app.on_message(filters.command("basket"))
async def shoot_basket(bot, message):
    # Auto-delete command message
    try:
        await message.delete()
    except Exception:
        pass
    
    try:
        x = await bot.send_dice(message.chat.id, "🏀")
        m = x.dice.value
        
        # Try to record in tournament
        success, round_complete = await record_tournament_score(message.chat.id, message.from_user.id, m, "basket")
        
        if success:
            await message.reply_text(
                f"🏀 {message.from_user.mention} scored: {m}\n"
                f"✅ Score recorded!",
                quote=True
            )
            if round_complete:
                await message.reply_text("🎉 Round complete! Waiting for admin...")
        else:
            await message.reply_text(f"🏀 Hey {message.from_user.mention}, your score is: {m}", quote=True)
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Bowling Ball 🎳
@app.on_message(filters.command("ball"))
async def roll_ball(bot, message):
    # Auto-delete command message
    try:
        await message.delete()
    except Exception:
        pass
    
    try:
        x = await bot.send_dice(message.chat.id, "🎳")
        m = x.dice.value
        
        # Try to record in tournament
        success, round_complete = await record_tournament_score(message.chat.id, message.from_user.id, m, "ball")
        
        if success:
            await message.reply_text(
                f"🎳 {message.from_user.mention} scored: {m}\n"
                f"✅ Score recorded!",
                quote=True
            )
            if round_complete:
                await message.reply_text("🎉 Round complete! Waiting for admin...")
        else:
            await message.reply_text(f"🎳 Hey {message.from_user.mention}, your score is: {m}", quote=True)
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Football ⚽
@app.on_message(filters.command("football"))
async def kick_football(bot, message):
    # Auto-delete command message
    try:
        await message.delete()
    except Exception:
        pass
    
    try:
        x = await bot.send_dice(message.chat.id, "⚽")
        m = x.dice.value
        await message.reply_text(f"⚽ Hey {message.from_user.mention}, your score is: {m}", quote=True)
        
        # Record in tournament
        await record_tournament_score(message.chat.id, message.from_user.id, m, "football")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")


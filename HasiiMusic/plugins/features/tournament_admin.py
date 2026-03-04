"""
Tournament Arena - Admin Commands
Admin controls for managing tournaments
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from HasiiMusic import app, lang
from HasiiMusic.helpers._tournament import TournamentHelper
from HasiiMusic.helpers._admins import admin_check

GAME_TYPES = {
    "all": "🎮 All Games",
    "dice": "🎲 Dice Only",
    "dart": "🎯 Dart Only",
    "basket": "🏀 Basketball Only",
    "jackpot": "🎰 Jackpot Only",
    "ball": "🎳 Bowling Only",
    "football": "⚽ Football Only"
}

TOURNAMENT_TYPES = {
    "team": "👥 Team Battle",
    "solo": "🏆 Solo Competition",
    "ffa": "⚔️ Free For All"
}


@app.on_message(filters.command(["tournamentstart", "gameon"]) & filters.group)
@lang.language()
@admin_check
async def start_tournament_cmd(_, message: Message):
    """Start a tournament - Admin only"""
    # Auto-delete command message
    try:
        await message.delete()
    except Exception:
        pass
    
    try:
        # Check if tournament already exists
        existing = await TournamentHelper.get_active_tournament(message.chat.id)
        if existing:
            return await message.reply_text(message.lang.get(
                "tournament_already_exists",
                "❌ A tournament is already active! Use /tournamentstop to end it first."
            ))
        
        # Show tournament setup keyboard (default: Team + All Games + 2 Teams)
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Team Battle", callback_data="tour_setup_team"),
                InlineKeyboardButton("🏆 Solo", callback_data="tour_setup_solo")
            ],
            [
                InlineKeyboardButton("✅ 2 Teams", callback_data="tour_teams_2"),
                InlineKeyboardButton("3️⃣ 3 Teams", callback_data="tour_teams_3"),
                InlineKeyboardButton("4️⃣ 4 Teams", callback_data="tour_teams_4")
            ],
            [
                InlineKeyboardButton("✅ All Games", callback_data="tour_game_all"),
            ],
            [
                InlineKeyboardButton("🎲 Dice", callback_data="tour_game_dice"),
                InlineKeyboardButton("🎯 Dart", callback_data="tour_game_dart"),
                InlineKeyboardButton("🏀 Basket", callback_data="tour_game_basket")
            ],
            [
                InlineKeyboardButton("🎰 Jackpot", callback_data="tour_game_jackpot"),
                InlineKeyboardButton("🎳 Bowling", callback_data="tour_game_ball"),
                InlineKeyboardButton("⚽ Football", callback_data="tour_game_football")
            ],
            [InlineKeyboardButton("✅ Create Tournament", callback_data="tour_create_default")]
        ])
        
        await message.reply_text(
            message.lang.get(
                "tournament_setup",
                "🎮 <b>TOURNAMENT ARENA SETUP</b>\n\n"
                "Choose tournament type and game mode:\n\n"
                "👥 <b>Team Battle:</b> Players join teams and compete together (select 2-4 teams)\n"
                "🏆 <b>Solo:</b> Every player for themselves\n\n"
                "Select game type or create with default settings (Team + All Games)"
            ),
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Error in start_tournament_cmd: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")


@app.on_message(filters.command(["tournamentbegin", "gamestart"]) & filters.group)
@lang.language()
@admin_check
async def begin_tournament_cmd(_, message: Message):
    """Begin the tournament (start Round 1) - Admin only"""
    # Auto-delete command message
    try:
        await message.delete()
    except Exception:
        pass
    
    try:
        tournament = await TournamentHelper.get_active_tournament(message.chat.id)
        if not tournament:
            return await message.reply_text(message.lang.get(
                "no_tournament",
                "❌ No tournament found! Use /gameon to create one."
            ))
        
        if tournament["status"] == "playing":
            return await message.reply_text(message.lang.get(
                "tournament_already_active",
                "❌ Tournament is already active!"
            ))
        
        # Check minimum players
        total_players = sum(len(players) for players in tournament["teams"].values())
        if total_players < 2:
            return await message.reply_text(message.lang.get(
                "tournament_min_players",
                "❌ Need at least 2 players to start! Current players: {0}"
            ).format(total_players))
        
        success, tournament = await TournamentHelper.start_tournament(message.chat.id)
        if success:
            # Countdown animation
            countdown_msg = await message.reply_text("🎮 <b>Starting Tournament...</b>\n\n⏰ <b>5</b>")
            
            import asyncio
            for count in [4, 3, 2, 1]:
                await asyncio.sleep(1)
                await countdown_msg.edit_text(f"🎮 <b>Starting Tournament...</b>\n\n⏰ <b>{count}</b>")
            
            await asyncio.sleep(1)
            await countdown_msg.edit_text("🎮 <b>Starting Tournament...</b>\n\n🚀 <b>READY!</b>")
            await asyncio.sleep(0.5)
            
            # Get current turn info
            current_user_id = tournament["current_turn_user_id"]
            current_user = await app.get_users(current_user_id)
            
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
            
            scoreboard_data = await TournamentHelper.get_scoreboard(message.chat.id)
            scoreboard_text = await format_scoreboard(scoreboard_data, message.lang, started=True)
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Live Scores", callback_data="tour_scores")],
                [InlineKeyboardButton("🏁 End Tournament", callback_data="tour_end")]
            ])
            
            turn_text = (
                f"🎮 <b>ROUND 1 STARTED!</b>\n\n"
                f"{scoreboard_text}\n\n"
                f"🎯 <b>Now Playing:</b> {current_user.mention}\n"
                f"⏱ You have 30 seconds to send {game_emoji}!\n"
            )
            
            await countdown_msg.edit_text(turn_text, reply_markup=keyboard)
        else:
            await message.reply_text(message.lang.get(
                "tournament_start_failed",
                "❌ Failed to start tournament!"
            ))
    except Exception as e:
        print(f"Error in begin_tournament_cmd: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")


@app.on_message(filters.command(["tournamentstop", "gamestop"]) & filters.group)
@lang.language()
@admin_check
async def stop_tournament_cmd(_, message: Message):
    """Stop and finish the tournament - Admin only"""
    # Auto-delete command message
    try:
        await message.delete()
    except Exception:
        pass
    
    try:
        # Check if tournament exists and its status
        tournament = await TournamentHelper.get_active_tournament(message.chat.id)
        if not tournament:
            return await message.reply_text(message.lang.get(
                "no_active_tournament",
                "❌ No active tournament found!"
            ))
        
        if tournament["status"] == "pending":
            return await message.reply_text(
                "❌ Tournament hasn't started yet! Use /gamestart to begin, or /gamecancel to cancel."
            )
        
        success, results = await TournamentHelper.stop_tournament(message.chat.id)
        if success and results:
            # Format final results
            results_text = await format_results(results, message.lang)
            await message.reply_text(results_text)
        else:
            await message.reply_text(message.lang.get(
                "no_active_tournament",
                "❌ No active tournament found!"
            ))
    except Exception as e:
        print(f"Error in stop_tournament_cmd: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")


@app.on_message(filters.command(["tournamentcancel", "gamecancel"]) & filters.group)
@lang.language()
@admin_check
async def cancel_tournament_cmd(_, message: Message):
    """Cancel the tournament - Admin only"""
    # Auto-delete command message
    try:
        await message.delete()
    except Exception:
        pass
    
    try:
        success = await TournamentHelper.cancel_tournament(message.chat.id)
        if success:
            await message.reply_text(message.lang.get(
                "tournament_cancelled",
                "🚫 Tournament cancelled!"
            ))
        else:
            await message.reply_text(message.lang.get(
                "no_tournament",
                "❌ No tournament found!"
            ))
    except Exception as e:
        print(f"Error in cancel_tournament_cmd: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")


@app.on_message(filters.command(["score", "scores", "standings"]) & filters.group)
@lang.language()
async def view_scores_cmd(_, message: Message):
    """View current tournament scores"""
    # Auto-delete command message
    try:
        await message.delete()
    except Exception:
        pass
    
    try:
        scoreboard_data = await TournamentHelper.get_scoreboard(message.chat.id)
        if not scoreboard_data:
            return await message.reply_text(message.lang.get(
                "no_tournament",
                "❌ No active tournament!"
            ))
        
        scoreboard_text = await format_scoreboard(scoreboard_data, message.lang)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data="tour_scores")]
        ])
        
        await message.reply_text(scoreboard_text, reply_markup=keyboard)
    except Exception as e:
        print(f"Error in view_scores_cmd: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")


@app.on_message(filters.command(["leaderboard", "topleaders", "rankings"]) & filters.group)
@lang.language()
async def leaderboard_cmd(_, message: Message):
    """View chat leaderboard"""
    # Auto-delete command message
    try:
        await message.delete()
    except Exception:
        pass
    
    try:
        leaderboard = await TournamentHelper.get_leaderboard(message.chat.id, limit=10)
        
        if not leaderboard:
            return await message.reply_text(message.lang.get(
                "no_leaderboard",
                "📊 No leaderboard data yet! Play some tournaments first."
            ))
        
        text = message.lang.get(
            "leaderboard_title",
            "🏆 <b>HALL OF CHAMPIONS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        
        medals = ["🥇", "🥈", "🥉"]
        for idx, player in enumerate(leaderboard, 1):
            medal = medals[idx-1] if idx <= 3 else f"{idx}."
            text += (
                f"{medal} <b>{player['user_name']}</b>\n"
                f"   💎 Score: {player['total_score']} | "
                f"🎮 Played: {player['tournaments_played']} | "
                f"🏆 Won: {player['tournaments_won']} "
                f"({player['win_rate']}%)\n\n"
            )
        
        await message.reply_text(text)
    except Exception as e:
        print(f"Error in leaderboard_cmd: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")


async def format_scoreboard(scoreboard_data: dict, lang: dict, started: bool = False) -> str:
    """Format scoreboard text"""
    tournament = scoreboard_data["tournament"]
    team_scores = scoreboard_data["team_scores"]
    
    # Status emoji
    status_emoji = {
        "pending": "⏳",
        "playing": "🔥",
        "waiting_admin": "⏸️",
        "finished": "🏁"
    }
    
    status = tournament["status"]
    game_name = GAME_TYPES.get(tournament["game_type"], "All Games")
    tournament_type = tournament["tournament_type"]
    
    text = (
        f"🎮 <b>TOURNAMENT ARENA</b> {status_emoji.get(status, '❓')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 Status: <b>{status.upper()}</b>\n"
        f"🎯 Game: <b>{game_name}</b>\n"
        f"🏆 Mode: <b>{TOURNAMENT_TYPES.get(tournament_type, 'Unknown')}</b>\n"
    )
    
    if started and tournament.get("current_round", 0) > 0:
        text += f"🔢 Round: <b>{tournament['current_round']}</b>\n"
        
        # Show current turn
        if tournament.get("current_turn_user_id"):
            from HasiiMusic import app
            try:
                current_user = await app.get_users(tournament["current_turn_user_id"])
                text += f"🎯 Current Turn: <b>{current_user.first_name}</b>\n"
            except:
                pass
    
    text += "\n"
    
    # Format based on tournament type
    if tournament_type == "team":
        # Sort teams by score
        sorted_teams = sorted(team_scores.items(), key=lambda x: x[1]["total"], reverse=True)
        
        for rank, (team_name, data) in enumerate(sorted_teams, 1):
            rank_emoji = ["👑", "🥈", "🥉"][rank-1] if rank <= 3 else f"{rank}."
            text += (
                f"{rank_emoji} <b>{team_name}</b>\n"
                f"   💎 Total Score: <b>{data['total']}</b>\n"
                f"   👥 Members ({len(data['players'])}):\n"
            )
            
            for idx, player in enumerate(data["players"], 1):
                text += f"      {idx}. {player['name']} - {player['score']}\n"
            
            text += "\n"
    else:
        # Solo mode - show top 10 individual rankings
        sorted_players = sorted(team_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        
        # Limit to top 10
        top_players = sorted_players[:10]
        
        for rank, (player_name, data) in enumerate(top_players, 1):
            rank_emoji = ["👑", "🥈", "🥉"][rank-1] if rank <= 3 else f"{rank}."
            text += f"{rank_emoji} <b>{player_name}</b> - 💎 {data['score']}\n"
        
        if len(sorted_players) > 10:
            text += f"\n<i>... and {len(sorted_players) - 10} more players</i>\n"
    
    if status == "pending":
        text += "\n💡 <i>Waiting for admin to start the tournament...</i>"
    elif status == "playing":
        text += "\n🎮 <i>Tournament is LIVE! Wait for your turn!</i>"
    elif status == "waiting_admin":
        text += "\n⏸️ <i>Round complete! Admin deciding next round...</i>"
    
    return text


async def format_results(results: dict, lang: dict) -> str:
    """Format tournament results"""
    team_scores = results.get("team_scores", {})
    winner = results.get("winner", "Unknown")
    tournament_type = results.get("tournament_type", "team")
    
    text = (
        f"🏆 <b>TOURNAMENT RESULTS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👑 <b>WINNER: {winner}</b> 🎊\n\n"
        f"📊 <b>Final Standings:</b>\n\n"
    )
    
    if tournament_type == "team":
        sorted_teams = sorted(team_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        
        for rank, (team_name, data) in enumerate(sorted_teams, 1):
            rank_emoji = ["🥇", "🥈", "🥉"][rank-1] if rank <= 3 else f"{rank}."
            text += (
                f"{rank_emoji} {team_name}\n"
                f"   💎 Score: <b>{data['score']}</b> | "
                f"👥 Players: {data['players']}\n\n"
            )
    else:
        # Solo mode - show top 10 individual results
        sorted_players = sorted(team_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        
        # Limit to top 10
        top_players = sorted_players[:10]
        
        for rank, (player_name, data) in enumerate(top_players, 1):
            rank_emoji = ["🥇", "🥈", "🥉"][rank-1] if rank <= 3 else f"{rank}."
            text += f"{rank_emoji} <b>{player_name}</b> - 💎 {data['score']}\n"
        
        if len(sorted_players) > 10:
            text += f"\n<i>... and {len(sorted_players) - 10} more players</i>\n"
    
    text += "\n🎉 <i>Congratulations to all participants!</i>"
    
    return text

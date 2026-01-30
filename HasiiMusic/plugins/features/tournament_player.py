"""
Tournament Arena - Player Commands
Player participation, joining teams, and viewing stats
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from HasiiMusic import app, lang
from HasiiMusic.helpers._tournament import TournamentHelper


@app.on_message(filters.command(["join", "jointeam", "register"]) & filters.group)
@lang.language()
async def join_tournament_cmd(_, message: Message):
    """Join the tournament"""
    try:
        tournament = await TournamentHelper.get_active_tournament(message.chat.id)
        
        if not tournament:
            return await message.reply_text(message.lang.get(
                "no_tournament",
                "❌ No tournament available! Ask an admin to start one with /gameon"
            ))
        
        if tournament["status"] != "pending":
            return await message.reply_text(message.lang.get(
                "tournament_already_started",
                "❌ Tournament already started! Wait for the next one."
            ))
        
        # Check if already joined
        is_team_mode = tournament["tournament_type"] == "team"
        user = message.from_user
        
        # Check if user already joined
        if is_team_mode:
            already_joined = any(user.id in players for players in tournament["teams"].values())
        else:
            already_joined = user.id in tournament.get("players", [])
        
        if already_joined:
            return await message.reply_text(message.lang.get(
                "tournament_already_joined",
                "❌ You've already joined this tournament!"
            ))
        
        if is_team_mode:
            # Team mode - show team selection menu
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔴 Red Dragons", callback_data="tour_select_🔴 Red Dragons")],
                [InlineKeyboardButton("🔵 Blue Wolves", callback_data="tour_select_🔵 Blue Wolves")],
                [InlineKeyboardButton("🟢 Green Vipers", callback_data="tour_select_🟢 Green Vipers")],
                [InlineKeyboardButton("🟡 Yellow Tigers", callback_data="tour_select_🟡 Yellow Tigers")],
                [InlineKeyboardButton("📊 View Teams", callback_data="tour_scores")]
            ])
            
            await message.reply_text(
                "🎮 <b>SELECT YOUR TEAM</b>\n\n"
                "Choose which team you want to join:",
                reply_markup=keyboard
            )
        else:
            # Solo mode - join directly
            user_name = user.first_name or f"User{user.id}"
            success, result = await TournamentHelper.join_tournament(
                message.chat.id,
                user.id,
                user_name,
                None
            )
            
            if success:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📊 View Players", callback_data="tour_scores")]
                ])
                
                await message.reply_text(
                    message.lang.get(
                        "tournament_joined_solo",
                        "✅ You joined the tournament!\n\n"
                        "🏆 Solo mode - compete individually!\n"
                        "Wait for admin to start with /gamestart"
                    ),
                    reply_markup=keyboard
                )
            else:
                await message.reply_text("❌ Failed to join tournament!")
        else:
            error_messages = {
                "no_tournament": "❌ No tournament available!",
                "already_started": "❌ Tournament already started!",
                "already_joined": "❌ You've already joined this tournament!",
                "max_players": "❌ Tournament is full!",
                "error": "❌ An error occurred!"
            }
            await message.reply_text(message.lang.get(
                f"tournament_{result}",
                error_messages.get(result, "❌ Failed to join!")
            ))
    except Exception as e:
        print(f"Error in join_tournament_cmd: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")


@app.on_message(filters.command(["leave", "leaveteam", "quit"]) & filters.group)
@lang.language()
async def leave_tournament_cmd(_, message: Message):
    """Leave the tournament"""
    try:
        success = await TournamentHelper.leave_tournament(
            message.chat.id,
            message.from_user.id
        )
        
        if success:
            await message.reply_text(message.lang.get(
                "tournament_left",
                "👋 You left the tournament!"
            ))
        else:
            await message.reply_text(message.lang.get(
                "not_in_tournament",
                "❌ You're not in any tournament or it already started!"
            ))
    except Exception as e:
        print(f"Error in leave_tournament_cmd: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")


@app.on_message(filters.command(["teams", "myteam", "participants"]) & filters.group)
@lang.language()
async def view_teams_cmd(_, message: Message):
    """View tournament teams"""
    try:
        tournament = await TournamentHelper.get_active_tournament(message.chat.id)
        
        if not tournament:
            return await message.reply_text(message.lang.get(
                "no_tournament",
                "❌ No active tournament!"
            ))
        
        text = (
            f"👥 <b>TOURNAMENT TEAMS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        
        total_players = 0
        for team_name, player_ids in tournament["teams"].items():
            text += f"<b>{team_name}</b> ({len(player_ids)} players)\n"
            
            if player_ids:
                # Get player names from database
                from HasiiMusic.helpers._tournament import players_col
                for pid in player_ids:
                    player = await players_col.find_one({"user_id": pid})
                    player_name = player.get("user_name", f"User{pid}") if player else f"User{pid}"
                    text += f"   • {player_name}\n"
                    total_players += 1
            else:
                text += "   <i>No players yet</i>\n"
            
            text += "\n"
        
        text += f"📊 Total participants: <b>{total_players}/{tournament['max_players']}</b>\n\n"
        
        if tournament["status"] == "pending":
            text += "💡 <i>Join with /join command!</i>"
        
        await message.reply_text(text)
    except Exception as e:
        print(f"Error in view_teams_cmd: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")


@app.on_message(filters.command(["mystats", "profile", "tournamentstats"]) & filters.group)
@lang.language()
async def player_stats_cmd(_, message: Message):
    """View player tournament stats"""
    try:
        from HasiiMusic.helpers._tournament import players_col, leaderboard_col
        
        user_id = message.from_user.id
        
        # Get player data
        player = await players_col.find_one({"user_id": user_id})
        leaderboard_data = await leaderboard_col.find_one({
            "chat_id": message.chat.id,
            "user_id": user_id
        })
        
        if not player and not leaderboard_data:
            return await message.reply_text(message.lang.get(
                "no_player_stats",
                "❌ You haven't participated in any tournaments yet!"
            ))
        
        user_name = message.from_user.first_name or f"User{user_id}"
        
        text = (
            f"📊 <b>PLAYER STATS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 <b>{user_name}</b>\n\n"
        )
        
        if leaderboard_data:
            total_score = leaderboard_data.get("total_score", 0)
            tournaments_played = leaderboard_data.get("tournaments_played", 0)
            tournaments_won = leaderboard_data.get("tournaments_won", 0)
            win_rate = round((tournaments_won / tournaments_played * 100), 1) if tournaments_played > 0 else 0
            
            text += (
                f"💎 Total Score: <b>{total_score}</b>\n"
                f"🎮 Tournaments Played: <b>{tournaments_played}</b>\n"
                f"🏆 Tournaments Won: <b>{tournaments_won}</b>\n"
                f"📈 Win Rate: <b>{win_rate}%</b>\n"
            )
        
        if player:
            joined = player.get("tournaments_joined", 0)
            text += f"\n📝 Tournaments Joined: <b>{joined}</b>\n"
        
        # Check if in current tournament
        tournament = await TournamentHelper.get_active_tournament(message.chat.id)
        if tournament:
            user_in_tournament = False
            user_team = None
            for team_name, player_ids in tournament["teams"].items():
                if user_id in player_ids:
                    user_in_tournament = True
                    user_team = team_name
                    break
            
            if user_in_tournament:
                current_score = tournament["scores"].get(str(user_id), 0)
                text += (
                    f"\n🎯 <b>Current Tournament:</b>\n"
                    f"   Team: {user_team}\n"
                    f"   Score: <b>{current_score}</b>\n"
                )
        
        await message.reply_text(text)
    except Exception as e:
        print(f"Error in player_stats_cmd: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")


@app.on_message(filters.command(["tournamentinfo", "gameinfo"]) & filters.group)
@lang.language()
async def tournament_info_cmd(_, message: Message):
    """Show tournament information and rules"""
    try:
        text = (
            "🎮 <b>TOURNAMENT ARENA - HOW TO PLAY</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            "📋 <b>WHAT IS IT?</b>\n"
            "Compete with others in epic dice game tournaments!\n"
            "Join a team, play games, earn points, and climb the leaderboard!\n\n"
            
            "🎯 <b>HOW TO JOIN:</b>\n"
            "1️⃣ Admin starts tournament with /gameon\n"
            "2️⃣ Use /join to enter a team\n"
            "3️⃣ Admin begins with /gamestart\n"
            "4️⃣ Play dice games to earn points!\n\n"
            
            "🎲 <b>SCORING:</b>\n"
            "Play any dice game and your score automatically counts:\n"
            "• /dice - Roll the dice\n"
            "• /dart - Hit the dartboard\n"
            "• /basket - Score basketball shots\n"
            "• /jackpot - Spin the slot machine\n"
            "• /ball - Bowl for strikes\n"
            "• /football - Score goals\n\n"
            
            "Or just send the emoji: 🎲 🎯 🏀 🎰 🎳 ⚽\n\n"
            
            "🏆 <b>WINNING:</b>\n"
            "Team with highest total score wins!\n"
            "Winners get recorded in the Hall of Champions!\n\n"
            
            "📊 <b>COMMANDS:</b>\n"
            "/join - Join tournament\n"
            "/leave - Leave tournament\n"
            "/teams - View all teams\n"
            "/score - Check live scores\n"
            "/mystats - Your statistics\n"
            "/leaderboard - Hall of Champions\n\n"
            
            "💡 <i>Tip: Work with your team and play strategically!</i>"
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 Start Tournament", callback_data="tour_ask_admin")],
            [InlineKeyboardButton("📊 Leaderboard", callback_data="tour_leaderboard")]
        ])
        
        await message.reply_text(text, reply_markup=keyboard)
    except Exception as e:
        print(f"Error in tournament_info_cmd: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")

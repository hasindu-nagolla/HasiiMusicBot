"""
Tournament Arena - Callback Handlers
Inline keyboard callback handlers for tournament interactions
"""

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from HasiiMusic import app
from HasiiMusic.helpers._tournament import TournamentHelper
from HasiiMusic.core.lang import language
from HasiiMusic.helpers._admins import is_admin_callback


# Tournament creation callbacks
@app.on_callback_query(filters.regex(r"^tour_setup_"))
async def tournament_setup_callback(_, query: CallbackQuery):
    """Handle tournament setup options"""
    try:
        action = query.data.split("_")[-1]
        
        # Store in user data (you can implement session storage)
        await query.answer(f"Selected: {action.capitalize()}")
        
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_game_"))
async def tournament_game_callback(_, query: CallbackQuery):
    """Handle game type selection"""
    try:
        game_type = query.data.split("_")[-1]
        await query.answer(f"Selected game: {game_type}")
        
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_create_"))
async def tournament_create_callback(_, query: CallbackQuery):
    """Create tournament with selected options"""
    try:
        # Check if admin
        is_adm = await is_admin_callback(query)
        if not is_adm:
            return await query.answer("Only admins can create tournaments!", show_alert=True)
        
        # Create with default or stored settings
        success = await TournamentHelper.create_tournament(
            chat_id=query.message.chat.id,
            created_by=query.from_user.id,
            tournament_type="team",
            game_type="all",
            max_players=20,
            teams_count=2,
            duration=30
        )
        
        if success:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Join Tournament", callback_data="tour_join_auto")],
                [InlineKeyboardButton("📊 View Teams", callback_data="tour_scores")],
                [InlineKeyboardButton("🎮 Start Tournament", callback_data="tour_begin")]
            ])
            
            text = (
                "🎮 <b>TOURNAMENT CREATED!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n\n"
                "🏆 Type: Team Battle\n"
                "🎯 Games: All Dice Games\n"
                "👥 Max Players: 20\n"
                "⏰ Duration: 30 minutes\n\n"
                "💡 Players can join now!\n"
                "Admin will start when ready."
            )
            
            await query.message.edit_text(text, reply_markup=keyboard)
            await query.answer("Tournament created successfully!")
        else:
            await query.answer("Failed to create tournament! One may already exist.", show_alert=True)
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_join_"))
async def tournament_join_callback(_, query: CallbackQuery):
    """Join tournament via callback"""
    try:
        user = query.from_user
        user_name = user.first_name or f"User{user.id}"
        
        success, result = await TournamentHelper.join_tournament(
            query.message.chat.id,
            user.id,
            user_name,
            None  # Auto-assign team
        )
        
        if success:
            # Show team selection
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔴 Red Dragons", callback_data="tour_team_🔴 Red Dragons")],
                [InlineKeyboardButton("🔵 Blue Wolves", callback_data="tour_team_🔵 Blue Wolves")],
                [InlineKeyboardButton("🟢 Green Vipers", callback_data="tour_team_🟢 Green Vipers")],
                [InlineKeyboardButton("🟡 Yellow Tigers", callback_data="tour_team_🟡 Yellow Tigers")],
                [InlineKeyboardButton("📊 View Teams", callback_data="tour_scores")]
            ])
            
            await query.answer(f"Joined {result}!")
            await query.message.reply_text(
                f"✅ {user_name} joined <b>{result}</b>!\n\n"
                f"Want to switch teams? Choose below:",
                reply_markup=keyboard
            )
        else:
            error_messages = {
                "no_tournament": "No tournament available!",
                "already_started": "Tournament already started!",
                "already_joined": "You've already joined!",
                "max_players": "Tournament is full!",
                "error": "An error occurred!"
            }
            await query.answer(error_messages.get(result, "Failed to join!"), show_alert=True)
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_team_"))
async def tournament_change_team_callback(_, query: CallbackQuery):
    """Change team"""
    try:
        team_name = query.data.replace("tour_team_", "")
        
        # Leave current team and join new one
        await TournamentHelper.leave_tournament(query.message.chat.id, query.from_user.id)
        
        success, result = await TournamentHelper.join_tournament(
            query.message.chat.id,
            query.from_user.id,
            query.from_user.first_name or f"User{query.from_user.id}",
            team_name
        )
        
        if success:
            await query.answer(f"Switched to {team_name}!")
        else:
            await query.answer("Failed to switch teams!", show_alert=True)
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_begin$"))
async def tournament_begin_callback(_, query: CallbackQuery):
    """Begin tournament"""
    try:
        is_adm = await is_admin_callback(query)
        if not is_adm:
            return await query.answer("Only admins can start!", show_alert=True)
        
        tournament = await TournamentHelper.get_active_tournament(query.message.chat.id)
        if not tournament:
            return await query.answer("No tournament found!", show_alert=True)
        
        # Check minimum players
        total_players = sum(len(players) for players in tournament["teams"].values())
        if total_players < 2:
            return await query.answer(f"Need at least 2 players! Current: {total_players}", show_alert=True)
        
        success = await TournamentHelper.start_tournament(query.message.chat.id)
        if success:
            from HasiiMusic.plugins.features.tournament_admin import format_scoreboard
            
            scoreboard_data = await TournamentHelper.get_scoreboard(query.message.chat.id)
            scoreboard_text = await format_scoreboard(scoreboard_data, {}, started=True)
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Live Scores", callback_data="tour_scores")],
                [InlineKeyboardButton("🏁 End Tournament", callback_data="tour_end")]
            ])
            
            await query.message.edit_text(scoreboard_text, reply_markup=keyboard)
            await query.answer("Tournament started! Let the games begin!")
        else:
            await query.answer("Failed to start!", show_alert=True)
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_scores$"))
async def tournament_scores_callback(_, query: CallbackQuery):
    """View current scores"""
    try:
        scoreboard_data = await TournamentHelper.get_scoreboard(query.message.chat.id)
        if not scoreboard_data:
            return await query.answer("No active tournament!", show_alert=True)
        
        from HasiiMusic.plugins.features.tournament_admin import format_scoreboard
        scoreboard_text = await format_scoreboard(scoreboard_data, {})
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data="tour_scores")]
        ])
        
        if scoreboard_data["tournament"]["status"] == "active":
            keyboard.inline_keyboard.append(
                [InlineKeyboardButton("🏁 End Tournament", callback_data="tour_end")]
            )
        
        await query.message.edit_text(scoreboard_text, reply_markup=keyboard)
        await query.answer("Scoreboard updated!")
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_end$"))
async def tournament_end_callback(_, query: CallbackQuery):
    """End tournament"""
    try:
        is_adm = await is_admin_callback(query)
        if not is_adm:
            return await query.answer("Only admins can end the tournament!", show_alert=True)
        
        success, results = await TournamentHelper.stop_tournament(query.message.chat.id)
        if success and results:
            from HasiiMusic.plugins.features.tournament_admin import format_results
            
            results_text = await format_results(results, {})
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Leaderboard", callback_data="tour_leaderboard")],
                [InlineKeyboardButton("🎮 New Tournament", callback_data="tour_ask_admin")]
            ])
            
            await query.message.edit_text(results_text, reply_markup=keyboard)
            await query.answer("Tournament ended!")
        else:
            await query.answer("No active tournament!", show_alert=True)
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_leaderboard$"))
async def tournament_leaderboard_callback(_, query: CallbackQuery):
    """View leaderboard"""
    try:
        leaderboard = await TournamentHelper.get_leaderboard(query.message.chat.id, limit=10)
        
        if not leaderboard:
            return await query.answer("No leaderboard data yet!", show_alert=True)
        
        text = "🏆 <b>HALL OF CHAMPIONS</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        medals = ["🥇", "🥈", "🥉"]
        for idx, player in enumerate(leaderboard, 1):
            medal = medals[idx-1] if idx <= 3 else f"{idx}."
            text += (
                f"{medal} <b>{player['user_name']}</b>\n"
                f"   💎 {player['total_score']} | "
                f"🎮 {player['tournaments_played']} | "
                f"🏆 {player['tournaments_won']} "
                f"({player['win_rate']}%)\n\n"
            )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="tour_scores")]
        ])
        
        await query.message.edit_text(text, reply_markup=keyboard)
        await query.answer("Leaderboard loaded!")
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_ask_admin$"))
async def tournament_ask_admin_callback(_, query: CallbackQuery):
    """Request admin to start tournament"""
    try:
        await query.answer("Ask an admin to use /gameon to start a tournament!")
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)

"""
Tournament Arena - Callback Handlers
Inline keyboard callback handlers for tournament interactions
"""

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from HasiiMusic import app
from HasiiMusic.helpers._tournament import TournamentHelper
from HasiiMusic.core.lang import Language
from HasiiMusic.helpers._admins import is_admin_callback

# Temporary storage for tournament settings per chat
tournament_settings = {}


# Tournament creation callbacks
@app.on_callback_query(filters.regex(r"^tour_setup_"))
async def tournament_setup_callback(_, query: CallbackQuery):
    """Handle tournament setup options"""
    try:
        action = query.data.split("_")[-1]
        chat_id = query.message.chat.id
        
        # Initialize settings if not exists
        if chat_id not in tournament_settings:
            tournament_settings[chat_id] = {"type": "team", "game": "all", "teams": 2}
        
        # Update tournament type
        tournament_settings[chat_id]["type"] = action
        
        # Get current settings
        settings = tournament_settings[chat_id]
        selected_type = settings["type"]
        selected_game = settings["game"]
        selected_teams = settings.get("teams", 2)
        
        # Update keyboard with checkmarks
        keyboard_rows = [
            [
                InlineKeyboardButton(
                    "✅ Team Battle" if selected_type == "team" else "👥 Team Battle",
                    callback_data="tour_setup_team"
                ),
                InlineKeyboardButton(
                    "✅ Solo" if selected_type == "solo" else "🏆 Solo",
                    callback_data="tour_setup_solo"
                )
            ]
        ]
        
        # Add team count selection if team mode
        if selected_type == "team":
            keyboard_rows.append([
                InlineKeyboardButton(
                    "✅ 2 Teams" if selected_teams == 2 else "2️⃣ 2 Teams",
                    callback_data="tour_teams_2"
                ),
                InlineKeyboardButton(
                    "✅ 3 Teams" if selected_teams == 3 else "3️⃣ 3 Teams",
                    callback_data="tour_teams_3"
                ),
                InlineKeyboardButton(
                    "✅ 4 Teams" if selected_teams == 4 else "4️⃣ 4 Teams",
                    callback_data="tour_teams_4"
                )
            ])
        
        keyboard_rows.extend([
            [
                InlineKeyboardButton(
                    "✅ All Games" if selected_game == "all" else "🎮 All Games",
                    callback_data="tour_game_all"
                ),
            ],
            [
                InlineKeyboardButton(
                    "✅ Dice" if selected_game == "dice" else "🎲 Dice",
                    callback_data="tour_game_dice"
                ),
                InlineKeyboardButton(
                    "✅ Dart" if selected_game == "dart" else "🎯 Dart",
                    callback_data="tour_game_dart"
                ),
                InlineKeyboardButton(
                    "✅ Basket" if selected_game == "basket" else "🏀 Basket",
                    callback_data="tour_game_basket"
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ Jackpot" if selected_game == "jackpot" else "🎰 Jackpot",
                    callback_data="tour_game_jackpot"
                ),
                InlineKeyboardButton(
                    "✅ Bowling" if selected_game == "ball" else "🎳 Bowling",
                    callback_data="tour_game_ball"
                ),
                InlineKeyboardButton(
                    "✅ Football" if selected_game == "football" else "⚽ Football",
                    callback_data="tour_game_football"
                )
            ],
            [InlineKeyboardButton("✅ Create Tournament", callback_data="tour_create_default")]
        ])
        
        keyboard = InlineKeyboardMarkup(keyboard_rows)
        try:
            await query.edit_message_reply_markup(reply_markup=keyboard)
            await query.answer(f"Selected: {action.capitalize()} mode")
        except Exception as e:
            if "MESSAGE_NOT_MODIFIED" in str(e):
                await query.answer("Already selected!", show_alert=False)
            else:
                raise
        
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_game_"))
async def tournament_game_callback(_, query: CallbackQuery):
    """Handle game type selection"""
    try:
        game_type = query.data.split("_")[-1]
        chat_id = query.message.chat.id
        
        # Initialize settings if not exists
        if chat_id not in tournament_settings:
            tournament_settings[chat_id] = {"type": "team", "game": "all", "teams": 2}
        
        # Update game type
        tournament_settings[chat_id]["game"] = game_type
        
        # Get current settings
        settings = tournament_settings[chat_id]
        selected_type = settings["type"]
        selected_game = settings["game"]
        selected_teams = settings.get("teams", 2)
        
        # Update keyboard with checkmarks
        keyboard_rows = [
            [
                InlineKeyboardButton(
                    "✅ Team Battle" if selected_type == "team" else "👥 Team Battle",
                    callback_data="tour_setup_team"
                ),
                InlineKeyboardButton(
                    "✅ Solo" if selected_type == "solo" else "🏆 Solo",
                    callback_data="tour_setup_solo"
                )
            ]
        ]
        
        # Add team count selection if team mode
        if selected_type == "team":
            keyboard_rows.append([
                InlineKeyboardButton(
                    "✅ 2 Teams" if selected_teams == 2 else "2️⃣ 2 Teams",
                    callback_data="tour_teams_2"
                ),
                InlineKeyboardButton(
                    "✅ 3 Teams" if selected_teams == 3 else "3️⃣ 3 Teams",
                    callback_data="tour_teams_3"
                ),
                InlineKeyboardButton(
                    "✅ 4 Teams" if selected_teams == 4 else "4️⃣ 4 Teams",
                    callback_data="tour_teams_4"
                )
            ])
        
        keyboard_rows.extend([
            [
                InlineKeyboardButton(
                    "✅ All Games" if selected_game == "all" else "🎮 All Games",
                    callback_data="tour_game_all"
                ),
            ],
            [
                InlineKeyboardButton(
                    "✅ Dice" if selected_game == "dice" else "🎲 Dice",
                    callback_data="tour_game_dice"
                ),
                InlineKeyboardButton(
                    "✅ Dart" if selected_game == "dart" else "🎯 Dart",
                    callback_data="tour_game_dart"
                ),
                InlineKeyboardButton(
                    "✅ Basket" if selected_game == "basket" else "🏀 Basket",
                    callback_data="tour_game_basket"
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ Jackpot" if selected_game == "jackpot" else "🎰 Jackpot",
                    callback_data="tour_game_jackpot"
                ),
                InlineKeyboardButton(
                    "✅ Bowling" if selected_game == "ball" else "🎳 Bowling",
                    callback_data="tour_game_ball"
                ),
                InlineKeyboardButton(
                    "✅ Football" if selected_game == "football" else "⚽ Football",
                    callback_data="tour_game_football"
                )
            ],
            [InlineKeyboardButton("✅ Create Tournament", callback_data="tour_create_default")]
        ])
        
        keyboard = InlineKeyboardMarkup(keyboard_rows)
        try:
            await query.edit_message_reply_markup(reply_markup=keyboard)
            await query.answer(f"Selected game: {game_type}")
        except Exception as e:
            if "MESSAGE_NOT_MODIFIED" in str(e):
                await query.answer("Already selected!", show_alert=False)
            else:
                raise
        
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_teams_"))
async def tournament_teams_callback(_, query: CallbackQuery):
    """Handle team count selection"""
    try:
        teams_count = int(query.data.split("_")[-1])
        chat_id = query.message.chat.id
        
        # Initialize settings if not exists
        if chat_id not in tournament_settings:
            tournament_settings[chat_id] = {"type": "team", "game": "all", "teams": 2}
        
        # Update team count
        tournament_settings[chat_id]["teams"] = teams_count
        
        # Get current settings
        settings = tournament_settings[chat_id]
        selected_type = settings["type"]
        selected_game = settings["game"]
        selected_teams = settings["teams"]
        
        # Update keyboard with checkmarks
        keyboard_rows = [
            [
                InlineKeyboardButton(
                    "✅ Team Battle" if selected_type == "team" else "👥 Team Battle",
                    callback_data="tour_setup_team"
                ),
                InlineKeyboardButton(
                    "✅ Solo" if selected_type == "solo" else "🏆 Solo",
                    callback_data="tour_setup_solo"
                )
            ]
        ]
        
        # Add team count selection if team mode
        if selected_type == "team":
            keyboard_rows.append([
                InlineKeyboardButton(
                    "✅ 2 Teams" if selected_teams == 2 else "2️⃣ 2 Teams",
                    callback_data="tour_teams_2"
                ),
                InlineKeyboardButton(
                    "✅ 3 Teams" if selected_teams == 3 else "3️⃣ 3 Teams",
                    callback_data="tour_teams_3"
                ),
                InlineKeyboardButton(
                    "✅ 4 Teams" if selected_teams == 4 else "4️⃣ 4 Teams",
                    callback_data="tour_teams_4"
                )
            ])
        
        keyboard_rows.extend([
            [
                InlineKeyboardButton(
                    "✅ All Games" if selected_game == "all" else "🎮 All Games",
                    callback_data="tour_game_all"
                ),
            ],
            [
                InlineKeyboardButton(
                    "✅ Dice" if selected_game == "dice" else "🎲 Dice",
                    callback_data="tour_game_dice"
                ),
                InlineKeyboardButton(
                    "✅ Dart" if selected_game == "dart" else "🎯 Dart",
                    callback_data="tour_game_dart"
                ),
                InlineKeyboardButton(
                    "✅ Basket" if selected_game == "basket" else "🏀 Basket",
                    callback_data="tour_game_basket"
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ Jackpot" if selected_game == "jackpot" else "🎰 Jackpot",
                    callback_data="tour_game_jackpot"
                ),
                InlineKeyboardButton(
                    "✅ Bowling" if selected_game == "ball" else "🎳 Bowling",
                    callback_data="tour_game_ball"
                ),
                InlineKeyboardButton(
                    "✅ Football" if selected_game == "football" else "⚽ Football",
                    callback_data="tour_game_football"
                )
            ],
            [InlineKeyboardButton("✅ Create Tournament", callback_data="tour_create_default")]
        ])
        
        keyboard = InlineKeyboardMarkup(keyboard_rows)
        try:
            await query.edit_message_reply_markup(reply_markup=keyboard)
            await query.answer(f"Selected: {teams_count} teams")
        except Exception as e:
            if "MESSAGE_NOT_MODIFIED" in str(e):
                await query.answer("Already selected!", show_alert=False)
            else:
                raise
        
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
        
        chat_id = query.message.chat.id
        
        # Get stored settings or use defaults
        settings = tournament_settings.get(chat_id, {"type": "team", "game": "all", "teams": 2})
        tournament_type = settings["type"]
        game_type = settings["game"]
        teams_count = settings.get("teams", 2) if tournament_type == "team" else 0
        
        # Create tournament with selected settings
        success = await TournamentHelper.create_tournament(
            chat_id=chat_id,
            created_by=query.from_user.id,
            tournament_type=tournament_type,
            game_type=game_type,
            max_players=20,
            teams_count=teams_count
        )
        
        if success:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Join Tournament", callback_data="tour_join_auto")],
                [InlineKeyboardButton("📊 View Standings", callback_data="tour_scores")],
                [InlineKeyboardButton("🎮 Start Tournament", callback_data="tour_begin")],
                [InlineKeyboardButton("🏁 End Tournament", callback_data="tour_end")]
            ])
            
            type_name = "Team Battle" if tournament_type == "team" else "Solo Competition"
            game_name = {"all": "All Dice Games", "dice": "🎲 Dice", "dart": "🎯 Dart", 
                        "basket": "🏀 Basketball", "jackpot": "🎰 Jackpot", 
                        "ball": "🎳 Bowling", "football": "⚽ Football"}.get(game_type, "All Games")
            
            teams_text = ""
            if tournament_type == "team":
                teams_text = f"👥 Teams: {teams_count}\n"
            
            text = (
                "🎮 <b>TOURNAMENT CREATED!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🏆 Type: {type_name}\n"
                f"{teams_text}"
                f"🎯 Games: {game_name}\n"
                "👥 Max Players: 20\n"
                "🎯 Mode: Turn-based rounds\n\n"
                "💡 Players can join now!\n"
                "Admin will start when ready."
            )
            
            await query.message.edit_text(text, reply_markup=keyboard)
            await query.answer("Tournament created successfully!")
            
            # Clear settings after creation
            if chat_id in tournament_settings:
                del tournament_settings[chat_id]
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
        chat_id = query.message.chat.id
        
        # Get tournament to check type
        tournament = await TournamentHelper.get_active_tournament(chat_id)
        if not tournament:
            return await query.answer("No active tournament!", show_alert=True)
        
        is_team_mode = tournament["tournament_type"] == "team"
        
        # Check if already joined
        if is_team_mode:
            already_joined = any(user.id in players for players in tournament["teams"].values())
        else:
            already_joined = user.id in tournament.get("players", [])
        
        if already_joined:
            return await query.answer("⚠️ You've already joined!", show_alert=True)
        
        if is_team_mode:
            # Team mode - show team selection menu (only available teams)
            team_buttons = []
            for team_name in tournament["teams"].keys():
                team_buttons.append([InlineKeyboardButton(team_name, callback_data=f"tour_select_{team_name}")])
            team_buttons.append([InlineKeyboardButton("◀️ Back", callback_data="tour_back")])
            
            keyboard = InlineKeyboardMarkup(team_buttons)
            
            await query.answer("Choose your team!")
            await query.message.reply_text(
                f"🎮 <b>SELECT YOUR TEAM</b>\n\n"
                f"👤 {user_name}, choose which team you want to join:",
                reply_markup=keyboard
            )
        else:
            # Solo mode - join directly
            success, result = await TournamentHelper.join_tournament(
                chat_id,
                user.id,
                user_name,
                None
            )
            
            if success:
                await query.answer("✅ Joined tournament!")
                await query.message.reply_text(
                    f"✅ {user_name} joined the tournament!\n\n"
                    f"🏆 Solo mode - compete individually!"
                )
            else:
                await query.answer("❌ Failed to join!", show_alert=True)
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_select_"))
async def tournament_select_team_callback(_, query: CallbackQuery):
    """Select and join a specific team"""
    try:
        team_name = query.data.replace("tour_select_", "")
        user = query.from_user
        user_name = user.first_name or f"User{user.id}"
        chat_id = query.message.chat.id
        
        # Join the selected team
        success, result = await TournamentHelper.join_tournament(
            chat_id,
            user.id,
            user_name,
            team_name
        )
        
        if success:
            await query.answer(f"✅ Joined {team_name}!")
            try:
                await query.message.edit_text(
                    f"✅ <b>{user_name}</b> joined <b>{team_name}</b>!\n\n"
                    f"Good luck in the tournament! 🎮"
                )
            except Exception:
                await query.message.reply_text(
                    f"✅ <b>{user_name}</b> joined <b>{team_name}</b>!"
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
        print(f"Error in team selection: {e}")
        await query.answer("❌ Error selecting team!", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_team_"))
async def tournament_change_team_callback(_, query: CallbackQuery):
    """Change team"""
    try:
        team_name = query.data.replace("tour_team_", "")
        
        # Check tournament type
        tournament = await TournamentHelper.get_active_tournament(query.message.chat.id)
        if not tournament or tournament["tournament_type"] != "team":
            return await query.answer("Team switching not available in this mode!", show_alert=True)
        
        # Leave current team and join new one
        await TournamentHelper.leave_tournament(query.message.chat.id, query.from_user.id)
        
        success, result = await TournamentHelper.join_tournament(
            query.message.chat.id,
            query.from_user.id,
            query.from_user.first_name or f"User{query.from_user.id}",
            team_name
        )
        
        if success:
            await query.answer(f"✅ Switched to {team_name}!")
        else:
            await query.answer("❌ Failed to switch teams!", show_alert=True)
    except Exception as e:
        print(f"Error in team switch: {e}")
        await query.answer("❌ Error switching teams!", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_begin$"))
async def tournament_begin_callback(_, query: CallbackQuery):
    """Begin tournament"""
    try:
        is_adm = await is_admin_callback(query)
        if not is_adm:
            return await query.answer("⚠️ Only admins can start!", show_alert=True)
        
        tournament = await TournamentHelper.get_active_tournament(query.message.chat.id)
        if not tournament:
            return await query.answer("❌ No tournament found!", show_alert=True)
        
        if tournament["status"] == "active":
            return await query.answer("⚠️ Tournament is already active!", show_alert=True)
        
        # Check minimum players
        is_team_mode = tournament["tournament_type"] == "team"
        if is_team_mode:
            total_players = sum(len(players) for players in tournament["teams"].values())
        else:
            total_players = len(tournament.get("players", []))
        
        if total_players < 2:
            return await query.answer(f"⚠️ Need at least 2 players! Current: {total_players}", show_alert=True)
        
        success, tournament = await TournamentHelper.start_tournament(query.message.chat.id)
        if success:
            # Countdown animation
            import asyncio
            countdown_msg = await query.message.reply_text("🎮 <b>Starting Tournament...</b>\n\n⏰ <b>5</b>")
            
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
            
            from HasiiMusic.plugins.features.tournament_admin import format_scoreboard
            
            scoreboard_data = await TournamentHelper.get_scoreboard(query.message.chat.id)
            scoreboard_text = await format_scoreboard(scoreboard_data, {}, started=True)
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh Scores", callback_data="tour_scores")],
                [InlineKeyboardButton("🏁 End Tournament", callback_data="tour_end")]
            ])
            
            # First show the scoreboard
            scoreboard_message = (
                f"🎮 <b>ROUND 1 STARTED!</b>\n\n"
                f"{scoreboard_text}"
            )
            
            try:
                await countdown_msg.edit_text(scoreboard_message, reply_markup=keyboard)
            except Exception:
                # If edit fails, send new message
                await countdown_msg.delete()
                await query.message.reply_text(scoreboard_message, reply_markup=keyboard)
            
            # Then mention the first player in a separate message
            await query.message.reply_text(
                f"🎯 {current_user.mention} <b>Your turn!</b>\n"
                f"⏱ You have 30 seconds to send {game_emoji}!"
            )
            await query.answer("🎮 Tournament started!")
        else:
            await query.answer("❌ Failed to start!", show_alert=True)
    except Exception as e:
        print(f"Error in tournament begin: {e}")
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_scores$"))
async def tournament_scores_callback(_, query: CallbackQuery):
    """View current scores"""
    try:
        scoreboard_data = await TournamentHelper.get_scoreboard(query.message.chat.id)
        if not scoreboard_data:
            return await query.answer("❌ No active tournament!", show_alert=True)
        
        from HasiiMusic.plugins.features.tournament_admin import format_scoreboard
        tournament = scoreboard_data["tournament"]
        scoreboard_text = await format_scoreboard(scoreboard_data, {}, started=(tournament["status"] == "active"))
        
        # Build keyboard based on tournament status
        keyboard_buttons = []
        
        if tournament["status"] == "pending":
            # Pending - show refresh and back
            keyboard_buttons.append([InlineKeyboardButton("🔄 Refresh", callback_data="tour_scores")])
            keyboard_buttons.append([InlineKeyboardButton("◀️ Back", callback_data="tour_back")])
        elif tournament["status"] == "active":
            # Active - show refresh and back
            keyboard_buttons.append([InlineKeyboardButton("🔄 Refresh", callback_data="tour_scores")])
            keyboard_buttons.append([InlineKeyboardButton("◀️ Back", callback_data="tour_back")])
        
        keyboard = InlineKeyboardMarkup(keyboard_buttons) if keyboard_buttons else None
        
        # Try to edit, if fails (MESSAGE_NOT_MODIFIED), just answer
        try:
            if keyboard:
                await query.message.edit_text(scoreboard_text, reply_markup=keyboard)
            else:
                await query.message.edit_text(scoreboard_text)
            await query.answer("📊 Scoreboard updated!")
        except Exception as e:
            if "MESSAGE_NOT_MODIFIED" in str(e):
                await query.answer("📊 Already showing latest scores!")
            else:
                raise
    except Exception as e:
        print(f"Error in scores callback: {e}")
        await query.answer("❌ Error loading scores!", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_end$"))
async def tournament_end_callback(_, query: CallbackQuery):
    """End tournament"""
    try:
        is_adm = await is_admin_callback(query)
        if not is_adm:
            return await query.answer("⚠️ Only admins can end the tournament!", show_alert=True)
        
        tournament = await TournamentHelper.get_active_tournament(query.message.chat.id)
        if not tournament:
            return await query.answer("❌ No active tournament!", show_alert=True)
        
        # If pending, cancel it instead
        if tournament["status"] == "pending":
            success = await TournamentHelper.cancel_tournament(query.message.chat.id)
            if success:
                try:
                    await query.message.edit_text(
                        "🏁 <b>Tournament Ended</b>\n\n"
                        "The tournament was ended before it started."
                    )
                    await query.answer("✅ Tournament ended!")
                except Exception:
                    await query.message.reply_text("🏁 Tournament ended!")
                    await query.answer("✅ Ended!")
            else:
                await query.answer("❌ Failed to end tournament!", show_alert=True)
            return
        
        # If active, stop it and show results
        success, results = await TournamentHelper.stop_tournament(query.message.chat.id)
        if success and results:
            from HasiiMusic.plugins.features.tournament_admin import format_results
            results_text = await format_results(results, {})
            
            try:
                await query.message.edit_text(results_text)
                await query.answer("🏆 Tournament ended!")
            except Exception:
                await query.message.reply_text(results_text)
                await query.answer("🏆 Tournament ended!")
        else:
            await query.answer("❌ Failed to end tournament!", show_alert=True)
    except Exception as e:
        print(f"Error in tournament end: {e}")
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_cancel$"))
async def tournament_cancel_callback(_, query: CallbackQuery):
    """Cancel tournament - admin only"""
    try:
        is_adm = await is_admin_callback(query)
        if not is_adm:
            return await query.answer("⚠️ Only admins can cancel!", show_alert=True)
        
        success = await TournamentHelper.cancel_tournament(query.message.chat.id)
        if success:
            try:
                await query.message.edit_text(
                    "❌ <b>Tournament Cancelled</b>\n\n"
                    "The tournament has been cancelled by an admin."
                )
                await query.answer("✅ Tournament cancelled!")
            except Exception:
                await query.message.reply_text("❌ Tournament cancelled!")
                await query.answer("✅ Cancelled!")
        else:
            await query.answer("❌ No tournament to cancel!", show_alert=True)
    except Exception as e:
        print(f"Error in cancel: {e}")
        await query.answer("❌ Error cancelling!", show_alert=True)


@app.on_callback_query(filters.regex(r"^tour_back$"))
async def tournament_back_callback(_, query: CallbackQuery):
    """Go back to main tournament view"""
    try:
        tournament = await TournamentHelper.get_active_tournament(query.message.chat.id)
        if not tournament:
            return await query.answer("❌ No active tournament!", show_alert=True)
        
        # Recreate the main tournament view
        keyboard_buttons = []
        
        if tournament["status"] == "pending":
            keyboard_buttons = [
                [InlineKeyboardButton("✅ Join Tournament", callback_data="tour_join_auto")],
                [InlineKeyboardButton("📊 View Standings", callback_data="tour_scores")],
                [InlineKeyboardButton("🎮 Start Tournament", callback_data="tour_begin")],
                [InlineKeyboardButton("🏁 End Tournament", callback_data="tour_end")]
            ]
            status_text = "⏳ PENDING"
            message = "💡 Players can join now!\nAdmin will start when ready."
        else:
            keyboard_buttons = [
                [InlineKeyboardButton("🔄 Refresh Scores", callback_data="tour_scores")],
                [InlineKeyboardButton("🏁 End Tournament", callback_data="tour_end")]
            ]
            status_text = "🔥 ACTIVE"
            message = "🎮 Tournament is LIVE! Play dice games to earn points!"
        
        keyboard = InlineKeyboardMarkup(keyboard_buttons)
        
        type_name = "Team Battle" if tournament["tournament_type"] == "team" else "Solo Competition"
        game_name = {"all": "All Dice Games", "dice": "🎲 Dice", "dart": "🎯 Dart", 
                    "basket": "🏀 Basketball", "jackpot": "🎰 Jackpot", 
                    "ball": "🎳 Bowling", "football": "⚽ Football"}.get(tournament["game_type"], "All Games")
        
        text = (
            f"🎮 <b>TOURNAMENT ARENA {status_text}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🏆 Type: {type_name}\n"
            f"🎯 Games: {game_name}\n"
            f"👥 Max Players: {tournament['max_players']}\n"
            f"🎯 Mode: Turn-based rounds\n\n"
            f"{message}"
        )
        
        try:
            await query.message.edit_text(text, reply_markup=keyboard)
            await query.answer("◀️ Back to tournament")
        except Exception as e:
            if "MESSAGE_NOT_MODIFIED" not in str(e):
                raise
            await query.answer("Already on main view!")
    except Exception as e:
        print(f"Error in back callback: {e}")
        await query.answer("❌ Error!", show_alert=True)


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

@app.on_callback_query(filters.regex(r"^tour_next_round$"))
async def tournament_next_round_callback(_, query: CallbackQuery):
    """Admin starts next round"""
    try:
        is_adm = await is_admin_callback(query)
        if not is_adm:
            return await query.answer("⚠️ Only admins can start the next round!", show_alert=True)
        
        tournament = await TournamentHelper.get_active_tournament(query.message.chat.id)
        if not tournament:
            return await query.answer("❌ No active tournament!", show_alert=True)
        
        if tournament["status"] != "waiting_admin":
            return await query.answer("❌ Round is not complete yet!", show_alert=True)
        
        # Start next round
        success = await TournamentHelper.start_next_round(query.message.chat.id)
        if success:
            # Get updated tournament
            tournament = await TournamentHelper.get_active_tournament(query.message.chat.id)
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
            
            # Get scoreboard
            scoreboard_data = await TournamentHelper.get_scoreboard(query.message.chat.id)
            from HasiiMusic.plugins.features.tournament_admin import format_scoreboard
            scoreboard_text = await format_scoreboard(scoreboard_data, {}, started=True)
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Live Scores", callback_data="tour_scores")],
                [InlineKeyboardButton("🏁 End Tournament", callback_data="tour_end")]
            ])
            
            round_text = (
                f"🎮 <b>ROUND {tournament['current_round']} STARTED!</b>\n\n"
                f"{scoreboard_text}"
            )
            
            await query.message.edit_text(round_text, reply_markup=keyboard)
            
            # Mention the first player in a separate message
            await query.message.reply_text(
                f"🎯 {current_user.mention} <b>Your turn!</b>\n"
                f"⏱ You have 30 seconds to send {game_emoji}!"
            )
            await query.answer("✅ Round started!")
        else:
            await query.answer("❌ Failed to start round!", show_alert=True)
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)
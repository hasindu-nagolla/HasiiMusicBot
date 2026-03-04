"""
Tournament Arena Helper Functions
Manages competitive game tournaments with teams, scores, and leaderboards
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from pymongo import errors as pymongo_errors
from HasiiMusic import db, logger

# Tournament Collections
tournaments_col = db.db.tournaments
players_col = db.db.tournament_players
leaderboard_col = db.db.tournament_leaderboard


class TournamentHelper:
    """Helper class for tournament operations"""

    @staticmethod
    async def create_tournament(
        chat_id: int,
        created_by: int,
        tournament_type: str = "team",  # team, solo
        game_type: str = "all",  # all, dice, dart, basket, jackpot, ball, football
        max_players: int = 20,
        teams_count: int = 2  # 2, 3, or 4 teams
    ) -> bool:
        """Create a new turn-based tournament"""
        try:
            # Check if active tournament exists
            existing = await tournaments_col.find_one({
                "chat_id": chat_id,
                "status": {"$in": ["pending", "playing", "waiting_admin"]}
            })
            
            if existing:
                return False
            
            tournament_data = {
                "chat_id": chat_id,
                "created_by": created_by,
                "created_at": datetime.utcnow(),
                "tournament_type": tournament_type,
                "game_type": game_type,
                "max_players": max_players,
                "teams_count": teams_count,
                "status": "pending",  # pending, playing, waiting_admin, finished
                "teams": {},  # {team_name: [player_ids]} - only for team mode
                "players": [],  # [player_ids] - for solo mode
                "scores": {},  # {player_id: total_score_across_rounds}
                "winner": None,
                # Turn-based fields
                "current_round": 0,  # 0 = not started, 1, 2, 3...
                "turn_queue": [],  # List of user IDs in play order
                "current_turn_index": 0,  # Index in turn_queue
                "current_turn_user_id": None,  # Who's playing now
                "turn_start_time": None,  # When current turn started
                "round_scores": {},  # {round_num: {user_id: score}}
                "eliminated_users": []  # Users who left/timed out
            }
            
            # Initialize teams for team mode
            if tournament_type == "team":
                team_names = ["🔴 Red Dragons", "🔵 Blue Wolves", "🟢 Green Vipers", "🟡 Yellow Tigers"]
                # Only initialize the requested number of teams
                for i in range(teams_count):
                    tournament_data["teams"][team_names[i]] = []
            
            await tournaments_col.insert_one(tournament_data)
            return True
        except Exception as e:
            print(f"Error creating tournament: {e}")
            return False

    @staticmethod
    async def get_active_tournament(chat_id: int) -> Optional[Dict]:
        """Get active tournament for a chat"""
        return await tournaments_col.find_one({
            "chat_id": chat_id,
            "status": {"$in": ["pending", "playing", "waiting_admin"]}
        })

    @staticmethod
    async def build_turn_queue(tournament: Dict) -> List[int]:
        """Build turn queue with team rotation logic"""
        turn_queue = []
        
        if tournament["tournament_type"] == "team":
            # Team mode: Rotate between teams
            # Get all teams that have players
            active_teams = [(name, players) for name, players in tournament["teams"].items() if players]
            
            if not active_teams:
                return []
            
            # Find max team size
            max_size = max(len(players) for _, players in active_teams)
            
            # Interleave teams round-robin style
            for player_index in range(max_size):
                for team_name, players in active_teams:
                    if player_index < len(players):
                        turn_queue.append(players[player_index])
        else:
            # Solo mode: Simple FIFO order
            turn_queue = tournament.get("players", [])[:]
        
        return turn_queue

    @staticmethod
    async def start_tournament(chat_id: int) -> Tuple[bool, Optional[Dict]]:
        """Start Round 1 of tournament"""
        try:
            tournament = await TournamentHelper.get_active_tournament(chat_id)
            if not tournament or tournament["status"] != "pending":
                return False, None
            
            # Check if at least 2 players joined
            if tournament["tournament_type"] == "team":
                total_players = sum(len(players) for players in tournament["teams"].values())
            else:
                total_players = len(tournament.get("players", []))
            
            if total_players < 2:
                return False, None
            
            # Build turn queue
            turn_queue = await TournamentHelper.build_turn_queue(tournament)
            
            if not turn_queue:
                return False, None
            
            # Initialize Round 1
            first_player = turn_queue[0]
            
            await tournaments_col.update_one(
                {"_id": tournament["_id"]},
                {
                    "$set": {
                        "status": "playing",
                        "current_round": 1,
                        "turn_queue": turn_queue,
                        "current_turn_index": 0,
                        "current_turn_user_id": first_player,
                        "turn_start_time": datetime.utcnow(),
                        f"round_scores.1": {}  # Initialize round 1 scores
                    }
                }
            )
            
            # Return updated tournament
            tournament = await tournaments_col.find_one({"_id": tournament["_id"]})
            return True, tournament
        except Exception as e:
            print(f"Error starting tournament: {e}")
            return False, None

    @staticmethod
    async def record_turn_score(chat_id: int, user_id: int, score: int) -> Tuple[bool, bool]:
        """
        Record score for current turn and advance to next player
        Returns: (success, is_round_complete)
        """
        try:
            tournament = await TournamentHelper.get_active_tournament(chat_id)
            if not tournament or tournament["status"] != "playing":
                return False, False
            
            # Verify it's this user's turn
            if tournament.get("current_turn_user_id") != user_id:
                return False, False
            
            current_round = tournament["current_round"]
            
            # Record score for this round
            await tournaments_col.update_one(
                {"_id": tournament["_id"]},
                {
                    "$set": {
                        f"round_scores.{current_round}.{str(user_id)}": score
                    },
                    "$inc": {
                        f"scores.{str(user_id)}": score  # Add to total
                    }
                }
            )
            
            # Advance to next turn
            return await TournamentHelper.advance_turn(chat_id)
        except Exception as e:
            print(f"Error recording turn score: {e}")
            return False, False

    @staticmethod
    async def timeout_player(chat_id: int, user_id: int) -> Tuple[bool, bool]:
        """
        Handle 30-second timeout - give 0 points and advance
        Returns: (success, is_round_complete)
        """
        try:
            tournament = await TournamentHelper.get_active_tournament(chat_id)
            if not tournament or tournament["status"] != "playing":
                return False, False
            
            # Verify it's this user's turn
            if tournament.get("current_turn_user_id") != user_id:
                return False, False
            
            current_round = tournament["current_round"]
            
            # Record 0 score for timeout (both round and total)
            await tournaments_col.update_one(
                {"_id": tournament["_id"]},
                {
                    "$set": {
                        f"round_scores.{current_round}.{str(user_id)}": 0,
                        f"scores.{str(user_id)}": tournament["scores"].get(str(user_id), 0)  # Keep total unchanged (0 added)
                    }
                }
            )
            
            # Advance to next turn
            return await TournamentHelper.advance_turn(chat_id)
        except Exception as e:
            print(f"Error handling timeout: {e}")
            return False, False

    @staticmethod
    async def advance_turn(chat_id: int) -> Tuple[bool, bool]:
        """
        Move to next player's turn
        Returns: (success, is_round_complete)
        """
        try:
            tournament = await TournamentHelper.get_active_tournament(chat_id)
            if not tournament:
                return False, False
            
            turn_queue = tournament.get("turn_queue", [])
            current_index = tournament.get("current_turn_index", 0)
            
            # Move to next player
            next_index = current_index + 1
            
            # Check if round is complete
            if next_index >= len(turn_queue):
                # Round complete! Switch to waiting for admin
                await tournaments_col.update_one(
                    {"_id": tournament["_id"]},
                    {
                        "$set": {
                            "status": "waiting_admin",
                            "current_turn_user_id": None,
                            "turn_start_time": None
                        }
                    }
                )
                return True, True  # Round complete
            
            # Set next player
            next_player = turn_queue[next_index]
            
            await tournaments_col.update_one(
                {"_id": tournament["_id"]},
                {
                    "$set": {
                        "current_turn_index": next_index,
                        "current_turn_user_id": next_player,
                        "turn_start_time": datetime.utcnow()
                    }
                }
            )
            return True, False  # Turn advanced, round not complete
        except Exception as e:
            print(f"Error advancing turn: {e}")
            return False, False

    @staticmethod
    async def start_next_round(chat_id: int) -> Tuple[bool, Optional[Dict]]:
        """Admin starts next round"""
        try:
            tournament = await TournamentHelper.get_active_tournament(chat_id)
            if not tournament or tournament["status"] != "waiting_admin":
                return False, None
            
            next_round = tournament["current_round"] + 1
            turn_queue = tournament.get("turn_queue", [])
            
            if not turn_queue:
                return False, None
            
            first_player = turn_queue[0]
            
            await tournaments_col.update_one(
                {"_id": tournament["_id"]},
                {
                    "$set": {
                        "status": "playing",
                        "current_round": next_round,
                        "current_turn_index": 0,
                        "current_turn_user_id": first_player,
                        "turn_start_time": datetime.utcnow(),
                        f"round_scores.{next_round}": {}
                    }
                }
            )
            
            tournament = await tournaments_col.find_one({"_id": tournament["_id"]})
            return True, tournament
        except Exception as e:
            print(f"Error starting next round: {e}")
            return False, None

    @staticmethod
    async def stop_tournament(chat_id: int) -> Tuple[bool, Optional[Dict]]:
        """Stop tournament and show final results"""
        try:
            tournament = await TournamentHelper.get_active_tournament(chat_id)
            if not tournament:
                return False, None
            
            is_team_mode = tournament["tournament_type"] == "team"
            team_scores = {}
            winner = None
            
            if is_team_mode:
                # Calculate team scores
                for team_name, player_ids in tournament["teams"].items():
                    team_score = sum(
                        tournament["scores"].get(str(pid), 0) for pid in player_ids
                    )
                    team_scores[team_name] = {
                        "score": team_score,
                        "players": len(player_ids)
                    }
                
                # Determine winner
                winner = max(team_scores.items(), key=lambda x: x[1]["score"])[0]
            else:
                # Solo mode - build player scores with names
                for pid in tournament.get("players", []):
                    player = await players_col.find_one({"user_id": pid})
                    player_name = player.get("user_name", f"User{pid}") if player else f"User{pid}"
                    score = tournament["scores"].get(str(pid), 0)
                    team_scores[player_name] = {
                        "score": score,
                        "id": pid
                    }
                
                # Determine winner by name
                if team_scores:
                    winner = max(team_scores.items(), key=lambda x: x[1]["score"])[0]
            
            # Update tournament
            await tournaments_col.update_one(
                {"_id": tournament["_id"]},
                {
                    "$set": {
                        "status": "finished",
                        "end_time": datetime.utcnow(),
                        "winner": winner,
                        "team_scores": team_scores
                    }
                }
            )
            
            # Update leaderboard
            await TournamentHelper.update_leaderboard(chat_id, tournament, team_scores)
            
            return True, {**tournament, "team_scores": team_scores, "winner": winner}
        except Exception as e:
            print(f"Error stopping tournament: {e}")
            return False, None

    @staticmethod
    async def join_tournament(
        chat_id: int,
        user_id: int,
        user_name: str,
        team: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Join a tournament"""
        try:
            tournament = await TournamentHelper.get_active_tournament(chat_id)
            if not tournament:
                return False, "no_tournament"
            
            if tournament["status"] != "pending":
                return False, "already_started"
            
            # Check if already joined
            is_team_mode = tournament["tournament_type"] == "team"
            
            if is_team_mode:
                for team_name, player_ids in tournament["teams"].items():
                    if user_id in player_ids:
                        return False, "already_joined"
                total_players = sum(len(players) for players in tournament["teams"].values())
            else:
                if user_id in tournament.get("players", []):
                    return False, "already_joined"
                total_players = len(tournament.get("players", []))
            
            # Check max players
            if total_players >= tournament["max_players"]:
                return False, "max_players"
            
            # Add player
            if is_team_mode:
                # Auto-assign to smallest team if team not specified
                if not team or team not in tournament["teams"]:
                    team = min(
                        tournament["teams"].items(),
                        key=lambda x: len(x[1])
                    )[0]
                
                await tournaments_col.update_one(
                    {"_id": tournament["_id"]},
                    {
                        "$push": {f"teams.{team}": user_id},
                        "$set": {f"scores.{str(user_id)}": 0}
                    }
                )
            else:
                # Solo mode - just add to players list
                await tournaments_col.update_one(
                    {"_id": tournament["_id"]},
                    {
                        "$push": {"players": user_id},
                        "$set": {f"scores.{str(user_id)}": 0}
                    }
                )
                team = "solo"
            
            # Save player info
            await players_col.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "user_id": user_id,
                        "user_name": user_name,
                        "last_active": datetime.utcnow()
                    },
                    "$inc": {"tournaments_joined": 1}
                },
                upsert=True
            )
            
            return True, team
        except Exception as e:
            print(f"Error joining tournament: {e}")
            return False, "error"

    @staticmethod
    async def leave_tournament(chat_id: int, user_id: int) -> bool:
        """Leave a tournament"""
        try:
            tournament = await TournamentHelper.get_active_tournament(chat_id)
            if not tournament or tournament["status"] != "pending":
                return False
            
            is_team_mode = tournament["tournament_type"] == "team"
            
            if is_team_mode:
                # Remove from team
                for team_name, player_ids in tournament["teams"].items():
                    if user_id in player_ids:
                        await tournaments_col.update_one(
                            {"_id": tournament["_id"]},
                            {
                                "$pull": {f"teams.{team_name}": user_id},
                                "$unset": {f"scores.{str(user_id)}": ""}
                            }
                        )
                        return True
            else:
                # Remove from players list (solo mode)
                if user_id in tournament.get("players", []):
                    await tournaments_col.update_one(
                        {"_id": tournament["_id"]},
                        {
                            "$pull": {"players": user_id},
                            "$unset": {f"scores.{str(user_id)}": ""}
                        }
                    )
                    return True
            
            return False
        except Exception as e:
            print(f"Error leaving tournament: {e}")
            return False

    @staticmethod
    async def add_score(
        chat_id: int,
        user_id: int,
        score: int,
        game_type: str
    ) -> Tuple[bool, bool]:
        """
        Add score - ONLY during player's turn in turn-based mode
        Returns: (success, is_round_complete)
        """
        try:
            tournament = await TournamentHelper.get_active_tournament(chat_id)
            if not tournament or tournament["status"] != "playing":
                return False, False
            
            # CRITICAL: Check if it's this user's turn
            if tournament.get("current_turn_user_id") != user_id:
                return False, False
            
            # Check if already scored this round (prevent duplicates)
            current_round = tournament["current_round"]
            if str(user_id) in tournament.get("round_scores", {}).get(str(current_round), {}):
                return False, False  # Already scored this round
            
            # Check if game type matches
            if tournament["game_type"] != "all" and tournament["game_type"] != game_type:
                return False, False
            
            # Record score and advance turn
            return await TournamentHelper.record_turn_score(chat_id, user_id, score)
        except Exception as e:
            print(f"Error adding score: {e}")
            return False, False

    @staticmethod
    async def get_scoreboard(chat_id: int) -> Optional[Dict]:
        """Get current scoreboard"""
        tournament = await TournamentHelper.get_active_tournament(chat_id)
        if not tournament:
            return None
        
        is_team_mode = tournament["tournament_type"] == "team"
        team_scores = {}
        
        if is_team_mode:
            # Calculate team scores
            for team_name, player_ids in tournament["teams"].items():
                players_data = []
                for pid in player_ids:
                    player = await players_col.find_one({"user_id": pid})
                    player_name = player.get("user_name", f"User{pid}") if player else f"User{pid}"
                    players_data.append({
                        "id": pid,
                        "name": player_name,
                        "score": tournament["scores"].get(str(pid), 0)
                    })
                
                # Sort by score
                players_data.sort(key=lambda x: x["score"], reverse=True)
                
                team_total = sum(p["score"] for p in players_data)
                team_scores[team_name] = {
                    "total": team_total,
                    "players": players_data
                }
        else:
            # Solo mode - individual scores
            for pid in tournament.get("players", []):
                player = await players_col.find_one({"user_id": pid})
                player_name = player.get("user_name", f"User{pid}") if player else f"User{pid}"
                team_scores[player_name] = {
                    "score": tournament["scores"].get(str(pid), 0),
                    "id": pid
                }
        
        return {
            "tournament": tournament,
            "team_scores": team_scores
        }

    @staticmethod
    async def update_leaderboard(chat_id: int, tournament: Dict, team_scores: Dict):
        """Update chat leaderboard after tournament"""
        try:
            # Update winners
            for team_name, data in team_scores.items():
                for player_id in tournament["teams"].get(team_name, []):
                    score = tournament["scores"].get(str(player_id), 0)
                    is_winner = team_name == tournament.get("winner")
                    
                    await leaderboard_col.update_one(
                        {"chat_id": chat_id, "user_id": player_id},
                        {
                            "$inc": {
                                "total_score": score,
                                "tournaments_played": 1,
                                "tournaments_won": 1 if is_winner else 0
                            },
                            "$set": {"last_played": datetime.utcnow()}
                        },
                        upsert=True
                    )
        except Exception as e:
            print(f"Error updating leaderboard: {e}")

    @staticmethod
    async def get_leaderboard(chat_id: int, limit: int = 10) -> List[Dict]:
        """Get chat leaderboard"""
        try:
            cursor = leaderboard_col.find(
                {"chat_id": chat_id}
            ).sort("total_score", -1).limit(limit)
            
            leaderboard = []
            async for doc in cursor:
                player = await players_col.find_one({"user_id": doc["user_id"]})
                leaderboard.append({
                    "user_id": doc["user_id"],
                    "user_name": player.get("user_name", "Unknown") if player else "Unknown",
                    "total_score": doc.get("total_score", 0),
                    "tournaments_played": doc.get("tournaments_played", 0),
                    "tournaments_won": doc.get("tournaments_won", 0),
                    "win_rate": round(
                        (doc.get("tournaments_won", 0) / doc.get("tournaments_played", 1)) * 100,
                        1
                    )
                })
            
            return leaderboard
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []

    @staticmethod
    async def cancel_tournament(chat_id: int) -> bool:
        """Cancel a tournament"""
        try:
            tournament = await TournamentHelper.get_active_tournament(chat_id)
            if not tournament:
                return False
            
            await tournaments_col.update_one(
                {"_id": tournament["_id"]},
                {"$set": {"status": "cancelled"}}
            )
            return True
        except Exception as e:
            print(f"Error cancelling tournament: {e}")
            return False


# Turn timer monitoring
_timer_task = None
_timer_running = False
_mongo_error_count = 0
_last_mongo_error_time = None

async def monitor_turn_timers():
    """Background task to monitor and timeout players"""
    global _timer_running, _mongo_error_count, _last_mongo_error_time
    from HasiiMusic import app
    from pyrogram.errors import FloodWait
    
    # Wait for app to be fully started
    await asyncio.sleep(10)
    _timer_running = True
    retry_delay = 5  # Initial retry delay
    
    while _timer_running:
        try:
            # Check if app is connected
            if not app or not hasattr(app, 'send_message'):
                await asyncio.sleep(5)
                continue
            
            # Find all active tournaments
            active_tournaments = await tournaments_col.find({
                "status": "playing",
                "turn_start_time": {"$ne": None}
            }).to_list(length=None)
            
            # Reset retry delay and error count on successful query
            retry_delay = 5
            if _mongo_error_count > 0:
                logger.info("✅ Tournament timer: MongoDB connection restored")
                _mongo_error_count = 0
            
            current_time = datetime.utcnow()
            
            for tournament in active_tournaments:
                turn_start = tournament.get("turn_start_time")
                if not turn_start:
                    continue
                
                # Check if 30 seconds have passed
                elapsed = (current_time - turn_start).total_seconds()
                if elapsed >= 30:
                    # Timeout this player
                    chat_id = tournament["chat_id"]
                    user_id = tournament["current_turn_user_id"]
                    
                    success, round_complete = await TournamentHelper.timeout_player(chat_id, user_id)
                    
                    if success:
                        try:
                            # Notify chat about timeout
                            user = await app.get_users(user_id)
                            
                            if round_complete:
                                # Round complete, ask admin
                                from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                                
                                scoreboard_data = await TournamentHelper.get_scoreboard(chat_id)
                                from HasiiMusic.plugins.features.tournament_admin import format_scoreboard
                                scoreboard_text = await format_scoreboard(scoreboard_data, {}, started=True)
                                
                                keyboard = InlineKeyboardMarkup([
                                    [
                                        InlineKeyboardButton("✅ Next Round", callback_data="tour_next_round"),
                                        InlineKeyboardButton("🏁 End Game", callback_data="tour_end")
                                    ]
                                ])
                                
                                await app.send_message(
                                    chat_id,
                                    f"⏰ {user.mention} timed out! (0 points)\n\n"
                                    f"🎉 <b>ROUND COMPLETE!</b>\n\n"
                                    f"{scoreboard_text}\n\n"
                                    f"🎮 Admin, do you want to play another round?",
                                    reply_markup=keyboard
                                )
                            else:
                                # Turn advanced to next player
                                updated_tournament = await TournamentHelper.get_active_tournament(chat_id)
                                if updated_tournament and updated_tournament.get("current_turn_user_id"):
                                    next_user_id = updated_tournament["current_turn_user_id"]
                                    next_user = await app.get_users(next_user_id)
                                    
                                    # Get game emoji
                                    game_type = updated_tournament["game_type"]
                                    game_emoji = {
                                        "dice": "🎲",
                                        "dart": "🎯",
                                        "basket": "🏀",
                                        "jackpot": "🎰",
                                        "ball": "🎳",
                                        "football": "⚽",
                                        "all": "🎮"
                                    }.get(game_type, "🎮")
                                    
                                    await app.send_message(
                                        chat_id,
                                        f"⏰ {user.mention} timed out! (0 points)\n\n"
                                        f"🎯 {next_user.mention} Your turn!\n"
                                        f"⏱ You have 30 seconds to send {game_emoji}!"
                                    )
                        except FloodWait as fw:
                            # Handle flood wait - just skip this notification
                            logger.warning(f"FloodWait in timer monitor: {fw.value}s")
                            await asyncio.sleep(fw.value)
                        except Exception as e:
                            logger.error(f"Error notifying timeout: {e}")
            
            # Check every 5 seconds
            await asyncio.sleep(retry_delay)
        except asyncio.CancelledError:
            # Task was cancelled, clean exit
            _timer_running = False
            break
        except (pymongo_errors.ServerSelectionTimeoutError, 
                pymongo_errors.AutoReconnect,
                pymongo_errors.NetworkTimeout) as e:
            # MongoDB connection issue - use exponential backoff
            _mongo_error_count += 1
            current_time = datetime.utcnow()
            
            # Only log once per minute to avoid spam
            if (_last_mongo_error_time is None or 
                (current_time - _last_mongo_error_time).total_seconds() > 60):
                logger.warning(
                    f"⚠️ Tournament timer: MongoDB connection issue (attempt {_mongo_error_count}). "
                    f"Will retry with {retry_delay}s delay. This is usually temporary."
                )
                _last_mongo_error_time = current_time
            
            # Exponential backoff: 5s -> 10s -> 20s -> 30s (max)
            retry_delay = min(retry_delay * 2, 30)
            await asyncio.sleep(retry_delay)
        except Exception as e:
            # Other unexpected errors
            logger.error(f"Error in timer monitor: {e}")
            await asyncio.sleep(5)


async def start_timer_monitor():
    """Start the timer monitoring task"""
    global _timer_task, _timer_running
    try:
        if _timer_task is None or _timer_task.done():
            _timer_running = True
            _timer_task = asyncio.create_task(monitor_turn_timers())
            logger.info("✅ Tournament timer monitor started")
    except Exception as e:
        logger.error(f"❌ Failed to start tournament timer: {e}")


def stop_timer_monitor():
    """Stop the timer monitoring task"""
    global _timer_task, _timer_running
    _timer_running = False
    if _timer_task and not _timer_task.done():
        _timer_task.cancel()
        logger.info("🛑 Tournament timer monitor stopped")
    _timer_task = None

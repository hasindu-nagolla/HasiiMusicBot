"""
Tournament Arena Helper Functions
Manages competitive game tournaments with teams, scores, and leaderboards
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from HasiiMusic.core.mongo import db

# Tournament Collections
tournaments_col = db.tournaments
players_col = db.tournament_players
leaderboard_col = db.tournament_leaderboard


class TournamentHelper:
    """Helper class for tournament operations"""

    @staticmethod
    async def create_tournament(
        chat_id: int,
        created_by: int,
        tournament_type: str = "team",  # team, solo, ffa
        game_type: str = "all",  # all, dice, dart, basket, jackpot, ball, football
        max_players: int = 20,
        teams_count: int = 2,
        duration: int = 30  # minutes
    ) -> bool:
        """Create a new tournament"""
        try:
            # Check if active tournament exists
            existing = await tournaments_col.find_one({
                "chat_id": chat_id,
                "status": {"$in": ["pending", "active"]}
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
                "duration": duration,
                "status": "pending",  # pending, active, finished
                "teams": {},  # {team_name: [player_ids]}
                "scores": {},  # {player_id: score}
                "start_time": None,
                "end_time": None,
                "winner": None
            }
            
            # Initialize teams
            team_names = ["🔴 Red Dragons", "🔵 Blue Wolves", "🟢 Green Vipers", "🟡 Yellow Tigers"]
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
            "status": {"$in": ["pending", "active"]}
        })

    @staticmethod
    async def start_tournament(chat_id: int) -> bool:
        """Start a pending tournament"""
        try:
            tournament = await TournamentHelper.get_active_tournament(chat_id)
            if not tournament or tournament["status"] != "pending":
                return False
            
            # Check if at least 2 players joined
            total_players = sum(len(players) for players in tournament["teams"].values())
            if total_players < 2:
                return False
            
            end_time = datetime.utcnow() + timedelta(minutes=tournament["duration"])
            
            await tournaments_col.update_one(
                {"_id": tournament["_id"]},
                {
                    "$set": {
                        "status": "active",
                        "start_time": datetime.utcnow(),
                        "end_time": end_time
                    }
                }
            )
            return True
        except Exception as e:
            print(f"Error starting tournament: {e}")
            return False

    @staticmethod
    async def stop_tournament(chat_id: int) -> Tuple[bool, Optional[Dict]]:
        """Stop active tournament and calculate results"""
        try:
            tournament = await TournamentHelper.get_active_tournament(chat_id)
            if not tournament or tournament["status"] != "active":
                return False, None
            
            # Calculate team scores
            team_scores = {}
            for team_name, player_ids in tournament["teams"].items():
                team_score = sum(
                    tournament["scores"].get(str(pid), 0) for pid in player_ids
                )
                team_scores[team_name] = {
                    "score": team_score,
                    "players": len(player_ids)
                }
            
            # Determine winner
            if tournament["tournament_type"] == "team":
                winner = max(team_scores.items(), key=lambda x: x[1]["score"])[0]
            else:
                winner_id = max(tournament["scores"].items(), key=lambda x: x[1])[0]
                winner = winner_id
            
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
            for team_name, player_ids in tournament["teams"].items():
                if user_id in player_ids:
                    return False, "already_joined"
            
            # Check max players
            total_players = sum(len(players) for players in tournament["teams"].values())
            if total_players >= tournament["max_players"]:
                return False, "max_players"
            
            # Auto-assign to smallest team if team not specified
            if not team or team not in tournament["teams"]:
                team = min(
                    tournament["teams"].items(),
                    key=lambda x: len(x[1])
                )[0]
            
            # Add player to team
            await tournaments_col.update_one(
                {"_id": tournament["_id"]},
                {
                    "$push": {f"teams.{team}": user_id},
                    "$set": {f"scores.{user_id}": 0}
                }
            )
            
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
            
            # Remove from team
            for team_name, player_ids in tournament["teams"].items():
                if user_id in player_ids:
                    await tournaments_col.update_one(
                        {"_id": tournament["_id"]},
                        {
                            "$pull": {f"teams.{team_name}": user_id},
                            "$unset": {f"scores.{user_id}": ""}
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
    ) -> bool:
        """Add score to player in active tournament"""
        try:
            tournament = await TournamentHelper.get_active_tournament(chat_id)
            if not tournament or tournament["status"] != "active":
                return False
            
            # Check if game type matches
            if tournament["game_type"] != "all" and tournament["game_type"] != game_type:
                return False
            
            # Check if player is in tournament
            user_in_tournament = any(
                user_id in players for players in tournament["teams"].values()
            )
            
            if not user_in_tournament:
                return False
            
            # Add score
            await tournaments_col.update_one(
                {"_id": tournament["_id"]},
                {"$inc": {f"scores.{user_id}": score}}
            )
            
            return True
        except Exception as e:
            print(f"Error adding score: {e}")
            return False

    @staticmethod
    async def get_scoreboard(chat_id: int) -> Optional[Dict]:
        """Get current scoreboard"""
        tournament = await TournamentHelper.get_active_tournament(chat_id)
        if not tournament:
            return None
        
        # Calculate team scores
        team_scores = {}
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

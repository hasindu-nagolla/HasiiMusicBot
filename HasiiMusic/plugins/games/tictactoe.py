from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from HasiiMusic import app
from .utils import safe_edit

# Memory store for active games per chat
games = {}

def get_board(board, finished=False):
    keyboard = []
    for i in range(0, 16, 4):
        row = []
        for j in range(4):
            pos = i + j
            text = board[pos] if board[pos] != " " else "➖"
            callback_data = f"ttt_move_{pos}" if not finished else "ttt_ignore"
            row.append(InlineKeyboardButton(text, callback_data=callback_data))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def check_win(b):
    win_combinations = [
        (0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11), (12, 13, 14, 15), # Rows
        (0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15), # Cols
        (0, 5, 10, 15), (3, 6, 9, 12)                                 # Diagonals
    ]
    for combo in win_combinations:
        if b[combo[0]] == b[combo[1]] == b[combo[2]] == b[combo[3]] and b[combo[0]] != " ":
            return True
    return False

@app.on_message(filters.command(["ttt", "tictactoe"]))
async def ttt_start(client, message):
    chat_id = message.chat.id
    
    # Private chat check
    if message.chat.type == "private":
        await message.reply_text("❌ TicTacToe is a multiplayer game and can only be played in groups.")
        return
        
    # Handle Anonymous Admins
    sender_name = message.from_user.first_name if message.from_user else (message.sender_chat.title if message.sender_chat else "Someone")
    
    p1 = None
    if message.from_user:
        p1 = {"id": message.from_user.id, "name": message.from_user.first_name, "symbol": "❌"}

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🎮 Join Game", callback_data="ttt_join")]])
    sent_msg = await message.reply_text(f"🎮 TicTacToe\n\n{sender_name} started a new game! Waiting for opponents...", reply_markup=keyboard)
    
    game_id = f"{chat_id}_{sent_msg.id}"
    games[game_id] = {
        "board": [" "] * 16,
        "p1": p1,
        "p2": None,
        "turn": "p1",
        "status": "waiting"
    }


@app.on_callback_query(filters.regex("^ttt_"))
async def ttt_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    msg_id = callback_query.message.id
    game_id = f"{chat_id}_{msg_id}"
    
    if data == "ttt_ignore":
        await callback_query.answer()
        return

    if game_id not in games:
        await callback_query.answer("This game is no longer active.", show_alert=True)
        return
        
    game = games[game_id]
    
    import time
    now = time.time()
    if now - game.get("last_click_time", 0) < 0.8:
        await callback_query.answer("Please don't click so fast!", show_alert=False)
        return
    game["last_click_time"] = now
    
    if data == "ttt_join":
        if game["status"] != "waiting":
            await callback_query.answer("Game already started!", show_alert=True)
            return
            
        if game["p1"] is None:
            # Anonymous admin (or someone else) claiming p1 spot
            game["p1"] = {"id": user_id, "name": callback_query.from_user.first_name, "symbol": "❌"}
            await callback_query.answer("You joined as Player 1 (❌)!")
            
            # Still waiting for p2
            await safe_edit(callback_query.message, text=f"🎮 TicTacToe\n\n❌ {game['p1']['name']} is waiting for an opponent...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎮 Join Game", callback_data="ttt_join")]])
            )
            
        # P2 joins
        game["p2"] = {"id": user_id, "name": callback_query.from_user.first_name, "symbol": "⭕"}
        game["status"] = "playing"
        
        await safe_edit(callback_query.message, text=f"🎮 TicTacToe\n\n❌ {game['p1']['name']}\n⭕ {game['p2']['name']}\n\nIt's {game['p1']['name']}'s turn!", reply_markup=get_board(game["board"])
        )
        return
        
    # Handling moves
    if data.startswith("ttt_move_"):
        if game["status"] != "playing":
            await callback_query.answer("Game is not active.", show_alert=True)
            return
            
        is_p1 = user_id == game["p1"]["id"]
        is_p2 = user_id == game["p2"]["id"]
        
        if not (is_p1 or is_p2):
            await callback_query.answer("You are not playing this game!", show_alert=True)
            return
            
        current_turn_key = game["turn"]
        if user_id != game[current_turn_key]["id"]:
            await callback_query.answer("It's not your turn!", show_alert=True)
            return
            
        pos = int(data.split("_")[2])
        if game["board"][pos] != " ":
            await callback_query.answer("That spot is already taken!", show_alert=True)
            return
            
        # Make the move
        game["board"][pos] = game[current_turn_key]["symbol"]
        
        # Check win/draw
        if check_win(game["board"]):
            game["status"] = "finished"
            await safe_edit(callback_query.message, text=f"🏆 Game Over!\n\n{game[current_turn_key]['name']} ({game[current_turn_key]['symbol']}) won the game!", reply_markup=get_board(game["board"], finished=True)
            )
            del games[game_id]
            return
            
        if " " not in game["board"]:
            game["status"] = "finished"
            await safe_edit(callback_query.message, text=f"🤝 Game Over!\n\nIt's a draw between {game['p1']['name']} and {game['p2']['name']}!", reply_markup=get_board(game["board"], finished=True)
            )
            del games[game_id]
            return
            
        # Next turn
        game["turn"] = "p2" if game["turn"] == "p1" else "p1"
        next_player = game[game["turn"]]
        
        await safe_edit(callback_query.message, text=f"🎮 TicTacToe\n\n❌ {game['p1']['name']}\n⭕ {game['p2']['name']}\n\nIt's {next_player['name']}'s turn!", reply_markup=get_board(game["board"])
        )

import time
import chess
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified
from HasiiMusic import app

games = {}

def get_chess_board(board, selected_sq=-1, finished=False):
    chars = {
        "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
        "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚",
    }
    keyboard = []
    # Render from rank 7 (top) down to rank 0 (bottom)
    for r in range(7, -1, -1):
        row = []
        for c in range(8):
            sq = r * 8 + c
            
            if sq == selected_sq:
                text = "🟡"
            else:
                piece = board.piece_at(sq)
                if piece:
                    text = chars[piece.symbol()]
                else:
                    text = " "
                    
            cb = f"chs_{sq}" if not finished else "chs_ignore"
            row.append(InlineKeyboardButton(text, callback_data=cb))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

@app.on_message(filters.command(["chess"]))
async def chess_start(client, message):
    chat_id = message.chat.id
    
    if message.chat.type == "private":
        await message.reply_text("❌ Chess is a multiplayer game and can only be played in groups.")
        return
        
    sender_name = message.from_user.first_name if message.from_user else (message.sender_chat.title if message.sender_chat else "Someone")
    
    p1 = None
    if message.from_user:
        p1 = {"id": message.from_user.id, "name": message.from_user.first_name, "symbol": "⚪️"}

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🎮 Join Game", callback_data="chs_join")]])
    sent_msg = await message.reply_text(f"♟️ Chess\n\n{sender_name} started a new game! Waiting for opponents...", reply_markup=keyboard)

    game_id = f"{chat_id}_{sent_msg.id}"
    games[game_id] = {
        "board": chess.Board(),
        "p1": p1,
        "p2": None,
        "selected_sq": -1,
        "status": "waiting"
    }


@app.on_callback_query(filters.regex("^chs_"))
async def chess_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    msg_id = callback_query.message.id
    game_id = f"{chat_id}_{msg_id}"
    
    if data == "chs_ignore":
        await callback_query.answer()
        return

    if game_id not in games:
        await callback_query.answer("This game is no longer active.", show_alert=True)
        return
        
    game = games[game_id]
    
    # Anti-spam rate limit
    now = time.time()
    if now - game.get("last_click_time", 0) < 0.8:
        await callback_query.answer("Please don't click so fast!", show_alert=False)
        return
    game["last_click_time"] = now
    
    if data == "chs_join":
        if game["status"] != "waiting":
            await callback_query.answer("Game already started!", show_alert=True)
            return
            
        if game["p1"] is None:
            game["p1"] = {"id": user_id, "name": callback_query.from_user.first_name, "symbol": "⚪️"}
            await callback_query.answer("You joined as White (⚪️)!")
            await callback_query.message.edit_text(
                f"♟️ Chess\n\n⚪️ {game['p1']['name']} is waiting for an opponent...",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎮 Join Game", callback_data="chs_join")]])
            )
            return
            
        game["p2"] = {"id": user_id, "name": callback_query.from_user.first_name, "symbol": "⚫️"}
        game["status"] = "playing"
        
        await callback_query.message.edit_text(
            f"♟️ Chess\n\n⚪️ {game['p1']['name']}\n⚫️ {game['p2']['name']}\n\nIt's {game['p1']['name']}'s turn!",
            reply_markup=get_chess_board(game["board"])
        )
        return
        
    # Handling moves
    if game["status"] != "playing":
        await callback_query.answer("Game is not active.", show_alert=True)
        return
        
    is_p1 = user_id == game["p1"]["id"]
    is_p2 = user_id == game["p2"]["id"]
    
    if not (is_p1 or is_p2):
        await callback_query.answer("You are not playing this game!", show_alert=True)
        return
        
    board = game["board"]
    is_white_turn = board.turn == chess.WHITE
    
    if is_white_turn and not is_p1:
        await callback_query.answer("It's White's turn!", show_alert=True)
        return
    if not is_white_turn and not is_p2:
        await callback_query.answer("It's Black's turn!", show_alert=True)
        return
        
    pos = int(data.split("_")[1])

    # Step 1: Selecting a piece
    if game["selected_sq"] == -1:
        piece = board.piece_at(pos)
        if not piece:
            await callback_query.answer("Select a piece to move!", show_alert=True)
            return
            
        is_white_piece = piece.color == chess.WHITE
        if (is_p1 and not is_white_piece) or (is_p2 and is_white_piece):
            await callback_query.answer("That is not your piece!", show_alert=True)
            return
            
        game["selected_sq"] = pos
        await callback_query.message.edit_reply_markup(reply_markup=get_chess_board(board, selected_sq=pos))
        return

    # Step 2: Selecting destination or changing selection
    src = game["selected_sq"]
    
    # If clicked own piece again, change selection or unselect
    piece = board.piece_at(pos)
    if piece:
        is_white_piece = piece.color == chess.WHITE
        if (is_p1 and is_white_piece) or (is_p2 and not is_white_piece):
            if game["selected_sq"] == pos:
                game["selected_sq"] = -1
                await callback_query.message.edit_reply_markup(reply_markup=get_chess_board(board))
            else:
                game["selected_sq"] = pos
                await callback_query.message.edit_reply_markup(reply_markup=get_chess_board(board, selected_sq=pos))
            return
            
    # Try to move
    move = chess.Move(src, pos)
    
    # Auto Queen Promotion
    src_piece = board.piece_at(src)
    if src_piece and src_piece.piece_type == chess.PAWN:
        if (src_piece.color == chess.WHITE and pos // 8 == 7) or \
           (src_piece.color == chess.BLACK and pos // 8 == 0):
            move.promotion = chess.QUEEN
            
    if move not in board.legal_moves:
        await callback_query.answer("Invalid move! Check the rules or see if you're in Check.", show_alert=True)
        game["selected_sq"] = -1
        await callback_query.message.edit_reply_markup(reply_markup=get_chess_board(board))
        return
        
    # Execute move
    board.push(move)
    game["selected_sq"] = -1
    
    # Check Game Over
    if board.is_checkmate():
        game["status"] = "finished"
        winner = game["p1"] if board.turn == chess.BLACK else game["p2"]
        await callback_query.message.edit_text(
            f"🏆 Checkmate!\n\n{winner['name']} ({winner['symbol']}) won the game!",
            reply_markup=get_chess_board(board, finished=True)
        )
        del games[game_id]
        return
        
    if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves():
        game["status"] = "finished"
        await callback_query.message.edit_text(
            f"🤝 Draw!\n\nThe game ended in a draw.",
            reply_markup=get_chess_board(board, finished=True)
        )
        del games[game_id]
        return
        
    # Check
    check_text = "\n\n⚠️ **CHECK!**" if board.is_check() else ""
    
    next_player = game["p1"] if board.turn == chess.WHITE else game["p2"]
    
    await callback_query.message.edit_text(
        f"♟️ Chess\n\n⚪️ {game['p1']['name']}\n⚫️ {game['p2']['name']}\n\nIt's {next_player['name']}'s turn!{check_text}",
        reply_markup=get_chess_board(board)
    )

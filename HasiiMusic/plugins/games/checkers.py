import time
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified
from HasiiMusic import app

games = {}

# Constants
EMPTY_INVALID = -1
EMPTY_VALID = 0
P1_MAN = 1
P2_MAN = 2
P1_KING = 3
P2_KING = 4

def init_board():
    board = []
    for r in range(8):
        for c in range(8):
            if (r + c) % 2 == 1:
                if r < 3:
                    board.append(P2_MAN)
                elif r > 4:
                    board.append(P1_MAN)
                else:
                    board.append(EMPTY_VALID)
            else:
                board.append(EMPTY_INVALID)
    return board

def get_checkers_board(board, selected_pos=-1, finished=False):
    chars = {
        EMPTY_INVALID: " ",
        EMPTY_VALID: " ",
        P1_MAN: "🔴",
        P2_MAN: "⚪️",
        P1_KING: "🟥",
        P2_KING: "⬜️",
        "selected": "🟡"
    }
    keyboard = []
    for r in range(8):
        row = []
        for c in range(8):
            pos = r * 8 + c
            text = chars["selected"] if pos == selected_pos else chars[board[pos]]
            cb = f"chk_{pos}" if not finished and board[pos] != EMPTY_INVALID else "chk_ignore"
            row.append(InlineKeyboardButton(text, callback_data=cb))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def get_jumps_for_piece(board, src, player):
    jumps = []
    piece = board[src]
    if piece in (EMPTY_VALID, EMPTY_INVALID): return []
    is_king = piece in (P1_KING, P2_KING)
    
    r, c = src // 8, src % 8
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    
    if is_king:
        for dr, dc in directions:
            curr_r, curr_c = r + dr, c + dc
            jumped_pos = -1
            while 0 <= curr_r < 8 and 0 <= curr_c < 8:
                pos = curr_r * 8 + curr_c
                p = board[pos]
                if p != EMPTY_VALID:
                    if jumped_pos != -1:
                        break # Cannot jump two pieces in a row
                    is_p1 = player == 1
                    p_is_p1 = p in (P1_MAN, P1_KING)
                    if is_p1 == p_is_p1:
                        break # Blocked by own piece
                    else:
                        jumped_pos = pos # Opponent piece found
                else:
                    if jumped_pos != -1:
                        jumps.append(pos) # Valid landing spot after jump
                curr_r += dr
                curr_c += dc
    else:
        if player == 1:
            directions = [(-1, -1), (-1, 1)] # P1 moves UP (-)
        else:
            directions = [(1, -1), (1, 1)]   # P2 moves DOWN (+)
            
        for dr, dc in directions:
            jump_r, jump_c = r + dr, c + dc
            land_r, land_c = r + 2*dr, c + 2*dc
            
            if 0 <= land_r < 8 and 0 <= land_c < 8:
                jump_pos = jump_r * 8 + jump_c
                land_pos = land_r * 8 + land_c
                
                if board[land_pos] == EMPTY_VALID:
                    jumped_piece = board[jump_pos]
                    if jumped_piece not in (EMPTY_VALID, EMPTY_INVALID):
                        jumped_is_p1 = jumped_piece in (P1_MAN, P1_KING)
                        is_p1 = player == 1
                        if is_p1 != jumped_is_p1: # Opponent's piece
                            jumps.append(land_pos)
    return jumps

def has_any_jumps(board, player):
    for i in range(64):
        piece = board[i]
        if piece not in (EMPTY_VALID, EMPTY_INVALID):
            is_p1 = piece in (P1_MAN, P1_KING)
            if (player == 1 and is_p1) or (player == 2 and not is_p1):
                if get_jumps_for_piece(board, i, player):
                    return True
    return False

def is_valid_move(board, src, dst, player):
    # player: 1 for P1, 2 for P2
    piece = board[src]
    if piece in (EMPTY_VALID, EMPTY_INVALID): return False, False, -1
    is_p1 = piece in (P1_MAN, P1_KING)
    if (player == 1 and not is_p1) or (player == 2 and is_p1): return False, False, -1
    if board[dst] != EMPTY_VALID: return False, False, -1

    r1, c1 = src // 8, src % 8
    r2, c2 = dst // 8, dst % 8
    dr = r2 - r1
    dc = c2 - c1

    if abs(dr) != abs(dc): return False, False, -1

    is_king = piece in (P1_KING, P2_KING)
    
    step_r = 1 if dr > 0 else -1
    step_c = 1 if dc > 0 else -1

    if is_king:
        # Check all squares between src and dst
        curr_r, curr_c = r1 + step_r, c1 + step_c
        jumped_count = 0
        jump_pos = -1
        while curr_r != r2 and curr_c != c2:
            pos = curr_r * 8 + curr_c
            p = board[pos]
            if p != EMPTY_VALID:
                is_p1 = player == 1
                p_is_p1 = p in (P1_MAN, P1_KING)
                if is_p1 == p_is_p1:
                    return False, False, -1 # Blocked by own piece
                else:
                    jumped_count += 1
                    jump_pos = pos
            curr_r += step_r
            curr_c += step_c
            
        if jumped_count > 1: return False, False, -1 # Cannot jump over 2 pieces in one line
        
        if jumped_count == 1:
            return True, True, jump_pos
        else:
            return True, False, -1
    else:
        # Simple move
        if abs(dr) == 1:
            if player == 1 and dr > 0: return False, False, -1 # P1 moves UP (-)
            if player == 2 and dr < 0: return False, False, -1 # P2 moves DOWN (+)
            return True, False, -1

        # Capture move
        if abs(dr) == 2:
            jump_pos = (r1 + dr // 2) * 8 + (c1 + dc // 2)
            jumped_piece = board[jump_pos]
            if jumped_piece in (EMPTY_VALID, EMPTY_INVALID): return False, False, -1
            jumped_is_p1 = jumped_piece in (P1_MAN, P1_KING)
            if (player == 1) == jumped_is_p1: return False, False, -1
            return True, True, jump_pos

    return False, False, -1

def check_win(board):
    p1_pieces = sum(1 for p in board if p in (P1_MAN, P1_KING))
    p2_pieces = sum(1 for p in board if p in (P2_MAN, P2_KING))
    if p1_pieces == 0: return 2
    if p2_pieces == 0: return 1
    return 0

@app.on_message(filters.command(["daam", "checkers"]))
async def chk_start(client, message):
    chat_id = message.chat.id
    
    if message.chat.type == "private":
        await message.reply_text("❌ Checkers is a multiplayer game and can only be played in groups.")
        return
        
    sender_name = message.from_user.first_name if message.from_user else (message.sender_chat.title if message.sender_chat else "Someone")
    
    p1 = None
    if message.from_user:
        p1 = {"id": message.from_user.id, "name": message.from_user.first_name, "symbol": "🔴"}

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🎮 Join Game", callback_data="chk_join")]])
    sent_msg = await message.reply_text(f"🎮 Checkers\n\n{sender_name} started a new game! Waiting for opponents...", reply_markup=keyboard)
    
    game_id = f"{chat_id}_{sent_msg.id}"
    games[game_id] = {
        "board": init_board(),
        "p1": p1,
        "p2": None,
        "turn": "p1",
        "selected_pos": -1,
        "status": "waiting"
    }


@app.on_callback_query(filters.regex("^chk_"))
async def chk_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    msg_id = callback_query.message.id
    game_id = f"{chat_id}_{msg_id}"
    
    if data == "chk_ignore":
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
    
    if data == "chk_join":
        if game["status"] != "waiting":
            await callback_query.answer("Game already started!", show_alert=True)
            return
            
        if game["p1"] is None:
            game["p1"] = {"id": user_id, "name": callback_query.from_user.first_name, "symbol": "🔴"}
            await callback_query.answer("You joined as Player 1 (🔴)!")
            await callback_query.message.edit_text(
                f"🎮 Checkers\n\n🔴 {game['p1']['name']} is waiting for an opponent...",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎮 Join Game", callback_data="chk_join")]])
            )
            return
            
        game["p2"] = {"id": user_id, "name": callback_query.from_user.first_name, "symbol": "⚪️"}
        game["status"] = "playing"
        
        await callback_query.message.edit_text(
            f"🎮 Checkers\n\n🔴 {game['p1']['name']}\n⚪️ {game['p2']['name']}\n\nIt's {game['p1']['name']}'s turn!",
            reply_markup=get_checkers_board(game["board"])
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
        
    current_turn_key = game["turn"]
    if user_id != game[current_turn_key]["id"]:
        await callback_query.answer("It's not your turn!", show_alert=True)
        return
        
    pos = int(data.split("_")[1])
    board = game["board"]
    player_num = 1 if current_turn_key == "p1" else 2

    # Step 1: Selecting a piece
    forced_piece = game.get("must_jump_with", -1)
    
    if game["selected_pos"] == -1:
        piece = board[pos]
        if piece in (EMPTY_VALID, EMPTY_INVALID):
            await callback_query.answer("Select one of your pieces first!", show_alert=True)
            return
        is_piece_p1 = piece in (P1_MAN, P1_KING)
        if (player_num == 1 and not is_piece_p1) or (player_num == 2 and is_piece_p1):
            await callback_query.answer("That is not your piece!", show_alert=True)
            return
            
        if forced_piece != -1 and pos != forced_piece:
            await callback_query.answer("You must continue jumping with the selected piece!", show_alert=True)
            return
            
        if forced_piece == -1 and has_any_jumps(board, player_num):
            if not get_jumps_for_piece(board, pos, player_num):
                await callback_query.answer("You have a mandatory capture! Select a piece that can jump.", show_alert=True)
                return
                
        game["selected_pos"] = pos
        await callback_query.message.edit_reply_markup(reply_markup=get_checkers_board(board, selected_pos=pos))
        return

    # Step 2: Selecting destination or changing selection
    src = game["selected_pos"]
    
    # If clicked on own piece again, change selection or unselect
    piece = board[pos]
    if piece not in (EMPTY_VALID, EMPTY_INVALID):
        is_piece_p1 = piece in (P1_MAN, P1_KING)
        if (player_num == 1 and is_piece_p1) or (player_num == 2 and not is_piece_p1):
            if forced_piece != -1:
                await callback_query.answer("You must finish your multiple jump!", show_alert=True)
                return
                
            if game["selected_pos"] == pos:
                # Unselect if clicking the same piece
                game["selected_pos"] = -1
                await callback_query.message.edit_reply_markup(reply_markup=get_checkers_board(board))
            else:
                if has_any_jumps(board, player_num) and not get_jumps_for_piece(board, pos, player_num):
                    await callback_query.answer("You have a mandatory capture! Select a piece that can jump.", show_alert=True)
                    return
                # Change selection to the new piece
                game["selected_pos"] = pos
                await callback_query.message.edit_reply_markup(reply_markup=get_checkers_board(board, selected_pos=pos))
            return

    # Try to move
    valid, is_capture, jump_pos = is_valid_move(board, src, pos, player_num)
    if not valid:
        await callback_query.answer("Invalid move!", show_alert=True)
        game["selected_pos"] = -1 if forced_piece == -1 else forced_piece
        await callback_query.message.edit_reply_markup(reply_markup=get_checkers_board(board, selected_pos=game["selected_pos"]))
        return
        
    if forced_piece == -1 and not is_capture and has_any_jumps(board, player_num):
        await callback_query.answer("You must capture an opponent's piece!", show_alert=True)
        game["selected_pos"] = -1
        await callback_query.message.edit_reply_markup(reply_markup=get_checkers_board(board))
        return

    # Execute move
    board[pos] = board[src]
    board[src] = EMPTY_VALID
    if is_capture:
        board[jump_pos] = EMPTY_VALID

    # King promotion
    promoted = False
    if player_num == 1 and pos // 8 == 0 and board[pos] == P1_MAN:
        board[pos] = P1_KING
        promoted = True
    elif player_num == 2 and pos // 8 == 7 and board[pos] == P2_MAN:
        board[pos] = P2_KING
        promoted = True

    game["selected_pos"] = -1

    # Check win
    winner = check_win(board)
    if winner != 0:
        game["status"] = "finished"
        win_player = game["p1"] if winner == 1 else game["p2"]
        await callback_query.message.edit_text(
            f"🏆 Game Over!\n\n{win_player['name']} ({win_player['symbol']}) won the Checkers game!",
            reply_markup=get_checkers_board(board, finished=True)
        )
        del games[game_id]
        return
        
    # Check for multiple jumps
    if is_capture and not promoted:
        further_jumps = get_jumps_for_piece(board, pos, player_num)
        if further_jumps:
            game["selected_pos"] = pos
            game["must_jump_with"] = pos
            await callback_query.message.edit_text(
                f"🎮 Checkers\n\n🔴 {game['p1']['name']}\n⚪️ {game['p2']['name']}\n\nIt's {game[game['turn']]['name']}'s turn! You must jump again.",
                reply_markup=get_checkers_board(board, selected_pos=pos)
            )
            return

    # Change turn
    game["must_jump_with"] = -1
    game["turn"] = "p2" if game["turn"] == "p1" else "p1"
    next_player = game[game["turn"]]
    
    await callback_query.message.edit_text(
        f"🎮 Checkers\n\n🔴 {game['p1']['name']}\n⚪️ {game['p2']['name']}\n\nIt's {next_player['name']}'s turn!",
        reply_markup=get_checkers_board(board)
    )

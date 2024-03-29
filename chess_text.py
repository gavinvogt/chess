"""
File: chess_text.py
Author: Gavin Vogt
This program lets the user play text-based chess.
"""

# dependencies
import traceback

# my code
from model import ChessGame, BoardState
from model.moves import Move


def attempt_move(game: ChessGame, board: BoardState, move: Move):
    """
    Attempts to make the given move on the board. If successful, adds
    the new board to the game.
    game: ChessGame representing the game
    board: BoardState representing the current board
    move: Move representing the move to make
    Return: True if move made successfully, False otherwise
    """
    piece = board.get_piece(move.start.row, move.start.col)
    if piece is not None and piece.can_move(board, move):
        # Try to make the move
        try:
            board = board.make_move(move)
        except Exception:
            print("bad:")
            traceback.print_exc()
        else:
            # Move was successful
            game.push(board)
            return True
    else:
        print("Invalid move!")
    return False


def main():
    print("CHESS! Text version, written by Gavin Vogt\n")

    # Create the chess game and starting position
    game = ChessGame()
    board = BoardState()
    game.push(board)

    board.print_board()
    move_str = ""
    while True:
        # Get the move
        if board.white_to_move():
            color_char = "w"
        else:
            color_char = "b"
        move_str = input(f"Move ({board.fullmove()}{color_char}): ")
        upper_move = move_str.strip().upper()
        if upper_move == "FEN":
            print(board.to_fen())
            continue
        elif upper_move in ("QUIT", "EXIT"):
            print("Goodbye!")
            return
        move = board.parse_move(move_str)
        if move is not None and attempt_move(game, board, move):
            # Update the board reference and print new state
            board = game.current_state()
            board.print_board()
            result = game.get_result()
            if result is not None:
                print(result.get_type())
                print("due to", result.get_reason())
                print("Score:", result.score_string())
                break
        else:
            print("Invalid move!")

    play_again = input("\nPlay again? ").strip().lower()
    if play_again.startswith("y"):
        print()
        main()


if __name__ == "__main__":
    main()

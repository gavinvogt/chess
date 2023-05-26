"""
File: test.py
Author: Gavin Vogt
This program tests a chess board
"""

import traceback
from model.board_state import BoardState
from model.coordinate import Coordinate
import model.moves as moves


def test_get_moves():
    # TODO: test the piece.get_moves(board, start_coords) function

    board = BoardState()
    start = Coordinate.from_notation("g1")
    knight = board.get_piece(start.row, start.col)
    print(knight)
    print("can move:", knight.can_move(board, Coordinate.from_notation("f3")))
    print(knight.get_moves(board, start))


def test_parser():
    """
    Tests the move parser
    """
    board = BoardState()
    print("\nVALID MOVES (naive):")
    for move_str in (
        "e4",
        "e2-e3",
        "e2-e4",
        "Nf3",
        "Ngf3",
        "N1f3",
        "Ng1 f3",
        "Nc3",
        "0-0",
        "0-0-0",
    ):
        move = board.parse_move(move_str)
        piece = board.get_piece(move.start.row, move.start.col)
        print(move_str, ": ", move, ", ", piece)

    print("\nINVALID MOVES:")
    for move_str in ("Ng3", "Nbf3", "Ng2 f3", "Bc4", "Nc6", "Ke2"):
        move = board.parse_move(move_str)
        print(move_str, ": ", move)


SAMPLE_GAME = """e4 e5 Nf3 f6 Nxe5 fxe5 Qh5+ Ke7 Qxe5+
Kf7 Bc4+ d5 Bxd5+ Kg6 h4 h5 Bxb7 Bxb7 Qf5+ Kh6
d4+ g5 Qf7 Qe7 hxg5+ Qxg5 Rxh5#"""


def main():
    board = BoardState()
    board.print_board()
    # move = input(f"Move ({board._fullmove_number}): ")
    # while move != 'quit':
    for move in [
        "e2-e4",
        "d7-d5",
        "g1-f3",
        "b8-c6",
        "f1-b5",
        "c8-g4",
        "0-0",
        "d8-d6",
        "b5-c6",
        "0-0-0",
    ]:
        print("Move:", move)
        if move == "0-0":
            move = moves.KingsideCastle(board.white_to_move())
            piece = board.get_king()
        elif move == "0-0-0":
            move = moves.QueensideCastle(board.white_to_move())
            piece = board.get_king()
        else:
            start, target = move.split("-")
            start, target = Coordinate.from_notation(start), Coordinate.from_notation(
                target
            )
            print("Basic move:", start, target)
            piece = board.get_piece(start.row, start.col)
            move = moves.BasicMove(start, target)
        if piece is not None and piece.can_move(board, move):
            try:
                board = board.make_move(move)
            except Exception:
                print("bad:")
                traceback.print_exc()
        else:
            print("Invalid move!")
        board.print_board()
        # move = input(f"Move ({board._fullmove_number}): ")


if __name__ == "__main__":
    test_parser()
    # main()

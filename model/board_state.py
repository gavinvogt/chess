'''
File: board_state.py
Author: Gavin Vogt
This program defines the BoardState class for a game of chess
'''

# dependencies
import re
from copy import deepcopy

# my code
from . import pieces
from . import moves
from .coordinate import Coordinate

class BoardState:
    '''
    This class represents the board state for a game of chess.

    Useful methods:
      - white_to_move()
      - make_move()
      - is_valid_state()
      - get_piece()
      - find_king()
      - to_fen()
      - print_board()
      - copy()
    '''

    __slots__ = ('_grid', '_turn', '_w_kingside', '_w_queenside', '_b_kingside', '_b_queenside',
                 '_en_passant_target', '_set_passant_this_turn', '_halfmove_clock', '_fullmove_number')

    def __init__(self, fen_record='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'):
        '''
        Constructs a new board state
        fen_record: str, representing the state of the game (defaults to new game)
        '''
        # Load the pieces on the board
        info = fen_record.split()
        self._board_from_fen(info[0])

        # Active color
        if info[1] == 'w':
            self._turn = True
        elif info[1] == 'b':
            self._turn = False

        # Castling availability
        for char in info[2]:
            if char == 'K':
                self._w_kingside = True
            elif char == 'k':
                self._b_kingside = True
            elif char == 'Q':
                self._w_queenside = True
            elif char == 'q':
                self._b_queenside = True

        # En passant target
        if info[3] == '-':
            self._en_passant_target = None
        else:
            self._en_passant_target = info[3]
        self._set_passant_this_turn = False

        # Halfmove clock
        self._halfmove_clock = int(info[4])

        # Fullmove number
        self._fullmove_number = int(info[5])

    def __eq__(self, other):
        '''
        Checks if two board states are equal.

        Two positions are by definition "the same" if the same types of pieces
        occupy the same squares, the same player has the move, the remaining
        castling rights are the same and the possibility to capture en passant
        is the same. ~ https://en.wikipedia.org/wiki/Threefold_repetition

        Return: True if board states are the same, False otherwise
        '''
        if isinstance(other, self.__class__):
            if self._turn != other._turn:
                # Wrong player turn
                return False
            if (self._w_kingside != other._w_kingside) \
                    or (self._w_queenside != other._w_queenside) \
                    or (self._b_kingside != other._b_kingside) \
                    or (self._b_queenside != other._b_queenside):
                # Castling rights don't match
                return False
            if self._en_passant_target != other._en_passant_target:
                # En-passant targets don't match
                return False
            for piece1, piece2 in zip(self._grid, other._grid):
                if piece1 != piece2:
                    # Pieces on same square don't match
                    return False
            return True
        else:
            return NotImplemented

    def white_to_move(self):
        '''
        Checks if it is white's turn to move
        Return: bool, representing if it is white to move
        '''
        return self._turn

    def halfmove(self):
        '''
        Getter for the halfmove clock number (number of moves since last pawn
        advance or capture)
        '''
        return self._halfmove_clock

    def fullmove(self):
        '''
        Getter for the fullmove number
        '''
        return self._fullmove_number

    def can_castle_kingside(self):
        '''
        Checks if the current player can castle kingside.
        Return: True if can castle kingside, False otherwise
        '''
        # Check inherent castling availability
        if self._turn:
            available = self._w_kingside
            rank = 1
        else:
            available = self._b_kingside
            rank = 8
        if not available:
            return False

        # Check if the king or squares between it and the rook are under attack / occupied
        if self.under_attack(Coordinate.from_coords(rank, 5), not self._turn):
            # king in check
            return False
        targets = (Coordinate.from_coords(rank, 6),  # f1 / f8
                   Coordinate.from_coords(rank, 7))  # g1 / g8
        for target in targets:
            if self._grid[target.row - 1][target.col - 1] is not None \
                    or self.under_attack(target, not self._turn):
                # square occupied / under threat
                return False
        return True

    def can_castle_queenside(self):
        '''
        Checks if the current player can castle queenside.
        Return: True if can castle queenside, False otherwise
        '''
        # Check inherent castling availability
        if self._turn:
            availabile = self._w_queenside
            rank = 1
        else:
            availabile = self._b_queenside
            rank = 8
        if not availabile:
            return False

        # Check if the king or squares between it and the rook are under attack / occupied
        if self.under_attack(Coordinate.from_coords(5, rank), not self._turn):
            # king in check
            return False
        targets = (Coordinate.from_coords(rank, 4),  # d1 / d8
                   Coordinate.from_coords(rank, 3),  # c1 / c8
                   Coordinate.from_coords(rank, 2))  # b1 / b8
        for target in targets:
            if self._grid[target.row - 1][target.col - 1] is not None \
                    or self.under_attack(target, not self._turn):
                # square occupied / under threat
                return False
        return True

    def en_passant_coords(self):
        '''
        Gets the coordinates for the en-passant target
        Return: Coordinate holding the valid en-passant square, or None
        if there is no valid square.
        '''
        if self._en_passant_target is None:
            # no target
            return None
        else:
            # has a target
            return Coordinate.from_notation(self._en_passant_target)

    def set_en_passant(self, coords):
        '''
        Sets the coordinates for the en-passant target
        coords: Coordinate holding the valid en-passant square, or None
        if there is no valid square.
        '''
        if coords is None:
            # no target
            self._en_passant_target = None
        else:
            # has a target
            self._en_passant_target = coords.to_notation()
        self._set_passant_this_turn = True

    def make_move(self, move):
        '''
        Makes the given move. Raises an exception if the move was not valid.
        Return: new BoardState if the move was valid
        '''
        new_state = move.execute(self.copy())
        new_state._update_state(move)
        if new_state.is_valid_state():
            return new_state
        else:
            raise moves.InvalidMoveException("Invalid move: king is in check")

    def is_checkmate(self):
        '''
        Checks if the current player is in checkmate
        Return: True if the current player is in checkmate, False otherwise
        '''
        # King in check with no legal moves
        return self.in_check() and not self._any_legal_moves()

    def is_fifty_move_rule(self):
        '''
        Checks if the game just ended in a draw due to the fifty-move rule.
        Return: True if draw, False otherwise
        '''
        return (self._halfmove_clock >= 50)

    def is_stalemate(self):
        '''
        Checks if the game just ended in a draw due to stalemate.
        Return: True if draw, False otherwise
        '''
        # King not in check, but no legal moves
        return (not self.in_check()) and (not self._any_legal_moves())

    def _any_legal_moves(self):
        '''
        Checks if the current player has any legal moves
        Return: True if the player has legal moves, and False otherwise
        '''
        # Check all pieces of current color for legal moves
        for row in range(8):
            for col in range(8):
                piece = self._grid[row][col]
                if piece is not None and piece.is_white() == self._turn:
                    # Check if this piece has any legal moves
                    legal_moves = piece.get_moves(self, Coordinate.from_coords(row + 1, col + 1))
                    if len(legal_moves) > 0:
                        return True

        # No legal moves were found
        return False

    def insufficient_material(self):
        '''
        Checks if the game just ended in a draw due to insufficient material.
        WARNING: USES (modified) USCF STANDARD.
        Return: True if draw, False otherwise
        '''
        #              [B, N]
        white_counts = [0, 0]
        black_counts = [0, 0]

        # Get the piece counts for each player
        for row in self._grid:
            for piece in row:
                if piece is not None and type(piece) != pieces.King:
                    piece_type = type(piece)
                    if piece_type in (pieces.Queen, pieces.Rook, pieces.Pawn):
                        # Queen, rook, or pawn = not insufficient material
                        return False
                    elif piece_type == pieces.Bishop:
                        # Piece is a bishop
                        i = 0
                    else:
                        # Piece is a knight
                        i = 1
                    if piece.is_white():
                        white_counts[i] += 1
                    else:
                        black_counts[i] += 1
        if sum(white_counts) <= 1 and sum(black_counts) <= 1:
            # Both players have at most one minor piece
            return True
        elif white_counts[0] == 0 and white_counts[1] == 2 and sum(black_counts) == 0:
            # White has two knights against lone king
            return True
        elif black_counts[0] == 0 and black_counts[1] == 2 and sum(white_counts) == 0:
            # Black has two knights against lone king
            return True

        # Failed to find insufficient material
        return False

    def _update_state(self, move):
        '''
        Updates the state variables for this board state
        move: Move that was previously executed to create this board state
        '''
        # Update turn info
        self._turn = not self._turn
        if self._turn:
            self._fullmove_number += 1

        # Update halfmove clock
        if move.was_capture() or move.was_pawn_advance():
            self._halfmove_clock = 0
        else:
            self._halfmove_clock += 1

        # Update castling info
        self._update_castling()

        # Update en-passant target
        if not self._set_passant_this_turn:
            self._en_passant_target = None
        self._set_passant_this_turn = False

    def _update_castling(self):
        '''
        Updates the castling information for this board state
        '''
        # Update white castling
        king = self.get_piece(1, 5)
        k_rook = self.get_piece(1, 8)
        q_rook = self.get_piece(1, 1)
        king_bad = (king is None) or (not king.is_white()) or (type(king) != pieces.King)
        k_rook_bad = (k_rook is None) or (not k_rook.is_white()) or (type(k_rook) != pieces.Rook)
        q_rook_bad = (q_rook is None) or (not q_rook.is_white()) or (type(q_rook) != pieces.Rook)
        if king_bad or k_rook_bad:
            # can't castle kingside
            self._w_kingside = False
        if king_bad or q_rook_bad:
            # can't castle queenside
            self._w_queenside = False

        # Update black castling
        king = self.get_piece(8, 5)
        k_rook = self.get_piece(8, 8)
        q_rook = self.get_piece(8, 1)
        king_bad = (king is None) or (king.is_white()) or (type(king) != pieces.King)
        k_rook_bad = (k_rook is None) or (k_rook.is_white()) or (type(k_rook) != pieces.Rook)
        q_rook_bad = (q_rook is None) or (q_rook.is_white()) or (type(q_rook) != pieces.Rook)
        if king_bad or k_rook_bad:
            # can't castle kingside
            self._b_kingside = False
        if king_bad or q_rook_bad:
            # can't castle queenside
            self._b_queenside = False

    def put(self, location, piece):
        '''
        Places the given piece at the given location
        location: Coordinate to place piece at
        piece: Piece to place
        '''
        self._grid[location.row - 1][location.col - 1] = piece

    def under_attack(self, target, color: bool):
        '''
        Checks if the given target Coordinate is under attack from the pieces
        of the given color.
        target: Coordinate, representing the square to check if under attack
        color: bool, representing which color pieces would threaten the square
        Return: True if threatened, False otherwise
        '''
        for row in range(8):
            for col in range(8):
                piece = self._grid[row][col]
                if piece is not None and piece.is_white() == color:
                    # Found a piece of the desired color
                    start = Coordinate.from_coords(row + 1, col + 1)
                    if piece.can_attack(self, start, target):
                        # Target square is under attack
                        return True
        return False

    def count_attackers(self, target, color: bool):
        '''
        Checks how many pieces of the given color are attacking the target Coordinate.
        target: Coordinate, representing the square to check if under attack
        color: bool, representing which color pieces would threaten the square
        Return: int, representing how many pieces are attacking it (0+)
        '''
        count = 0
        for row in range(8):
            for col in range(8):
                piece = self._grid[row][col]
                if piece is not None and piece.is_white() == color:
                    # Found a piece of the desired color
                    start = Coordinate.from_coords(row + 1, col + 1)
                    if piece.can_attack(self, start, target):
                        # Target square is under attack
                        count += 1
        return count

    def in_check(self, color: bool = None):
        '''
        Checks if the king of the given color is in check
        color: True for white, False for black, default uses current player's turn
        Return: True if in check, False otherwise
        '''
        if color is None:
            color = self._turn
        king_coord = self.find_king(color)
        return self.under_attack(king_coord, not color)

    def is_valid_state(self):
        '''
        Checks if the board is in a valid state
        Return: True if valid, False otherwise
        '''
        return not self.in_check(not self._turn)

    def get_piece(self, row: int, col: int):
        '''
        Gets the piece at the given location on the board. Throws an
        IndexError if the row and column are invalid
        row: int, representing the row (1-8)
        col: int, representing the column (1-8)
        '''
        return self._grid[row - 1][col - 1]

    def get_king(self, color: bool = None):
        '''
        Finds the king with the given color
        color: True for white, False for black, None to use current color
        Return: King for the given color
        '''
        king_coord = self.find_king(color)
        if king_coord is None:
            return None
        else:
            return self.get_piece(king_coord.row, king_coord.col)

    def find_king(self, color: bool = None):
        '''
        Finds the location of the king with the given color
        color: True for white, False for black, None to use current color
        Return: Coordinate holding the king's location
        '''
        if color is None:
            color = self._turn
        for row in range(8):
            for col in range(8):
                piece = self._grid[row][col]
                if type(piece) == pieces.King and piece.is_white() == color:
                    return Coordinate.from_coords(row + 1, col + 1)

    def print_board(self):
        '''
        Prints out the string representation of the board
        '''
        for row in range(8, 0, -1):
            print('  +-----------------------------------------------+')
            print(row, end=' |')
            for piece in self._grid[row - 1]:
                if piece is None:
                    print('    ', end=' |')
                else:
                    print(' ' + piece.short_name(), end=' |')
            print()
        print('  +-----------------------------------------------+')
        print('     a     b     c     d     e     f     g     h   ')

    def to_fen(self):
        '''
        Converts the entire board state to a FEN string
        '''
        # Pieces on the board
        board_fen = self._board_to_fen()

        # Active color
        if self._turn:
            active_color = 'w'
        else:
            active_color = 'b'

        # Castling availability
        castling = ''
        if self._w_kingside:
            castling += 'K'
        if self._w_queenside:
            castling += 'Q'
        if self._b_kingside:
            castling += 'k'
        if self._b_queenside:
            castling += 'q'
        if len(castling) == 0:
            castling = '-'

        # En passant target
        if self._en_passant_target is None:
            en_passant_target = '-'
        else:
            en_passant_target = self._en_passant_target

        return " ".join((board_fen, active_color, castling, en_passant_target,
                        str(self._halfmove_clock), str(self._fullmove_number)))

    def copy(self):
        '''
        Creates a copy of this board (using deepcopy)
        Return: BoardState with exact same state as this one
        '''
        return deepcopy(self)

    def _board_from_fen(self, board_fen):
        '''
        Sets up the orientation of the pieces on the board, given the
        FEN notation for the piece placement.
        board_fen: str, representing the FEN notation for the piece placement
        '''
        self._grid = []
        fen_rows = board_fen.split('/')
        fen_rows.reverse()
        for line in fen_rows:
            rank = []
            for char in line:
                if char.isalpha():
                    # Placing a piece
                    rank.append(pieces.Piece.from_fen(char))
                else:
                    # Placing # blank spots
                    for _ in range(int(char)):
                        rank.append(None)
            self._grid.append(rank)

    def _board_to_fen(self):
        '''
        Converts the piece positions to FEN notation
        '''
        row = 7
        lines = []
        while row >= 0:
            fen_str = ""
            blank_count = 0
            rank = self._grid[row]
            for piece in rank:
                if piece is None:
                    blank_count += 1
                else:
                    if blank_count > 0:
                        fen_str += str(blank_count)
                        blank_count = 0
                    fen_str += piece.to_fen()
            if blank_count > 0:
                fen_str += str(blank_count)
            lines.append(fen_str)
            row -= 1
        return '/'.join(lines)

    def moves_with_target(self, target: Coordinate, classinfo=None):
        '''
        Finds all moves that can legally move to the given target square.
        target: Coordinate, representing the target square
        classinfo: piece type, or None for any piece to be allowed
        Return: list of Moves
        '''
        valid_moves = []
        for row in range(8):
            for col in range(8):
                # Get the piece at this square
                start = Coordinate.from_coords(row + 1, col + 1)
                piece = self._grid[row][col]
                if piece is not None and piece.is_white() == self._turn \
                        and (classinfo is None or type(piece) == classinfo):
                    # Get all the moves for this piece (matches type and current color)
                    for move in piece.get_moves(self, start):
                        if move.target == target:
                            valid_moves.append(move)
        return valid_moves

    def parse_move(self, move_str: str):
        '''
        Parses the given move string to create the associated Move object
        move_str: str, representing the user input for a move
        Return: Move that was parsed, or None if invalid/ambiguous
        '''
        move_str = move_str.strip().rstrip("#+")   # ignore mate/check characters
        if move_str == "0-0":
            move = moves.KingsideCastle(self._turn)
        elif move_str == "0-0-0":
            move = moves.QueensideCastle(self._turn)
        else:
            # e2e4, e2 e4, e2-e4, e2 - e4, e4xd5, e4 x d5, ...
            pattern = r"^([a-h]{1}[1-8]{1})\s*[x-]?\s*([a-h]{1}[1-8]{1})$"
            match_obj = re.match(pattern, move_str)
            if match_obj is not None:
                start_notation, target_notation = match_obj.group(1), match_obj.group(2)
                start = Coordinate.from_notation(start_notation)
                target = Coordinate.from_notation(target_notation)
                piece = self.get_piece(start.row, start.col)
                if type(piece) == pieces.Pawn and self._en_passant_target == target_notation:
                    # En passant for pawn
                    move = moves.EnPassant(start, target)
                else:
                    # Basic move
                    move = moves.BasicMove(start, target)
                return move

            # e7e8Q, e7-e8=R, d7xe8 B, ...
            pattern = r"^([a-h]{1}[1-8]{1})\s*[x-]?\s*([a-h]{1}[1-8]{1})\s*=?\s*([KQRBN]{1})$"
            match_obj = re.match(pattern, move_str)
            if match_obj is not None:
                start_notation, target_notation = match_obj.group(1), match_obj.group(2)
                start = Coordinate.from_notation(start_notation)
                target = Coordinate.from_notation(target_notation)
                piece = self.get_piece(start.row, start.col)
                promote_to = self._piece_type(match_obj.group(3))
                if type(piece) == pieces.Pawn and promote_to != pieces.Pawn:
                    # Pawn promotion
                    return moves.PawnPromotion(start, target, promote_to)

            # Set required row/col to null and try the other patterns
            required_row = None
            required_col = None

            # e4
            pattern = r"^[a-h]{1}[1-8]{1}$"
            match_obj = re.match(pattern, move_str)
            if match_obj is not None:
                target = Coordinate.from_notation(match_obj.group())
                return self._process_match(target, pieces.Pawn, required_col=target.col)

            # exd5, e x d5, e-d5, e - d5 ...
            pattern = r"^([a-h]{1})\s*[x-]?\s*([a-h]{1}[1-8]{1})$"
            match_obj = re.match(pattern, move_str)
            if match_obj is not None:
                target = Coordinate.from_notation(match_obj.group(2))
                return self._process_match(target, pieces.Pawn,
                        required_col="abcdefgh".index(match_obj.group(1)) + 1)

            # e8 Q, e8 = R, ...
            pattern = r"^([a-h]{1}[1-8]{1})\s*=?\s*([KQRBN]{1})$"
            match_obj = re.match(pattern, move_str)
            if match_obj is not None:
                # Pawn promotion
                target = Coordinate.from_notation(match_obj.group(1))
                promote_to = self._piece_type(match_obj.group(2))
                return self._process_promotion_match(target, promote_to)

            # dxe8=Q, d-e8 R, ...
            pattern = r"^([a-h]{1})\s*[x-]?\s*([a-h]{1}[1-8]{1})\s*=?\s*([KQRBN]{1})$"
            match_obj = re.match(pattern, move_str)
            if match_obj is not None:
                # Pawn promotion
                target = Coordinate.from_notation(match_obj.group(2))
                promote_to = self._piece_type(match_obj.group(3))
                col="abcdefgh".index(match_obj.group(1)) + 1
                return self._process_promotion_match(target, promote_to, required_col=col)

            # Nf3, Nxf3, N f3, N x f3, N-f3, N - f3, ...
            pattern = r"^([KQRBNP]{1})\s*[x-]?\s*([a-h]{1}[1-8]{1})$"
            match_obj = re.match(pattern, move_str)
            if match_obj is not None:
                target = Coordinate.from_notation(match_obj.group(2))
                piece_type = self._piece_type(match_obj.group(1))
                return self._process_match(target, piece_type)

            # Ngf3, Ngxf3, Ng f3, Ng x f3, Ng-f3, Ng - f3, ...
            pattern = r"^([KQRBNP]{1})([a-h]{1})\s*[x-]?\s*([a-h]{1}[1-8]{1})$"
            match_obj = re.match(pattern, move_str)
            if match_obj is not None:
                target = Coordinate.from_notation(match_obj.group(3))
                piece_type = self._piece_type(match_obj.group(1))
                return self._process_match(target, piece_type,
                        required_col="abcdefgh".index(match_obj.group(2)) + 1)

            # N1f3, N1xf3, N1 f3, N1 x f3, N1-f3, N1 - f3, ...
            pattern = r"^([KQRBNP]{1})([1-8]{1})\s*[x-]?\s*([a-h]{1}[1-8]{1})$"
            match_obj = re.match(pattern, move_str)
            if match_obj is not None:
                target = Coordinate.from_notation(match_obj.group(3))
                piece_type = self._piece_type(match_obj.group(1))
                return self._process_match(target, piece_type, required_row=int(match_obj.group(2)))

            # Ng1f3, Ng1xf3, Ng1 f3, Ng1 x f3, Ng1-f3, Ng1 - f3, ...
            pattern = r"^([KQRBNP]{1})([a-h]{1}[1-8]{1})\s*[x-]?\s*([a-h]{1}[1-8]{1})$"
            match_obj = re.match(pattern, move_str)
            if match_obj is not None:
                start = Coordinate.from_notation(match_obj.group(2))
                target = Coordinate.from_notation(match_obj.group(3))
                piece_type = self._piece_type(match_obj.group(1))
                return self._process_match(target, piece_type,
                        required_row=start.row, required_col=start.col)

            # Couldn't parse the move
            return None

        # Return move
        return move

    def _piece_type(self, piece_char):
        '''
        Converts the piece character to the piece classinfo
        piece_char: str, representing the piece type
        Return: classinfo for the correct piece
        '''
        piece_char = piece_char.upper()
        if piece_char == "K":
            return pieces.King
        elif piece_char == "Q":
            return pieces.Queen
        elif piece_char == "R":
            return pieces.Rook
        elif piece_char == "B":
            return pieces.Bishop
        elif piece_char == "N":
            return pieces.Knight
        elif piece_char == "P":
            return pieces.Pawn

    def _process_match(self, target, piece_type, *, required_row=None, required_col=None):
        '''
        Processes a move parse match
        target: Coordinate, representing the target square
        piece_type: classinfo for the type the piece moving to the target must be
        required_row: int, representing the required start row (optional)
        required_col: int, representing the required start col (optional)
        Return: Move that was found
        '''
        valid_moves = []
        for move in self.moves_with_target(target, piece_type):
            # check if the move matches the row/col requirements
            start = move.start
            if (required_row is None or start.row == required_row) and \
                    (required_col is None or start.col == required_col):
                valid_moves.append(move)

        # Make sure only one possible move from input
        if len(valid_moves) == 1:
            return valid_moves[0]
        else:
            return None

    def _process_promotion_match(self, target, promote_to, *, required_col=None):
        '''
        Processes a move parse match for a pawn promotion
        target: Coordinate, representing the target square
        promote_to: classinfo for the piece to promote to
        required_col: int, representing the required start col (optional)
        '''
        valid_moves = []
        for move in self.moves_with_target(target, pieces.Pawn):
            # check if move matches column and promotion requirements
            if type(move) == moves.PawnPromotion and move.promote_to() == promote_to \
                    and (required_col is None or move.start.col == required_col):
                valid_moves.append(move)

        # Make sure only one possible move from input
        if len(valid_moves) == 1:
            return valid_moves[0]
        else:
            return None

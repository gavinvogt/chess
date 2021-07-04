'''
File: pieces.py
Author: Gavin Vogt
This program defines the classes for all the Pieces.
'''

# dependencies
import abc

# my code
from .moves import BasicMove, KingsideCastle, QueensideCastle, PawnPromotion, EnPassant, InvalidMoveException
from .coordinate import Coordinate, InvalidCoordinateError

class Piece(metaclass=abc.ABCMeta):
    '''
    This class represents a chess piece.
    '''
    FEN_SYMBOL = None
    SHORT_NAME = '--'
    VALUE = 0
    __slots__ = ('_color',)

    def __init__(self, color: bool):
        '''
        Constructs a new chess piece
        '''
        if color not in (True, False):
            raise ValueError(f'Invalid color: {color}')
        self._color = color

    def __repr__(self):
        '''
        String representation of the piece
        '''
        return f'<{self.__class__.__name__} ({self._color_str()})>'

    def __eq__(self, other):
        '''
        Checks if two pieces are equal
        '''
        if isinstance(other, self.__class__):
            # Check piece type + color
            return (type(self) == type(other)) and (self._color == other._color)
        else:
            return NotImplemented

    def is_white(self):
        '''
        Checks if this piece is white
        '''
        return self._color

    @abc.abstractmethod
    def can_attack(self, board, start, target):
        '''
        Checks if this piece can attack the given row and column of
        the board.
        board: BoardState to use
        start: Coordinate, representing the start coordinate of the piece
        target: Coordinate, representing the target coordinate of the piece
        Return: True if it can attack the given square, False otherwise
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def can_move(self, board, move):
        '''
        Checks if this piece can make the given move on the board. Does
        not account for if the move will leave the king in check
        board: BoardState to use
        move: Move to check if movement is valid
        Return: True if the piece can move like that, False otherwise
        '''
        raise NotImplementedError

    def get_moves(self, board, start):
        '''
        Gets all the available moves for this piece
        board: BoardState to use
        start: Coordinate, representing the start coordinate of the piece
        Return: list of Move objets representing the moves
        '''
        valid_moves = []
        for move in self.potential_moves(board, start):
            try:
                board.make_move(move)
            except InvalidMoveException:
                # Move is not valid
                pass
            else:
                # Move is valid
                valid_moves.append(move)
        return valid_moves

    def potential_moves(self, board, start):
        '''
        Gets all the potential moves for this piece
        board: BoardState to use
        start: Coordinate, representing the start coordinate of the piece
        Return: list of Move objets representing the potential moves
        '''
        raise NotImplementedError

    def short_name(self):
        '''
        Returns the short (3 char) name for the piece
        '''
        return self._color_str()[0] + self.SHORT_NAME

    def long_name(self):
        '''
        Returns the long name for the piece
        '''
        return self._color_str().upper() + '_' + self.__class__.__name__.upper()

    def get_value(self):
        '''
        Returns the value associated with the piece
        '''
        return self.VALUE

    def to_fen(self):
        '''
        Returns the FEN notation character representing this piece
        '''
        fen_symbol = self.__class__.FEN_SYMBOL
        if fen_symbol is None:
            raise InvalidPieceException('Invalid piece')
        elif self.is_white():
            return fen_symbol.upper()
        else:
            return fen_symbol.lower()

    @staticmethod
    def from_fen(fen_symbol: str):
        '''
        Converts the given fen symbol to the corresponding piece
        fen_symbol: char, representing the piece in FEN
        '''
        # Check if it is valid
        if not isinstance(fen_symbol, str) or len(fen_symbol) != 1:
            raise InvalidPieceException(f'Invalid fen symbol: {fen_symbol}')

        # Convert to the piece
        color = fen_symbol.isupper()
        fen_symbol = fen_symbol.upper()
        if fen_symbol == King.FEN_SYMBOL.upper():
            return King(color)
        elif fen_symbol == Queen.FEN_SYMBOL.upper():
            return Queen(color)
        elif fen_symbol == Rook.FEN_SYMBOL.upper():
            return Rook(color)
        elif fen_symbol == Bishop.FEN_SYMBOL.upper():
            return Bishop(color)
        elif fen_symbol == Knight.FEN_SYMBOL.upper():
            return Knight(color)
        elif fen_symbol == Pawn.FEN_SYMBOL.upper():
            return Pawn(color)
        else:
            raise InvalidPieceException(f'Invalid fen symbol: {fen_symbol}')

    def _color_str(self):
        if self._color:
            return 'White'
        else:
            return 'Black'

class King(Piece):
    '''
    This class represents a King piece
    '''
    FEN_SYMBOL = 'K'
    SHORT_NAME = 'Ki'
    VALUE = 200

    def can_attack(self, board, start, target):
        # Check that the start/target coords are valid
        if start is None or target is None:
            return False

        # Check the geometry
        delta_row = abs(start.row - target.row)
        delta_col = abs(start.col - target.col)
        if delta_row == 0 and delta_col == 0:
            return False
        return (0 <= delta_row <= 1) and (0 <= delta_col <= 1)

    def can_move(self, board, move):
        if type(move) == BasicMove:
            piece = board.get_piece(move.target.row, move.target.col)
            if piece is not None and piece.is_white() == self._color:
                # trying to take own piece
                return False
            else:
                # moving to blank square, or taking opponent piece
                return self.can_attack(board, move.start, move.target)
        elif type(move) == KingsideCastle:
            return board.can_castle_kingside()
        elif type(move) == QueensideCastle:
            return board.can_castle_queenside()
        else:
            # Un-recognized move for this piece
            return False

    def potential_moves(self, board, start):
        # Get all the regular moves
        moves = []
        for r in (-1, 0, 1):
            for c in (-1, 0, 1):
                # Check if the king can move to the square at these deltas
                if not (r == 0 and c == 0):
                    try:
                        target = Coordinate.from_coords(start.row + r, start.col + c)
                        move = BasicMove(start, target)
                    except InvalidCoordinateError:
                        pass
                    else:
                        moves.append(move)

        # Add any castling moves
        if not board.in_check():
            if board.can_castle_kingside():
                moves.append(KingsideCastle(self._color))
            if board.can_castle_queenside():
                moves.append(QueensideCastle(self._color))
        return moves

class Queen(Piece):
    '''
    This class represents a Queen piece
    '''
    FEN_SYMBOL = 'Q'
    SHORT_NAME = 'Qn'
    VALUE = 9

    def can_attack(self, board, start, target):
        if Rook.can_attack(self, board, start, target):
            # Moving like a rook to attack target
            return True
        else:
            # Check if it moves like a bishop to attack target
            return Bishop.can_attack(self, board, start, target)

    def can_move(self, board, move):
        if type(move) == BasicMove:
            piece = board.get_piece(move.target.row, move.target.col)
            if piece is not None and piece.is_white() == self._color:
                # trying to take own piece
                return False
            else:
                # moving to blank square, or taking opponent piece
                return self.can_attack(board, move.start, move.target)
        else:
            # Un-recognized move for this piece
            return False

    def potential_moves(self, board, start):
        moves = []
        for row_slope in (-1, 0, 1):
            for col_slope in (-1, 0, 1):
                if row_slope == 0 and col_slope == 0:
                    # skip (0, 0) slope
                    continue
                row, col = start.row + row_slope, start.col + col_slope
                while (1 <= row <= 8 and 1 <= col <= 8):
                    piece = board.get_piece(row, col)
                    if piece is not None and piece.is_white() == self._color:
                        # collision with own color
                        break
                    else:
                        target = Coordinate.from_coords(row, col)
                        moves.append(BasicMove(start, target))
                        if piece is not None:
                            # taking a piece of opposite color
                            break
                    row += row_slope
                    col += col_slope
        return moves

class Rook(Piece):
    '''
    This class represents a Rook piece
    '''
    FEN_SYMBOL = 'R'
    SHORT_NAME = 'Rk'
    VALUE = 5

    def can_attack(self, board, start, target):
        # Check that the start/target coords are valid
        if board is None or start is None or target is None:
            return False

        # Check shape of move
        if (start.col == target.col) == (start.row == target.row):
            # Columns are rows are both same, or both different
            return False

        # Check that there are no collisions
        col_diff = abs(target.col - start.col)
        row_diff = abs(target.row - start.row)
        col_slope = 0 if col_diff == 0 else (target.col - start.col) // col_diff
        row_slope = 0 if row_diff == 0 else (target.row - start.row) // row_diff
        row, col = start.row + row_slope, start.col + col_slope
        while row != target.row or col != target.col:
            if board.get_piece(row, col) is not None:
                # Found a piece blocking the way
                return False
            row += row_slope
            col += col_slope
        return True

    def can_move(self, board, move):
        if type(move) == BasicMove:
            piece = board.get_piece(move.target.row, move.target.col)
            if piece is not None and piece.is_white() == self._color:
                # trying to take own piece
                return False
            else:
                # moving to blank square, or taking opponent piece
                return self.can_attack(board, move.start, move.target)
        else:
            # Un-recognized move for this piece
            return False

    def potential_moves(self, board, start):
        moves = []
        for row_slope, col_slope in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            row, col = start.row + row_slope, start.col + col_slope
            while (1 <= row <= 8 and 1 <= col <= 8):
                piece = board.get_piece(row, col)
                if piece is not None and piece.is_white() == self._color:
                    # collision with own color
                    break
                else:
                    target = Coordinate.from_coords(row, col)
                    moves.append(BasicMove(start, target))
                    if piece is not None:
                        # taking a piece of opposite color
                        break
                row += row_slope
                col += col_slope
        return moves

class Bishop(Piece):
    '''
    This class represents a Bishop piece
    '''
    FEN_SYMBOL = 'B'
    SHORT_NAME = 'Bi'
    VALUE = 3

    def can_attack(self, board, start, target):
        # Check that the start/target coords are valid
        if board is None or start is None or target is None:
            return False

        # Check shape of move
        col_diff = abs(target.col - start.col)
        row_diff = abs(target.row - start.row)
        if row_diff == 0 or col_diff != row_diff:
            # no move, or not diagonal
            return False

        # Check that there are no collisions
        col_slope = 0 if col_diff == 0 else (target.col - start.col) // col_diff
        row_slope = 0 if row_diff == 0 else (target.row - start.row) // row_diff
        col = start.col
        for row in range(start.row + row_slope, target.row, row_slope):
            col += col_slope
            if board.get_piece(row, col) is not None:
                # Found a piece blocking the way
                return False
        return True

    def can_move(self, board, move):
        if type(move) == BasicMove:
            piece = board.get_piece(move.target.row, move.target.col)
            if piece is not None and piece.is_white() == self._color:
                # trying to take own piece
                return False
            else:
                # moving to blank square, or taking opponent piece
                return self.can_attack(board, move.start, move.target)
        else:
            # Un-recognized move for this piece
            return False

    def potential_moves(self, board, start):
        moves = []
        for row_slope in (-1, 1):
            for col_slope in (-1, 1):
                row, col = start.row + row_slope, start.col + col_slope
                while (1 <= row <= 8 and 1 <= col <= 8):
                    piece = board.get_piece(row, col)
                    if piece is not None and piece.is_white() == self._color:
                        # collision with own color
                        break
                    else:
                        target = Coordinate.from_coords(row, col)
                        moves.append(BasicMove(start, target))
                        if piece is not None:
                            # taking a piece of opposite color
                            break
                    row += row_slope
                    col += col_slope
        return moves

class Knight(Piece):
    '''
    This class represents a Knight piece
    '''
    FEN_SYMBOL = 'N'
    SHORT_NAME = 'Kn'
    VALUE = 3

    def can_attack(self, board, start, target):
        # Check that the start/target coords are valid
        if start is None or target is None:
            return False

        # Check the geometry
        col_diff = abs(start.col - target.col)
        row_diff = abs(start.row - target.row)
        if (col_diff == 1 and row_diff == 2) or (col_diff == 2 and row_diff == 1):
            # has L shape
            return True
        else:
            # invalid move
            return False

    def can_move(self, board, move):
        if type(move) == BasicMove:
            piece = board.get_piece(move.target.row, move.target.col)
            if piece is not None and piece.is_white() == self._color:
                # trying to take own piece
                return False
            else:
                # moving to blank square, or taking opponent piece
                return self.can_attack(board, move.start, move.target)
        else:
            # Un-recognized move for this piece
            return False

    def potential_moves(self, board, start):
        moves = []
        for row_diff in (-2, -1, 1, 2):
            for col_diff in (-2, -1, 1, 2):
                if abs(row_diff) != abs(col_diff):
                    # Has the proper L shape
                    try:
                        target = Coordinate.from_coords(start.row + row_diff, start.col + col_diff)
                    except InvalidCoordinateError:
                        # not on the board
                        pass
                    else:
                        # valid coordinate for move
                        moves.append(BasicMove(start, target))
        return moves

class Pawn(Piece):
    '''
    This class represents a Pawn piece
    '''
    FEN_SYMBOL = 'P'
    SHORT_NAME = 'Pn'
    VALUE = 1
    __slots__ = ('_has_moved',)

    def __init__(self, color: bool):
        '''
        Constructs a new un-moved pawn
        '''
        super().__init__(color)
        self._has_moved = False

    def has_moved(self):
        '''
        Checks if this Pawn has moved before
        Return: True if moved before, and False otherwise
        '''
        return self._has_moved

    def set_moved(self):
        '''
        Sets this Pawn to having been moved
        '''
        self._has_moved = True

    def can_attack(self, board, start, target):
        # Check that the start/target coords are valid
        if start is None or target is None:
            return False

        # Check if it can attack the target (1 away, diagonal)
        direction = self._get_direction()
        return (abs(start.col - target.col) == 1) and (start.row + direction == target.row)

    def _get_direction(self):
        '''
        Gets the direction the pawn should be moving based on its color.
        Return: 1 for white, -1 for black
        '''
        if self._color:
            return 1
        else:
            return -1

    def can_move(self, board, move):
        if type(move) == BasicMove:
            if move.start.col == move.target.col:
                # moving forward 1 or 2 spaces
                direction = self._get_direction()
                distance = (move.target.row - move.start.row) // direction
                if distance == 1 and self._ranks_to_promotion(move.start) != 1:
                    # moving 1 space forward, not to final rank
                    return (board.get_piece(move.start.row + direction, move.start.col) is None)
                elif distance == 2 and not self._has_moved:
                    # moving 2 spaces forward
                    return (board.get_piece(move.start.row + direction, move.start.col) is None
                        and board.get_piece(move.start.row + 2*direction, move.start.col) is None)
                else:
                    # not moving a valid amount
                    return False
            else:
                # trying to take a piece
                piece = board.get_piece(move.target.row, move.target.col)
                if piece is not None and piece.is_white() == self._color:
                    # trying to take own piece
                    return False
                else:
                    # taking opponent's piece
                    return self.can_attack(board, move.start, move.target)
        elif type(move) == PawnPromotion:
            if move.start.col == move.target.col:
                # moving directly forward
                direction = self._get_direction()
                if move.start.row + direction == move.target.row and \
                        self._ranks_to_promotion(move.start) == 1:
                    # moving forward 1; check that the space is empty
                    return (board.get_piece(move.target.row, move.target.col) is None)
                else:
                    # invalid forward move
                    return False
            else:
                # trying to take a piece
                piece = board.get_piece(move.target.row, move.target.col)
                if piece is not None and piece.is_white() == self._color:
                    # trying to take own piece
                    return False
                else:
                    # taking opponent's piece
                    return self.can_attack(board, move.start, move.target)
        elif type(move) == EnPassant:
            if board.en_passant_coords() == move.target:
                # Check that the pawn is actually attacking the en-passant target
                return self.can_attack(board, move.start, move.target)
            else:
                # can't do en-passant to the target square
                return False
        else:
            # Un-recognized move for this piece
            return False

    def potential_moves(self, board, start):
        # Check for regular moves
        moves = []
        direction = self._get_direction()
        if self._ranks_to_promotion(start) == 1:
            # all moves will be promotions
            self._find_promotions(board, moves, start)
        else:
            # all moves will be basic moves
            self._find_basic_moves(board, moves, start)

        # Check for en passant
        en_passant_coords = board.en_passant_coords()
        if self.can_attack(board, start, en_passant_coords):
            moves.append(EnPassant(start, en_passant_coords))
        return moves

    def _find_promotions(self, board, moves, start):
        '''
        Finds all the potential promotion moves and adds them to the `moves` list.
        board: BoardState that the pawn is on
        moves: list of Moves to add to
        start: Coordinate, representing the start coordinate
        '''
        direction = self._get_direction()
        target = Coordinate.from_coords(start.row + direction, start.col)
        if board.get_piece(target.row, target.col) is None:
            # Blank square ahead
            moves.extend(self._all_promotions(start, target))
        for col_dir in (-1, 1):
            try:
                target = Coordinate.from_coords(start.row + direction, start.col + col_dir)
                piece = board.get_piece(target.row, target.col)
                if piece is not None and piece.is_white() != self._color:
                    # Attacking a black piece at this square
                    moves.extend(self._all_promotions(start, target))
            except InvalidCoordinateError:
                # Not a valid coordinate
                pass

    def _find_basic_moves(self, board, moves, start):
        '''
        Finds all the potential basic moves and adds them to the `moves` list.
        board: BoardState that the pawn is on
        moves: list of Moves to add to
        start: Coordinate, representing the start coordinate
        '''
        direction = self._get_direction()
        target = Coordinate.from_coords(start.row + direction, start.col)
        if board.get_piece(target.row, target.col) is None:
            # Blank square ahead
            moves.append(BasicMove(start, target))
            target = Coordinate.from_coords(start.row + 2*direction, start.col)
            if not self._has_moved and board.get_piece(target.row, target.col) is None:
                # Blank square 2 ahead
                moves.append(BasicMove(start, target))
        for col_dir in (-1, 1):
            try:
                target = Coordinate.from_coords(start.row + direction, start.col + col_dir)
                piece = board.get_piece(target.row, target.col)
                if piece is not None and piece.is_white() != self._color:
                    # Attacking a black piece at this square
                    moves.append(BasicMove(start, target))
            except InvalidCoordinateError:
                # Not a valid coordinate
                pass

    def _all_promotions(self, start, target):
        '''
        Gets all the possible promotions for the given start/target locations
        start: Coordinate, representing the start coordinate
        target: Coordinate, representing the target coordinate
        '''
        return [
            PawnPromotion(start, target, classinfo) for classinfo in (Knight, Bishop, Rook, Queen)
        ]

    def _ranks_to_promotion(self, location):
        '''
        Gets the number of ranks between this pawn's current location
        and the rank at which it can promote
        location: Coordinate representing its current position
        Return: int, representing the number of ranks left until it can promote
        '''
        if self._color:
            return 8 - location.row
        else:
            return location.row - 1

class InvalidPieceException(ValueError):
    '''
    This class represents an Exception for when an invalid piece is given
    '''
    pass
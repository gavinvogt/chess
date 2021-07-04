'''
File: moves.py
Author: Gavin Vogt
This program defines the various move classes.
Available moves:
    - BasicMove
    - KingsideCastle
    - QueensideCastle
    - PawnPromotion
    - EnPassant
'''

# dependencies
import abc

# my code
from . import pieces
from .coordinate import Coordinate

class Move(metaclass=abc.ABCMeta):
    '''
    This class represents a move in a chess game
    '''

    __slots__ = ('_start', '_target')

    def __init__(self, start, target):
        '''
        Creates a move with start/target coordinates
        start: Coordinate, representing the start coordinate
        target: Coordinate, representing the target coordinate
        '''
        self._start = start
        self._target = target

    def __repr__(self):
        '''
        String representation of the Move
        '''
        return f"<{self.__class__.__name__}({self._start.to_notation()} - {self._target.to_notation()})>"

    @property
    def start(self):
        '''
        Gives read-only access to the `start` Coordinate property
        '''
        return self._start

    @property
    def target(self):
        '''
        Gives read-only access to the `target` Coordinate property
        '''
        return self._target

    @abc.abstractmethod
    def execute(self, board):
        '''
        Executes this move on the GIVEN board (should already be copied)
        board: BoardState to do move on
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def was_capture(self):
        '''
        Checks if this move was a capture
        Return: True if was a capture, False otherwise
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def was_pawn_advance(self):
        '''
        Checks if this move was a pawn advance
        Return: True if pawn advance, False otherwise
        '''
        raise NotImplementedError

    def to_notation(self, new_board):
        '''
        Converts this PREVIOUSLY EXECUTED move to notation, including
        check/checkmate information.
        new_board: BoardState that was created after making the move
        '''
        # Add check / checkmate information
        notation = self.basic_notation(new_board)
        if new_board.is_checkmate():
            notation += '#'
        else:
            king_coord = new_board.find_king(new_board._turn)
            attackers = new_board.count_attackers(king_coord, not new_board._turn)
            if attackers == 1:
                notation += '+'
            elif attackers == 2:
                notation += '++'
        return notation

    @abc.abstractmethod
    def basic_notation(self, new_board):
        '''
        Converts this PREVIOUSLY EXECUTED move to notation
        Note: mostly just for internal use
        new_board: BoardState that was created after making the move
        '''
        raise NotImplementedError

class BasicMove(Move):
    '''
    This class represents a basic move in a chess game
    '''

    __slots__ = ('_was_capture', '_was_pawn')

    def __init__(self, start, target):
        '''
        Constructs a new basic move (move a piece from `start` to `target`)
        start: Coordinate representing the start square
        target: Coordinate representing the target square
        '''
        super().__init__(start, target)
        self._was_capture = False
        self._was_pawn = False

    @property
    def start(self):
        '''
        Gives read-only access to the `start` Coordinate property
        '''
        return super().start

    @property
    def target(self):
        '''
        Gives read-only access to the `target` Coordinate property
        '''
        return super().target

    def execute(self, board):
        if not self._start.is_valid():
            # invalid start position
            raise InvalidMoveException(f"Invalid move: bad start position {self._start}")
        elif not self._target.is_valid():
            # invalid target position
            raise InvalidMoveException(f"Invalid move: bad target position {self._target}")

        # Get the piece at the start position
        piece = board.get_piece(self._start.row, self._start.col)
        if piece is None or piece.is_white() != board.white_to_move():
            # Blank square, or not right color
            raise InvalidMoveException(f"Invalid move: {self._start}-{self._target}")

        # Get the piece at the target position
        target_piece = board.get_piece(self._target.row, self._target.col)
        if target_piece is not None:
            if target_piece.is_white() == board.white_to_move():
                # Trying to take own piece
                raise InvalidMoveException(f"Invalid move: {self._start}-{self._target}")
            else:
                # Taking opponent's piece
                self._was_capture = True

        # Special case for moving a pawn
        if type(piece) == pieces.Pawn:
            self._was_pawn = True
            piece.set_moved()
            if abs(self._start.row - self._target.row) == 2:
                # moved 2 spaces - en passant legal
                board.set_en_passant(Coordinate.from_coords(
                    (self._start.row + self._target.row) // 2, self._start.col))

        # Make the move
        board.put(self._target, piece)
        board.put(self._start, None)
        return board

    def was_capture(self):
        return self._was_capture

    def was_pawn_advance(self):
        return self._was_pawn

    def basic_notation(self, new_board):
        piece_moved = new_board.get_piece(self._target.row, self._target.col)
        if piece_moved.FEN_SYMBOL == 'P':
            # Pawn move
            if self._was_capture:
                notation = "abcdefgh"[self._start.col - 1]
            else:
                notation = ''
        else:
            # Not a pawn move
            notation = piece_moved.FEN_SYMBOL

        if self._was_capture:
            notation += "x"
        notation += self._target.to_notation()
        return notation

class KingsideCastle(Move):
    '''
    This class represents a kingside castle in a chess game
    '''

    __slots__ = ('_color',)

    def __init__(self, color: bool):
        '''
        Constructs a KingsideCastle move
        color: bool, representing white for True and black for False
        '''
        rank = 1 if color else 8
        start = Coordinate.from_coords(rank, 5)  # start
        target = Coordinate.from_coords(rank, 7)  # target
        super().__init__(start, target)
        self._color = color

    @property
    def start(self):
        '''
        Gives read-only access to the `start` Coordinate property
        '''
        return super().start

    @property
    def target(self):
        '''
        Gives read-only access to the `target` Coordinate property
        '''
        return super().target

    def execute(self, board):
        if not board.can_castle_kingside() or self._color != board.white_to_move():
            # Can't castle kingside OR
            # Color given to move was wrong
            raise InvalidMoveException(f"Invalid move: 0-0")
        rank = 1 if board.white_to_move() else 8
        king = board.get_piece(rank, 5)
        rook = board.get_piece(rank, 8)
        board.put(self._target, king)
        board.put(Coordinate.from_coords(rank, 6), rook)
        board.put(Coordinate.from_coords(rank, 8), None)  # remove old k_rook
        board.put(self._start, None)  # remove old king
        return board

    def was_capture(self):
        return False

    def was_pawn_advance(self):
        return False

    def basic_notation(self, new_board):
        return '0-0'

class QueensideCastle(Move):
    '''
    This class represents a queenside castle in a chess game
    '''

    __slots__ = ('_color',)

    def __init__(self, color: bool):
        '''
        Constructs a QueensideCastle move
        color: bool, representing white for True and black for False
        '''
        rank = 1 if color else 8
        start = Coordinate.from_coords(rank, 5)  # start
        target = Coordinate.from_coords(rank, 3)  # target
        super().__init__(start, target)
        self._color = color

    @property
    def start(self):
        '''
        Gives read-only access to the `start` Coordinate property
        '''
        return super().start

    @property
    def target(self):
        '''
        Gives read-only access to the `target` Coordinate property
        '''
        return super().target

    def execute(self, board):
        if not board.can_castle_queenside() or self._color != board.white_to_move():
            # Can't castle queenside OR
            # Color given to move was wrong
            raise InvalidMoveException(f"Invalid move: 0-0-0")

        rank = 1 if board.white_to_move() else 8
        king = board.get_piece(rank, 5)
        rook = board.get_piece(rank, 1)
        board.put(self._target, king)
        board.put(Coordinate.from_coords(rank, 4), rook)
        board.put(self._start, None)  # remove old king
        board.put(Coordinate.from_coords(rank, 1), None)  # remove old q_rook
        return board

    def was_capture(self):
        return False

    def was_pawn_advance(self):
        return False

    def basic_notation(self, new_board):
        return '0-0-0'

class PawnPromotion(BasicMove):
    '''
    This class represents a pawn promotion in a chess game
    '''

    __slots__ = ('_promote_to',)

    def __init__(self, start, target, classinfo):
        '''
        Constructs the information for a new pawn promotion.
        start: Coordinate representing the start square
        target: Coordinate representing the target square
        classinfo: class information for the Piece to promote to
        '''
        super().__init__(start, target)
        self._promote_to = classinfo

    def __repr__(self):
        '''
        String representation of the PawnPromotion move
        '''
        return f"<{self.__class__.__name__}({self._start.to_notation()} - {self._target.to_notation()}, {self._promote_to.__name__})>"

    @property
    def start(self):
        '''
        Gives read-only access to the `start` Coordinate property
        '''
        return super().start

    @property
    def target(self):
        '''
        Gives read-only access to the `target` Coordinate property
        '''
        return super().target

    def promote_to(self):
        '''
        Returns the classinfo for the piece to promote to
        '''
        return self._promote_to

    def set_promotion(self, classinfo):
        '''
        Sets the piece type to promote to
        classinfo: classinfo of the new piece type to promote to
        '''
        self._promote_to = classinfo

    def execute(self, board):
        # TODO: check if last rank is not occupied for forward

        if not (self._start.is_valid() and self._target.is_valid()):
            # Invalid start or target position
            raise InvalidMoveException(f"Invalid move: {self._start}-{self._target}")

        # Get the piece at the start position
        piece = board.get_piece(self._start.row, self._start.col)
        if not isinstance(piece, pieces.Pawn) or piece.is_white() != board.white_to_move():
            # Blank square, or not right color, or not Pawn
            raise InvalidMoveException(f"Invalid move: {self._start}-{self._target}")

        # Get the piece at the target position
        target_piece = board.get_piece(self._target.row, self._target.col)
        if target_piece is not None:
            if target_piece.is_white() == board.white_to_move():
                # Trying to take own piece
                raise InvalidMoveException(f"Invalid move: {self._start}-{self._target}")
            else:
                # Taking opponent's piece
                self._was_capture = True

        # Make the move
        board.put(self._target, self._promote_to(board.white_to_move()))
        board.put(self._start, None)
        return board

    def was_capture(self):
        return self._was_capture

    def was_pawn_advance(self):
        return True

    def basic_notation(self, new_board):
        if self._was_capture:
            notation = "abcdefgh"[self._start.col - 1] + "x"
        else:
            notation = ''
        notation += self._target.to_notation()
        notation += '=' + self._promote_to.FEN_SYMBOL
        return notation

class EnPassant(Move):
    '''
    This class represents an en-passant move in a chess game
    '''
    def __init__(self, start, target):
        '''
        Constructs a new en-passant move (move a pawn from `start` to `target`)
        start: Coordinate representing the start square
        target: Coordinate representing the target square
        '''
        super().__init__(start, target)

    @property
    def start(self):
        '''
        Gives read-only access to the `start` Coordinate property
        '''
        return super().start

    @property
    def target(self):
        '''
        Gives read-only access to the `target` Coordinate property
        '''
        return super().target

    def execute(self, board):
        if not (self._start.is_valid() and self._target.is_valid()) \
                or self._target != board.en_passant_coords():
            # Invalid start or target position, or invalid en-passant coords
            raise InvalidMoveException(f"Invalid move: {self._start}-{self._target}")

        # Get the piece at the start position
        piece = board.get_piece(self._start.row, self._start.col)
        if type(piece) != pieces.Pawn or piece.is_white() != board.white_to_move():
            # Blank square, or not right color, or not Pawn
            raise InvalidMoveException(f"Invalid move: {self._start}-{self._target}")

        # Make the move
        board.put(self._target, piece)
        board.put(self._start, None)
        if board.white_to_move():
            # Taking pawn 1 rank in front of target
            other_pawn_coords = Coordinate.from_coords(self._target.row - 1, self._target.col)
        else:
            # Taking pawn 1 rank behind target
            other_pawn_coords = Coordinate.from_coords(self._target.row + 1, self._target.col)
        board.put(other_pawn_coords, None)
        return board

    def was_capture(self):
        return True

    def was_pawn_advance(self):
        return True

    def basic_notation(self, new_board):
        start_col = "abcdefgh"[self._start.col - 1]
        return f"{start_col}x{self._target.to_notation()}"


class InvalidMoveException(ValueError):
    '''
    This class represents the Exception thrown when an invalid move
    is made.
    '''
    pass
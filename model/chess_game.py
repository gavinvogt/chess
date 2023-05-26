"""
File: chess_game.py
Author: Gavin Vogt
This program defines the ChessGame class, which represents an
entire chess game. It also defines the GameResult class, which
is returned by the ChessGame if the game is over.
"""

from . import BoardState


class ChessGame:
    """
    This class represents a chess game, consisting of a series of board states
    """

    def __init__(self):
        """
        Constructs a new chess game
        """
        self._states: list[BoardState] = []

    def __len__(self):
        """
        Length of the ChessGame is the number of board states it contains
        """
        return len(self._states)

    def push(self, state: BoardState):
        """
        Pushes a new BoardState to the game
        state: BoardState to add
        """
        self._states.append(state)

    def pop_last(self):
        """
        Pops the last state in the list of board states, removing it from the list
        Return: BoardState that was last
        """
        return self._states.pop(-1)

    def current_state(self):
        """
        Gets the current board state
        Return: BoardState representing the current board state
        """
        return self._states[-1]

    def get_result(self):
        """
        Gets the game result (game over or still playable)
        Return: GameResult object if game over, or None
        """
        board = self.current_state()
        if board.is_checkmate():
            if board.white_to_move():
                # Black won
                return GameResult("Black Won", "checkmate", 0)
            else:
                # White won
                return GameResult("White Won", "checkmate", 1)
        elif board.is_fifty_move_rule():
            # Draw due to fifty move rule
            return GameResult("Draw", "fifty move rule", 0.5)
        elif board.is_stalemate():
            # Draw due to stalemate
            return GameResult("Draw", "stalemate", 0.5)
        elif self.threefold_repetition():
            # Draw due to threefold repetition
            return GameResult("Draw", "threefold repetition", 0.5)
        elif board.insufficient_material():
            # Draw due to insufficient material
            return GameResult("Draw", "insufficient material", 0.5)
        else:
            # Game is not over
            return None

    def threefold_repetition(self):
        """
        Checks if threefold repetition has occurred at the current position.
        Return: True if threefold repetition has occurred, False otherwise
        """
        current_state = self.current_state()
        halfmove = current_state.halfmove()  # number of turns to look back through
        if self._states[-halfmove - 1 :].count(current_state) >= 3:
            # Located a threefold repetition
            return True


class GameResult:
    """
    This class represents the result of a game (game over)
    """

    def __init__(self, result_type: str, reason: str, white_score: float):
        """
        Constructs the game result
        result_type: str, representing the game result ("Game Over", "Draw")
        reason: str, representing the reason the game is over
        white_score: float, representing white's score (1, .5, 0)
        """
        self._type = result_type
        self._reason = reason
        self._white = white_score
        self._black = 1 - white_score

    def get_type(self):
        """
        Gets the type of game end
        Return: str, representing the type of result
        """
        return self._type

    def get_reason(self):
        """
        Gets the reason the game ended
        Return: str, representing the reason for the game result
        """
        return self._reason

    def score_string(self):
        """
        Gets the string representing the score.
        Return: "1 - 0", "0.5 - 0.5", or "0 - 1"
        """
        return f"{self._white} - {self._black}"

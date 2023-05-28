"""
File: board_canvas.py
Author: Gavin Vogt
This program represents the canvas for the board.
"""

# dependencies
import tkinter
from PIL import ImageTk
from enum import Enum, auto
from typing import Optional

# my code
from model import BoardState, Coordinate, moves
from view.themes import Theme
from .pawn_promotion_popup import PawnPromotionPopup
from .view_utils import piece_to_image

SQUARE_SIZE = 78
SQUARE_OUTLINE = 2
TOTAL_SQUARE = (
    SQUARE_SIZE + SQUARE_OUTLINE
)  # useful for the actual number of pixels in square
BOARD_SIZE = 8 * TOTAL_SQUARE  # useful for board size (length of all the squares)
BOARD_BORDER = 6
BOARD_OUTLINE = 54
TOTAL_LENGTH = BOARD_SIZE + 2 * (BOARD_BORDER + BOARD_OUTLINE)  # total length of canvas
TEXT_FONT = ("Garamond", 15)
CIRCLE_RADIUS = 16


class Perspective(Enum):
    WHITE = auto()
    BLACK = auto()
    TO_MOVE = auto()

    def get_name(self):
        return " ".join(self.name.lower().capitalize().split("_"))


class Square:
    """
    This class represents a square on the chess board, holding information
    about the state (focused, highlighted, ...)
    """

    __slots__ = ("_id", "focus", "highlight", "move")

    def __init__(self, oid: int):
        """
        Creates a Square representing a square on the board
        oid: int, representing the object id of the square on the canvas
        """
        self._id = oid
        self.focus = False
        self.highlight = True
        self.move: Optional[moves.Move] = None

    def get_id(self):
        """
        Gets the object id for the square on the canvas
        """
        return self._id

    def reset(self):
        """
        Resets the square information
        """
        self.focus = False
        self.highlight = False
        self.move = None


class BoardCanvas(tkinter.Canvas):
    """
    This class represents the Canvas to use to draw the board
    """

    def __init__(
        self, tk: tkinter.Tk, theme: Theme, perspective: Perspective, board: BoardState
    ):
        """
        Creates the canvas that the chess board will be drawn on
        tk: root tkinter object
        theme: Theme to use when drawing everything
        board: BoardState to draw
        """
        super().__init__(tk, width=TOTAL_LENGTH, height=TOTAL_LENGTH)
        self._root_window = tk
        self._observers = []

        # Squares and board border
        self._border_id = self.create_rectangle(
            BOARD_OUTLINE,
            BOARD_OUTLINE,
            TOTAL_LENGTH - BOARD_OUTLINE,
            TOTAL_LENGTH - BOARD_OUTLINE,
            width=0,
        )
        self._perspective = perspective
        self._set_up_notation()
        self._create_squares()
        self._create_color_circle()

        self.set_theme(theme)
        self._images: list[ImageTk.PhotoImage] = []
        self.bind("<Button-1>", self.on_left_click)
        self.set_board(board)

    def _set_up_notation(self):
        """
        Sets up the notation labels (a-h and 1-8) along the sides of the board.
        Stores all of the labels to update their text color later for any
        theme changes.
        """
        self._notation_labels: list[tkinter.Label] = []
        white_perspective = self._is_white_perspective()

        # Draw all the file letters
        for col in range(1, 9):
            # Label on top
            x, y = self._square_to_coords(8, col)
            x += TOTAL_SQUARE // 2
            if not white_perspective:
                y -= 7 * TOTAL_SQUARE
            y -= BOARD_BORDER + BOARD_OUTLINE // 2
            top_label = tkinter.Label(self, text="abcdefgh"[col - 1], font=TEXT_FONT)
            top_label.place(x=x, y=y, anchor=tkinter.CENTER)
            self._notation_labels.append(top_label)

            # Label on bottom
            _, y = self._square_to_coords(1, col)
            if not white_perspective:
                y += 7 * TOTAL_SQUARE
            y += TOTAL_SQUARE + BOARD_BORDER + BOARD_OUTLINE // 2
            bottom_label = tkinter.Label(self, text="abcdefgh"[col - 1], font=TEXT_FONT)
            bottom_label.place(x=x, y=y, anchor=tkinter.CENTER)
            self._notation_labels.append(bottom_label)

        # Draw all the rank numbers
        for row in range(1, 9):
            # Label on the left
            x, y = self._square_to_coords(row, 1)
            if not white_perspective:
                x -= 7 * TOTAL_SQUARE
            x -= BOARD_BORDER + BOARD_OUTLINE // 2
            y += TOTAL_SQUARE // 2
            left_label = tkinter.Label(self, text=str(row), font=TEXT_FONT)
            left_label.place(x=x, y=y, anchor=tkinter.CENTER)
            self._notation_labels.append(left_label)

            # Label on the right
            x, _ = self._square_to_coords(row, 8)
            if not white_perspective:
                x += 7 * TOTAL_SQUARE
            x += TOTAL_SQUARE + BOARD_BORDER + BOARD_OUTLINE // 2
            right_label = tkinter.Label(self, text=str(row), font=TEXT_FONT)
            right_label.place(x=x, y=y, anchor=tkinter.CENTER)
            self._notation_labels.append(right_label)

    def _create_color_circle(self):
        """
        Creates the circle representing the color to move on the board,
        and saves the object id to update later
        """
        circle_loc = BOARD_SIZE + int(1.5 * BOARD_OUTLINE) + 2 * BOARD_BORDER
        self._color_circle = self.create_oval(
            circle_loc - CIRCLE_RADIUS,
            circle_loc - CIRCLE_RADIUS,
            circle_loc + CIRCLE_RADIUS,
            circle_loc + CIRCLE_RADIUS,
            width=2,
        )

    def add_observer(self, observer):
        """
        Adds an observer of the board
        observer: object with notify(move, new_board) method
        """
        self._observers.append(observer)

    def remove_observer(self, observer):
        """
        Removes an observer of the board
        observer: object with notify(move, new_board) method
        """
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def _notify_observers(self, move: moves.Move, new_board: BoardState):
        """
        Notifies all observers of the move that was made
        """
        for observer in self._observers:
            observer.notify(move, new_board)

    def set_perspective(self, new_perspective: Perspective):
        """
        Sets the perspective to use
        new_perspective: Perspective to update to
        """
        self._perspective = new_perspective
        self._draw_clean_board()
        self.update()

    def set_theme(self, new_theme: Theme):
        """
        Sets the new theme to use
        new_theme: Theme to update to
        """
        self._theme = new_theme

        # Update board outline, border, and square colors
        outline_color = self._theme.board_outline()
        self.configure(bg=outline_color)
        self.itemconfig(self._border_id, fill=self._theme.board_border())
        self._update_squares()

        # Update notation text colors
        text_color = self._theme.board_text()
        for label in self._notation_labels:
            label.config(bg=outline_color, fg=text_color)

    def set_board(self, new_board: BoardState):
        """
        Sets the new board to draw
        new_board: BoardState to update to
        """
        old_perspective = self._is_white_perspective()
        self._board = new_board
        if old_perspective != self._is_white_perspective():
            # Perspective changed; need to redraw the board
            self._draw_clean_board()
        else:
            # Just reset and update the squares
            self._reset_squares()
            self._update_squares()
        if new_board.white_to_move():
            self.itemconfig(self._color_circle, fill="white")
        else:
            self.itemconfig(self._color_circle, fill="black")
        self._draw_pieces()

    def _draw_clean_board(self):
        """
        Redraws the board and pieces.
        NOTE: Things could be done in a cleaner manner
        """
        self._create_squares()
        self._reset_squares()
        self._set_up_notation()
        self.set_theme(self._theme)  # Just using this to update the notation labels
        self._draw_pieces()

    def _reset_squares(self):
        """
        Resets the focus/highlight properties of all the squares
        """
        for row in self._squares:
            for square in row:
                square.reset()

    def _draw_pieces(self):
        """
        Clears the list of images and redraws all the pieces
        """
        # Draw the pieces on the board
        self._images.clear()
        for row in range(1, 9):
            for col in range(1, 9):
                # Draw the piece at this square
                piece = self._board.get_piece(row, col)
                if piece is not None:
                    # Need to draw this piece
                    image = piece_to_image(piece, dim=(TOTAL_SQUARE, TOTAL_SQUARE))
                    image = ImageTk.PhotoImage(image)
                    self._images.append(
                        image
                    )  # save so it doesn't get garbage collected
                    x, y = self._square_to_coords(row, col)
                    self.create_image(x, y, anchor=tkinter.NW, image=image)
        self.update()

    def on_left_click(self, event):
        """
        Left click event handler
        event: Event to handle
        """
        row, col = self._coords_to_square(event.x, event.y)
        if 1 <= row <= 8 and 1 <= col <= 8:
            # Valid click location
            piece = self._board.get_piece(row, col)
            if piece is not None and piece.is_white() == self._board.white_to_move():
                # Clicked on one of the current player's pieces
                self._reset_squares()
                possible_moves = piece.get_moves(
                    self._board, Coordinate.from_coords(row, col)
                )

                # Place focus on clicked square
                self._squares[row - 1][col - 1].focus = True

                # Highlight all the target squares
                for move in possible_moves:
                    row, col = move.target.row, move.target.col
                    square = self._squares[row - 1][col - 1]
                    square.highlight = True
                    square.move = move
            elif self._squares[row - 1][col - 1].highlight:
                move = self._squares[row - 1][col - 1].move
                if type(move) == moves.PawnPromotion:
                    # Need to ask user what piece to promote to
                    popup = PawnPromotionPopup(
                        self._root_window, self._board.white_to_move()
                    )
                    move.set_promotion(popup.get_choice().__class__)
                new_board = self._board.make_move(move)
                self.set_board(new_board)
                self._notify_observers(move, new_board)
            else:
                self._reset_squares()
        else:
            self._reset_squares()

        # Update the square colors
        self._update_squares()
        self.update()

    def _create_squares(self):
        # Draw the board
        self._squares: list[list[Square]] = []
        for row in range(1, 9):
            self._squares.append([])
            for col in range(1, 9):
                # Draw the square at (row, col)
                square_id = self._create_square(row, col)
                self._squares[-1].append(Square(square_id))

    def _create_square(self, row: int, col: int):
        """
        Draws a square on the board at the given square
        row: int, representing the row of the square (1 - 8)
        col: int, representing the column of the square (1 - 8)
        Return: int, representing the object id of the rectangle drawn
        """
        x, y = self._square_to_coords(row, col)
        return self.create_rectangle(
            x, y, x + SQUARE_SIZE, y + SQUARE_SIZE, width=SQUARE_OUTLINE
        )

    def _update_squares(self):
        """
        Updates the fill/outline of all the squares in the canvas
        """
        for row in range(1, 9):
            for col in range(1, 9):
                square = self._squares[row - 1][col - 1]
                self.itemconfig(
                    square.get_id(),
                    fill=self._theme.square_bg(
                        row, col, focus=square.focus, highlight=square.highlight
                    ),
                    outline=self._theme.square_outline(
                        row, col, focus=square.focus, highlight=square.highlight
                    ),
                )

    def _square_to_coords(self, row: int, col: int):
        """
        Gets the pixel location to draw a square at
        row: int, representing the row of the square (1 - 8)
        col: int, representing the column of the square (1 - 8)
        Return: (x, y) pixel location
        """
        if self._is_white_perspective():
            # White orientation
            x = col - 1
            y = 8 - row
        else:
            # Black orientation
            x = 8 - col
            y = row - 1

        x = x * TOTAL_SQUARE + BOARD_OUTLINE + BOARD_BORDER
        y = y * TOTAL_SQUARE + BOARD_OUTLINE + BOARD_BORDER
        return x, y

    def _coords_to_square(self, x: int, y: int):
        """
        Converts the pixel location to the square selected
        x: int, representing the x location on the canvas
        y: int, representing the y location on the canvas
        Return: (row, col), representing the square (1 - 8 for each)
        """
        x -= BOARD_OUTLINE + BOARD_BORDER
        y -= BOARD_OUTLINE + BOARD_BORDER
        if self._is_white_perspective():
            # White orientation
            col = 1 + x // TOTAL_SQUARE
            row = 8 - y // TOTAL_SQUARE
        else:
            # Black orientation
            col = 8 - x // TOTAL_SQUARE
            row = 1 + y // TOTAL_SQUARE

        return (row, col)

    def _is_white_perspective(self):
        """
        Checks if the board is currently showing white's perspective.
        Return: True if white, False if black
        """
        match self._perspective:
            case Perspective.WHITE:
                return True
            case Perspective.BLACK:
                return False
            case Perspective.TO_MOVE:
                return self._board.white_to_move()

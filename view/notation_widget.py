"""
File: notation_widget.py
Author: Gavin Vogt
This program defines the NotationWidget class, which can be used
for displaying the notation in a chess game

Used tutorial at https://blog.teclado.com/tkinter-scrollable-frames/
"""

# dependencies
import tkinter
from tkinter import ttk

WIDGET_HEIGHT = 590
WIDGET_WIDTH = 230
MOVE_WIDTH = 48
NOTATION_WIDTH = (WIDGET_WIDTH - MOVE_WIDTH) // 2


class NotationWidget(ttk.Frame):
    """
    This class is a frame for holding the notation in the chess game. It has
    a scrollbar for scrolling through the notation once it is long enough

    Useful methods:
      - add_move()
      - remove_last()
      - add_score()
    """

    def __init__(self, root: tkinter.Frame):
        """
        Constructs a widget to hold notation in a scrollable container
        root: tkinter root window
        """
        super().__init__(root, borderwidth=2, relief=tkinter.GROOVE)
        self._canvas = tkinter.Canvas(self, height=WIDGET_HEIGHT, width=WIDGET_WIDTH)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._set_up_frame()
        self._canvas.configure(yscrollcommand=scrollbar.set)

        self._canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Prepare to hold notation
        self._row = -1
        self._score = None
        self._last_move = None
        self._last_color = None
        self._scrollable_frame.columnconfigure(0, minsize=MOVE_WIDTH)  # move number
        self._scrollable_frame.columnconfigure(
            1, minsize=NOTATION_WIDTH, pad=2
        )  # white moves
        self._scrollable_frame.columnconfigure(2, minsize=NOTATION_WIDTH)  # black moves

    def clear(self):
        """
        Clears everything in the scrollable frame
        """
        self._row = -1
        self._score = None
        self._last_move = None
        self._last_color = None
        for widget in self._scrollable_frame.winfo_children():
            widget.destroy()

    def add_move(self, move_num: int, notation: str, color: bool):
        """
        Adds a move to the notation widget
        move_num: int, representing the move number of the move made
        notation: str, representing the notation for the move made
        color: bool, True for white and False for black move
        """
        if self._last_move != move_num:
            # On to next move
            self._row += 1
            if self._row < 0:
                self._row = 0
            ttk.Label(self._scrollable_frame, text=str(move_num)).grid(
                row=self._row, column=0, sticky=tkinter.W
            )
            if color is None or not color:
                # Skipped to black's move
                ttk.Label(self._scrollable_frame, text="...").grid(
                    row=self._row, column=1, sticky=tkinter.W
                )
        elif self._row < 0:
            self._row = 0

        # Notation for this move
        col = 1 if color else 2
        ttk.Label(self._scrollable_frame, text=notation).grid(
            row=self._row, column=col, sticky=tkinter.W
        )
        self._last_move = move_num
        self._last_color = color

    def remove_last(self):
        """
        Removes the last move that was added to notation
        """
        if self._row >= 0:
            # Remove score label
            if self._score is not None:
                self._delete_widgets(self._row, 0)
                self._score = None
                self._row -= 1

            if self._last_color:
                # removing white move + number (an entire row)
                self._delete_widgets(self._row, 0)
                self._delete_widgets(self._row, 1)
                self._last_move -= 1
                self._row -= 1
            else:
                # removing black move
                self._delete_widgets(self._row, 2)
            self._last_color = not self._last_color
        else:
            self.clear()

    def _delete_widgets(self, row: int, col: int):
        """
        Deletes all the widgets in the grid located at (row, col)
        row: int, representing the row location in the grid
        col: int, representing the column location in the grid
        """
        for widget in self._scrollable_frame.grid_slaves(row, col):
            widget.grid_remove()

    def add_score(self, score_text: str):
        """
        Adds the score text at the bottom of the notation
        """
        self._row += 1
        if self._row < 0:
            self._row = 0
        self._score = ttk.Label(self._scrollable_frame, text=score_text)
        self._score.grid(row=self._row, column=0, columnspan=3)

    def _set_up_frame(self):
        """
        Sets up the scrollable frame
        """
        self._scrollable_frame = ttk.Frame(self._canvas)
        self._scrollable_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")),
        )
        self._canvas.create_window(
            (0, 0), window=self._scrollable_frame, anchor=tkinter.NW
        )

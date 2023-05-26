"""
File: pawn_promotion_popup.py
Author: Gavin Vogt
This program defines the PawnPromotionPopup class for use in
getting the user's promotion choice
"""

# dependencies
import tkinter
from PIL import ImageTk

# my code
from model import pieces
from .view_utils import center_window_on_root, piece_to_image


def disable_event():
    pass


class PromotionOption(tkinter.Frame):
    """
    This class represents a pawn promotion option
    """

    def __init__(
        self,
        root: tkinter.Toplevel,
        popup: "PawnPromotionPopup",
        piece: pieces.Piece,
        index: int,
    ):
        """
        Constructs a new promotion option
        root: tkinter root window
        popup: PawnPromotionPopup this option is part of
        piece: Piece associated with this option
        index: int, representing the index of this option
        """
        super().__init__(root)
        self._piece = piece

        # Create the image label
        self._image = ImageTk.PhotoImage(piece_to_image(piece))
        label = tkinter.Label(self, image=self._image)
        label.bind("<Button-1>", lambda _: popup.update_selection(index))
        label.pack(padx=4, pady=4)

    def get_piece(self):
        """
        Gets the piece associated with this option
        """
        return self._piece


class PawnPromotionPopup:
    """
    This class represents a popup for asking the user which piece
    type to promote a pawn to.
    """

    def __init__(self, root: tkinter.Tk, color: bool):
        """
        Constructs a popup to ask the user what piece to promote
        the pawn to
        root: tkinter root window
        color: bool, True for white and False for black
        """
        self._popup = tkinter.Toplevel(root)
        self._popup.title("Select Pawn Promotion")
        self._popup.grab_set()
        self._popup.resizable(False, False)
        self._popup.protocol("WM_DELETE_WINDOW", disable_event)

        # Create the options
        self._options: list[PromotionOption] = []
        self._selected = -1
        piece_types = (pieces.Knight, pieces.Bishop, pieces.Rook, pieces.Queen)
        for piece_type in piece_types:
            self._selected += 1
            piece = piece_type(color)
            option = PromotionOption(self._popup, self, piece, self._selected)
            option.grid(row=0, column=self._selected)
            self._options.append(option)
        self.update_selection(self._selected)

        # Create the button to select option
        tkinter.Button(self._popup, text="Promote", command=self._popup.destroy).grid(
            row=1,
            column=0,
            columnspan=len(piece_types),
            padx=5,
            pady=5,
            sticky=tkinter.E,
        )

        center_window_on_root(self._popup, root)

    def update_selection(self, index: int):
        """
        Updates the selected piece index
        index: int, representing the newly selected piece to promote to
        """
        defaultbg = self._popup.cget("bg")
        self._options[self._selected].config(bg=defaultbg)
        self._options[index].config(bg="#C65102")
        self._selected = index

    def get_choice(self) -> pieces.Piece:
        """
        Gets the Piece chosen to promote to by the player. Waits until
        the popup window is destroyed to return choice
        """
        self._popup.wait_window()
        return self._options[self._selected].get_piece()

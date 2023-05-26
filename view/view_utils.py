"""
File: view_utils.py
Author: Gavin Vogt
This program provides utility functions for working with the piece images
"""

# dependencies
import tkinter
from PIL import Image
from typing import Union, Optional

# my code
from model.pieces import Piece


def center_window_on_screen(window: Union[tkinter.Tk, tkinter.Toplevel]):
    """
    Centers the given window on the screen
    """
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    x, y = _find_center(window, width, height)
    window.geometry(f"+{x}+{y}")


def center_window_on_root(
    window: Union[tkinter.Tk, tkinter.Toplevel], root: tkinter.Tk
):
    """
    Centers the given window on the root window. Assumes root is
    already updated
    """
    width = root.winfo_width()
    height = root.winfo_height()
    x, y = _find_center(window, width, height)
    window.geometry(f"+{x + root.winfo_x()}+{y + root.winfo_y()}")


def _find_center(window: Union[tkinter.Tk, tkinter.Toplevel], width: int, height: int):
    """
    Finds the (x, y) location to place the window at in order to center
    it in an area of given width/height
    window: window to center
    width: int, representing the width to center it in
    height: int, representing the height to center it in
    Return: (x, y) to place window at to center in area
    """
    window.update()

    # Get width/height of app
    app_width = window.winfo_width()
    app_height = window.winfo_height()

    # Calculate center location
    x = width // 2 - app_width // 2
    y = height // 2 - app_height // 2
    return (x, y)


# Load all the images beforehand
IMAGES: dict[str, Image.Image] = {}
for color in ("white", "black"):
    for piece_name in ("pawn", "knight", "bishop", "rook", "queen", "king"):
        key = f"{color}_{piece_name}"
        IMAGES[key] = Image.open(f"images/{key}.png")


def piece_to_image(piece: Piece, *, dim: Optional[tuple[int, int]] = None):
    """
    Returns the image for the given piece. Memoizes requests for specific
    dimensions to improve speed.
    piece: Piece object aware of piece type and color
    dim: tuple of (width, height) to resize the image to
    Return: Image object
    """
    # Determine piece color and name
    if piece.is_white():
        color = "white"
    else:
        color = "black"
    piece_name = piece.__class__.__name__.lower()

    # Resize if necessary
    key = f"{color}_{piece_name}"
    if dim is None:
        # No resizing needed
        image = IMAGES[key]
    else:
        # Need to return resized image
        resize_key = f"{key}_{dim[0]}_{dim[1]}"
        image = IMAGES.get(resize_key)
        if image is None:
            # These dimensions haven't been requested before
            image = IMAGES[key].resize(dim, Image.ANTIALIAS)
            IMAGES[resize_key] = image

    # Return the correct image
    return image

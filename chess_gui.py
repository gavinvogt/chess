"""
File: chess_gui.py
Author: Gavin Vogt
This program lets the user play chess with a GUI.
"""

# dependencies
import tkinter
from PIL import ImageTk
import ctypes
import traceback
import pyperclip
import pickle

# my code
from model import ChessGame, BoardState, GameResult
from model.moves import Move
from view import (
    BoardCanvas,
    Perspective,
    NotationWidget,
    WoodTheme,
    DarkTheme,
    LightTheme,
    center_window_on_screen,
    center_window_on_root,
)
from view.themes import Theme

# Improve DPI
ctypes.windll.shcore.SetProcessDpiAwareness(1)

THEMES = {
    theme.get_name(): theme
    for theme in (
        DarkTheme(),
        LightTheme(),
        WoodTheme(),
    )
}

PERSPECTIVES = {
    perpective.get_name(): perpective
    for perpective in (Perspective.WHITE, Perspective.BLACK, Perspective.TO_MOVE)
}

SAVEFILE = "game.pickle"


def save_game(game: ChessGame):
    """
    Saves the game to file
    """
    with open(SAVEFILE, "wb") as f:
        pickle.dump(game, f)


def load_game():
    """
    Loads the previous game from file
    Return: ChessGame if successful, otherwise None
    """
    try:
        with open(SAVEFILE, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None


class ChessGui(tkinter.Tk):
    """
    This class represents the GUI for the entire chess game
    """

    def __init__(self, game: ChessGame, theme: Theme, perspective: Perspective):
        """
        Constructs a new chess game GUI
        game: ChessGame to store the game progress in
        theme: Theme to draw the UI + board with
        """
        super().__init__()
        self.title("Chess")
        self.iconphoto(True, ImageTk.PhotoImage(file="images/icon.ico"))
        self._game = game
        if len(game) == 0:
            game.push(BoardState())
        self._board_canvas = BoardCanvas(self, theme, perspective, game.current_state())
        self._board_canvas.grid(row=0, column=0, rowspan=5)
        tkinter.Label(
            self,
            text=" Written by Gavin Vogt",
            bd=1,
            relief=tkinter.SUNKEN,
            anchor=tkinter.W,
        ).grid(row=5, column=0, columnspan=4, sticky=tkinter.E + tkinter.W)
        self._board_canvas.add_observer(self)
        self._set_up_themes(theme)
        self._set_up_perspectives(perspective)
        self._set_up_notation()
        self._set_up_undo_button()
        tkinter.Button(self, text="Copy FEN", command=self._copy_fen_to_clipboard).grid(
            row=4, column=2, padx=(5, 0), sticky=tkinter.E + tkinter.W
        )
        tkinter.Button(self, text="New Game", command=self._new_game).grid(
            row=4, column=3, padx=(5, 5), sticky=tkinter.E + tkinter.W
        )
        self.bind("<Control-w>", lambda _: self.quit())
        self.protocol("WM_DELETE_WINDOW", self.quit)
        center_window_on_screen(self)

    def quit(self):
        """
        Adds game saving to normal quit operation
        """
        save_game(self._game)
        super().quit()

    def _set_up_themes(self, initial_theme: Theme):
        """
        Sets up the theme selection menu
        initial_theme: Theme to start with
        """
        option_selected = tkinter.StringVar()
        option_selected.set(initial_theme.get_name())
        menu = tkinter.OptionMenu(
            self,
            option_selected,
            *THEMES.keys(),
            command=lambda choice: self._board_canvas.set_theme(THEMES[choice])
        )
        tkinter.Label(self, text="Select Theme:").grid(
            row=0, column=1, columnspan=2, padx=3, pady=14, sticky=tkinter.NE
        )
        menu.grid(row=0, column=3, padx=(2, 7), pady=7, sticky=tkinter.N)

    def _set_up_perspectives(self, initial_perspective: Perspective):
        """
        Sets up the theme selection menu
        initial_theme: Theme to start with
        """
        option_selected = tkinter.StringVar()
        option_selected.set(initial_perspective.get_name())
        menu = tkinter.OptionMenu(
            self,
            option_selected,
            *PERSPECTIVES.keys(),
            command=lambda choice: self._board_canvas.set_perspective(
                PERSPECTIVES[choice]
            )
        )
        tkinter.Label(self, text="Select Perspective:").grid(
            row=1, column=1, columnspan=2, padx=3, pady=14, sticky=tkinter.NE
        )
        menu.grid(row=1, column=3, padx=(2, 7), pady=7, sticky=tkinter.N)

    def _set_up_notation(self):
        """
        Sets up the notation widget for displaying the chess game notation
        """
        tkinter.Label(self, text="Notation").grid(row=2, column=1, columnspan=3)
        self._notation = NotationWidget(self)
        self._notation.grid(row=3, column=1, columnspan=3, padx=5, sticky=tkinter.N)

    def _set_up_undo_button(self):
        """
        Sets up the Undo button for undoing a move
        """
        self._undo_button = tkinter.Button(self, text="Undo", command=self._undo_last)
        self._undo_button.grid(
            row=4, column=1, padx=(5, 0), sticky=tkinter.E + tkinter.W
        )
        self._check_undo_validity()

    def notify(self, move: Move, new_board: BoardState):
        """
        Notify the ChessGui of a move that was made, along with the newly
        created board
        move: Move that was executed
        new_board: new BoardState produced by the move
        """
        notation = move.to_notation(new_board)
        if new_board.white_to_move():
            # Move was made by black
            color = False
            move_num = new_board.fullmove() - 1
        else:
            # Move was made by white
            color = True
            move_num = new_board.fullmove()
        self._notation.add_move(move_num, notation, color)
        self._game.push(new_board)
        self._check_undo_validity()

        result = self._game.get_result()
        if result is not None:
            # Game is over
            self._notation.add_score(result.score_string())
            self._display_result(result)

    def _display_result(self, result: GameResult):
        """
        Displays the result of the game
        result: GameResult object holding the result of the game
        """
        # Create the result window
        top = tkinter.Toplevel(self, width=200, height=150)
        top.title("Game Over")
        top.grab_set()

        # Create the result content
        tkinter.Label(top, text=result.get_type(), font=("Roboto", 18)).pack(
            padx=100, pady=(20, 0)
        )
        tkinter.Label(top, text="by " + result.get_reason(), font=("Roboto", 11)).pack()
        tkinter.Label(top, text=result.score_string(), font=("Roboto", 12)).pack(
            pady=(10, 20)
        )
        center_window_on_root(top, self)

    def _copy_fen_to_clipboard(self):
        """
        Copies the FEN notation for the current board state to the
        user's clipboard
        """
        fen = self._game.current_state().to_fen()
        pyperclip.copy(fen)

    def _new_game(self):
        """
        Starts a new game
        """
        self._game = ChessGame()
        board = BoardState()
        self._game.push(board)
        self._board_canvas.set_board(board)
        self._notation.clear()
        self._check_undo_validity()

    def _check_undo_validity(self):
        """
        Checks if the undo button is valid, and sets it to enabled/disabled
        based on whether UNDO is a valid operation
        """
        if len(self._game) <= 1:
            # Not enough states to undo
            self._undo_button["state"] = tkinter.DISABLED
        else:
            # Can undo
            self._undo_button["state"] = tkinter.NORMAL

    def _undo_last(self):
        """
        Undoes the last move
        """
        # Remove last board state and update board canvas
        self._game.pop_last()
        self._board_canvas.set_board(self._game.current_state())

        # Remove last notation item and check undo button validity
        self._notation.remove_last()
        self._check_undo_validity()


def main():
    # Choose the default theme and perspective
    theme = WoodTheme()
    perspective = Perspective.WHITE

    # Create the chess game
    game = load_game()
    if game is None:
        game = ChessGame()
        game.push(BoardState())
    gui = ChessGui(game, theme, perspective)
    gui.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        input("Press enter ")

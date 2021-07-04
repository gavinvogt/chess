# Chess
This repository contains both text-based and GUI-based chess. The chess model includes the
abillity to detect stalemate, fifty-move rule, threefold repetition, insufficient material,
and checkmate.

# GUI Version
`chess_gui.py`
The graphical version of text includes multiple color themes for the board. It also displays
the notation as the game is played, and notifies the user when the game is over. It has buttons
to allow undoing the last move, copying the FEN notation of the current position to clipboard,
and starting a new game. Upon closing, the game automatically saves the state of the game to
be reloaded next time it is opened.

# Text Version
`chess_text.py`
Contains a move parser that can take moves of the form "{start}-{target}", as well as more
standard notation such as "Nf3" and "e8=Q+". Does not save or load games because I only
considered it to be worth the effort for the GUI version.

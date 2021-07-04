'''
File: themes.py
Author: Gavin Vogt
This program defines the themes for the chess GUI. Each one holds the
background color for squares

focus: square is clicked
highlight: square is highlighted to show potential moves
'''

# dependencies
import abc

def rgb2hex(r,g,b):
    # found online
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

class Theme(metaclass=abc.ABCMeta):
    '''
    This class represents a color theme to use for drawing the chess board
    '''
    @abc.abstractmethod
    def get_name(self):
        '''
        Gets the theme name
        Return: str, representing the name of the theme
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def square_bg(self, row: int, col: int, *, focus: bool = False, highlight: bool = False):
        '''
        Returns the string for the square background color in hex.
        row: int, representing the square row (1 - 8)
        col: int, representing the square column (1 - 8)
        focus: bool, representing whether the square is focused
        highlight: bool, representing whether the square is highlighted
        Return: str, representing the hex color to make the square
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def square_outline(self, row: int, col: int, *, focus: bool = False, highlight: bool = False):
        '''
        Returns the string for the square outline color in hex.
        row: int, representing the square row (1 - 8)
        col: int, representing the square column (1 - 8)
        focus: bool, representing whether the square is focused
        highlight: bool, representing whether the square is highlighted
        Return: str, representing the hex color to make the square's outline
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def board_border(self):
        '''
        Returns the string for the border color of the board. This means the thin
        border around the squares.
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def board_outline(self):
        '''
        Returns the string for the outline color of the board. This means the thicker
        padding around the board + border.
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def board_text(self):
        '''
        Returns the string for the text color inside the thick outline. This will
        be used to write the letters and numbers for the notation system
        '''
        raise NotImplementedError

    def is_dark(self, row: int, col: int):
        '''
        Whether the given square should be dark or light colored.
        row: int, representing the square row (1 - 8)
        col: int, representing the square column (1 - 8)
        Return: True if dark, False if light
        '''
        if (row + col) % 2 == 0:
            # Dark square
            return True
        else:
            # Light square
            return False

class WoodTheme(Theme):
    '''
    This class represents the wood theme for the chess board
    '''
    def get_name(self):
        return "Wood"

    def square_bg(self, row: int, col: int, *, focus: bool = False, highlight: bool = False):
        if focus:
            # Square is focused (clicked)
            if self.is_dark(row, col):
                return rgb2hex(217, 111, 111)     # light red
            else:
                return rgb2hex(247, 162, 104)     # light orange
        elif highlight:
            # Square is highlighted
            if self.is_dark(row, col):
                return rgb2hex(94, 155, 154)      # light aqua
            else:
                return rgb2hex(157, 215, 183)     # light sea green
        else:
            # Basic square
            if self.is_dark(row, col):
                return rgb2hex(92, 55, 49)        # dark brown
            else:
                return rgb2hex(206, 172, 145)     # light brown

    def square_outline(self, row: int, col: int, *, focus: bool = False, highlight: bool = False):
        if focus:
            # Square is focused (clicked)
            return rgb2hex(251, 85, 55)       # red
        elif highlight:
            # Square is highlighted
            return rgb2hex(69, 107, 239)      # midnight blue
        else:
            # Basic square
            if self.is_dark(row, col):
                return self.square_bg(row, col)
            else:
                return self.square_bg(row, col)

    def board_border(self):
        return rgb2hex(206, 172, 145)

    def board_outline(self):
        return rgb2hex(92, 55, 49)

    def board_text(self):
        return rgb2hex(206, 172, 145)

class DarkTheme(Theme):
    '''
    This class represents the dark theme for the chess board
    '''
    def get_name(self):
        return "Dark"

    def square_bg(self, row: int, col: int, *, focus: bool = False, highlight: bool = False):
        if focus:
            # Square is focused (clicked)
            if self.is_dark(row, col):
                return rgb2hex(171, 195, 243)    # light blue
            else:
                return rgb2hex(216, 196, 238)    # light purple
        elif highlight:
            # Square is highlighted
            if self.is_dark(row, col):
                return rgb2hex(168, 134, 148)
            else:
                return rgb2hex(241, 241, 152)
        else:
            # Basic square
            if self.is_dark(row, col):
                return rgb2hex(75, 96, 154)      # dark blue
            else:
                return rgb2hex(218, 208, 194)    # light beige

    def square_outline(self, row: int, col: int, *, focus: bool = False, highlight: bool = False):
        if focus:
            # Square is focused (clicked)
            return rgb2hex(4, 249, 151)         # greenish blue
        elif highlight:
            # Square is highlighted
            return rgb2hex(245, 103, 73)        # salmon red
        else:
            # Basic square
            if self.is_dark(row, col):
                return self.square_bg(row, col)
            else:
                return self.square_bg(row, col)

    def board_border(self):
        return rgb2hex(75, 96, 154)      # dark blue

    def board_outline(self):
        return rgb2hex(218, 208, 194)

    def board_text(self):
        return rgb2hex(75, 96, 154)      # dark blue

class LightTheme(Theme):
    '''
    This class represents the light theme for the chess board
    '''
    def get_name(self):
        return "Light"

    def square_bg(self, row: int, col: int, *, focus: bool = False, highlight: bool = False):
        if focus:
            # Square is focused (clicked)
            if self.is_dark(row, col):
                return rgb2hex(187, 223, 132)   # lighter green
            else:
                return rgb2hex(186, 237, 245)   # light blue
        elif highlight:
            # Square is highlighted
            if self.is_dark(row, col):
                return rgb2hex(186, 193, 55)    # yellowish green
            else:
                return rgb2hex(248, 240, 132)   # light yellow
        else:
            # Basic square
            if self.is_dark(row, col):
                return rgb2hex(121, 149, 91)    # darker green
            else:
                return rgb2hex(238, 238, 213)   # light cream

    def square_outline(self, row: int, col: int, *, focus: bool = False, highlight: bool = False):
        if focus:
            # Square is focused (clicked)
            return rgb2hex(42, 251, 165)        # greenish blue
        elif highlight:
            # Square is highlighted
            return rgb2hex(255, 164, 30)        # orange
        else:
            # Basic square
            if self.is_dark(row, col):
                return self.square_bg(row, col)
            else:
                return self.square_bg(row, col)

    def board_border(self):
        return rgb2hex(121, 149, 91)

    def board_outline(self):
        return rgb2hex(238, 238, 213)

    def board_text(self):
        return rgb2hex(121, 149, 91)



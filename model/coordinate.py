"""
File: coordinate.py
Author: Gavin Vogt
This program defines the class used for representing the coordinates
of a square on the board
"""


class Coordinate:
    """
    This class represents a coordinate on the chess board.

    Useful properties:
      - row
      - col

    Useful methods:
      - to_notation()
    """

    __slots__ = ("_row", "_col")

    def __init__(self, row: int, col: int):
        """
        Constructs a new Coordinate for the given row and column
        row: int, representing the row of the square (1 - 8)
        col: int, representing the column of the square (1 - 8)
        """
        self._row = row
        self._col = col

    def __repr__(self):
        """
        Defines the string representation of the Coordinate
        """
        return f"<{self.__class__.__name__}({self._row}, {self._col})>"

    def __eq__(self, other: object):
        """
        Checks if two Coordinate objects are equal
        """
        if isinstance(other, Coordinate):
            return (self._row == other._row) and (self._col == other._col)
        else:
            return NotImplemented

    @property
    def row(self):
        """
        Allows read-only access to the `row` value
        """
        return self._row

    @property
    def col(self):
        """
        Allows read-only access to the `col` value
        """
        return self._col

    def is_valid(self):
        """
        Checks if this Coordinate is a valid location on the board
        Return: True if valid, False otherwise
        """
        return (1 <= self._row <= 8) and (1 <= self._col <= 8)

    @staticmethod
    def from_coords(row: int, col: int):
        """
        Converts the given coordinates into a Coordinate
        row: int, representing the row of the square
        col: int, representing the column of the square
        Return: Coordinate for the given location
        """
        if 1 <= row <= 8 and 1 <= col <= 8:
            return Coordinate(row, col)
        else:
            raise InvalidCoordinateError(f"Invalid coordinate: {row}, {col}")

    @classmethod
    def from_notation(cls, square_name: str):
        """
        Converts the algebraic notation name for a square to the corresponding coordinate.
        square_name: str, representing the algebraic notation for the square
        Return: Coordinate for the named location
        """
        if len(square_name) != 2:
            raise InvalidCoordinateError(f"Invalid coordinate: {square_name}")
        try:
            col = "abcdefgh".index(square_name[0].lower()) + 1
            row = int(square_name[1])
            return cls.from_coords(row, col)
        except Exception:
            raise InvalidCoordinateError(f"Invalid coordinate: {square_name}")

    def to_notation(self):
        """
        Converts the Coordinate to the string for its notation
        Return: str, representing the algebraic notation for this coordinate
        """
        return "abcdefgh"[self._col - 1] + str(self._row)


class InvalidCoordinateError(ValueError):
    """
    This class represents an Exception thrown when an invalid coordinate
    is given.
    """

    pass

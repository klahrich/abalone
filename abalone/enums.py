# -*- coding: utf-8 -*-

# Copyright 2020 Scriptim (https://github.com/Scriptim)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""This module provides some enumerations to represent the state of a game."""

from enum import Enum
from typing import Tuple

from colorama import Fore, Style

SIZE = 40
X_A1 = SIZE*3
Y_A1 = SIZE


class Player(Enum):
    """Enumeration of the two players."""
    value: int
    WHITE = -1
    """White player."""
    BLACK = 1
    """Black player."""


class Marble(Enum):
    """Enumeration of the states of a space."""
    value: int
    WHITE = Player.WHITE.value
    """Space contains white marble."""
    BLANK = 0
    """Space contains no marble."""
    BLACK = Player.BLACK.value
    """Space contains black marble."""

    def __str__(self) -> str:
        if self is Marble.WHITE:
            return Fore.WHITE + u'\u25CF' + Fore.RESET
        if self is Marble.BLACK:
            return Fore.BLUE + u'\u25CF' + Fore.RESET
        return Style.DIM + u'\u00B7' + Style.NORMAL


class Space(Enum):
    """Enumeration of all spaces of the board.

    ```
        I · · · · ·
       H · · · · · ·
      G · · · · · · ·
     F · · · · · · · ·
    E · · · · · · · · ·
     D · · · · · · · · 9
      C · · · · · · · 8
       B · · · · · · 7
        A · · · · · 6
           1 2 3 4 5
    ```
    """
    value: Tuple[str, ...]
    OFF = ('OFF',)
    """Represents everything off the board, e. g. when a marble has been pushed off the board."""
    A1 = ('A', '1', X_A1, Y_A1)
    """A1"""
    A2 = ('A', '2', X_A1 + SIZE, Y_A1)
    """A2"""
    A3 = ('A', '3', X_A1 + SIZE*2, Y_A1)
    """A3"""
    A4 = ('A', '4', X_A1 + SIZE*3, Y_A1)
    """A4"""
    A5 = ('A', '5', X_A1 + SIZE*4, Y_A1)
    """A5"""
    B1 = ('B', '1', X_A1 - SIZE*0.5, Y_A1 + SIZE)
    """B1"""
    B2 = ('B', '2', X_A1 + SIZE*0.5, Y_A1 + SIZE)
    """B2"""
    B3 = ('B', '3', X_A1 + SIZE*1.5, Y_A1 + SIZE)
    """B3"""
    B4 = ('B', '4', X_A1 + SIZE*2.5, Y_A1 + SIZE)
    """B4"""
    B5 = ('B', '5', X_A1 + SIZE*3.5, Y_A1 + SIZE)
    """B5"""
    B6 = ('B', '6', X_A1 + SIZE*4.5, Y_A1 + SIZE)
    """B6"""
    C1 = ('C', '1', X_A1 - SIZE, Y_A1 + SIZE*2)
    """C1"""
    C2 = ('C', '2', X_A1 + 0, Y_A1 + SIZE*2)
    """C2"""
    C3 = ('C', '3', X_A1 + SIZE*1, Y_A1 + SIZE*2)
    """C3"""
    C4 = ('C', '4', X_A1 + SIZE*2, Y_A1 + SIZE*2)
    """C4"""
    C5 = ('C', '5', X_A1 + SIZE*3, Y_A1 + SIZE*2)
    """C5"""
    C6 = ('C', '6', X_A1 + SIZE*4, Y_A1 + SIZE*2)
    """C6"""
    C7 = ('C', '7', X_A1 + SIZE*5, Y_A1 + SIZE*2)
    """C7"""
    D1 = ('D', '1', X_A1 - SIZE*1.5, Y_A1 + SIZE*3)
    """D1"""
    D2 = ('D', '2', X_A1 - SIZE*0.5, Y_A1 + SIZE*3)
    """D2"""
    D3 = ('D', '3', X_A1 + SIZE*0.5, Y_A1 + SIZE*3)
    """D3"""
    D4 = ('D', '4', X_A1 + SIZE*1.5, Y_A1 + SIZE*3)
    """D4"""
    D5 = ('D', '5', X_A1 + SIZE*2.5, Y_A1 + SIZE*3)
    """D5"""
    D6 = ('D', '6', X_A1 + SIZE*3.5, Y_A1 + SIZE*3)
    """D6"""
    D7 = ('D', '7', X_A1 + SIZE*4.5, Y_A1 + SIZE*3)
    """D7"""
    D8 = ('D', '8', X_A1 + SIZE*5.5, Y_A1 + SIZE*3)
    """D8"""
    E1 = ('E', '1', X_A1 - SIZE*2, Y_A1 + SIZE*4)
    """E1"""
    E2 = ('E', '2', X_A1 - SIZE*1, Y_A1 + SIZE*4)
    """E2"""
    E3 = ('E', '3', X_A1 - SIZE*0, Y_A1 + SIZE*4)
    """E3"""
    E4 = ('E', '4', X_A1 + SIZE*1, Y_A1 + SIZE*4)
    """E4"""
    E5 = ('E', '5', X_A1 + SIZE*2, Y_A1 + SIZE*4)
    """E5"""
    E6 = ('E', '6', X_A1 + SIZE*3, Y_A1 + SIZE*4)
    """E6"""
    E7 = ('E', '7', X_A1 + SIZE*4, Y_A1 + SIZE*4)
    """E7"""
    E8 = ('E', '8', X_A1 + SIZE*5, Y_A1 + SIZE*4)
    """E8"""
    E9 = ('E', '9', X_A1 + SIZE*6, Y_A1 + SIZE*4)
    """E9"""
    F2 = ('F', '2', X_A1 - SIZE*1.5, Y_A1 + SIZE*5)
    """F2"""
    F3 = ('F', '3', X_A1 - SIZE*0.5, Y_A1 + SIZE*5)
    """F3"""
    F4 = ('F', '4', X_A1 + SIZE*0.5, Y_A1 + SIZE*5)
    """F4"""
    F5 = ('F', '5', X_A1 + SIZE*1.5, Y_A1 + SIZE*5)
    """F5"""
    F6 = ('F', '6', X_A1 + SIZE*2.5, Y_A1 + SIZE*5)
    """F6"""
    F7 = ('F', '7', X_A1 + SIZE*3.5, Y_A1 + SIZE*5)
    """F7"""
    F8 = ('F', '8', X_A1 + SIZE*4.5, Y_A1 + SIZE*5)
    """F8"""
    F9 = ('F', '9', X_A1 + SIZE*5.5, Y_A1 + SIZE*5)
    """F9"""
    G3 = ('G', '3', X_A1 - SIZE*1.0, Y_A1 + SIZE*6)
    """G3"""
    G4 = ('G', '4', X_A1 - SIZE*0, Y_A1 + SIZE*6)
    """G4"""
    G5 = ('G', '5', X_A1 + SIZE*1.0, Y_A1 + SIZE*6)
    """G5"""
    G6 = ('G', '6', X_A1 + SIZE*2.0, Y_A1 + SIZE*6)
    """G6"""
    G7 = ('G', '7', X_A1 + SIZE*3.0, Y_A1 + SIZE*6)
    """G7"""
    G8 = ('G', '8', X_A1 + SIZE*4.0, Y_A1 + SIZE*6)
    """G8"""
    G9 = ('G', '9', X_A1 + SIZE*5.0, Y_A1 + SIZE*6)
    """G9"""
    H4 = ('H', '4', X_A1 - SIZE*0.5, Y_A1 + SIZE*7)
    """H4"""
    H5 = ('H', '5', X_A1 + SIZE*0.5, Y_A1 + SIZE*7)
    """H5"""
    H6 = ('H', '6', X_A1 + SIZE*1.5, Y_A1 + SIZE*7)
    """H6"""
    H7 = ('H', '7', X_A1 + SIZE*2.5, Y_A1 + SIZE*7)
    """H7"""
    H8 = ('H', '8', X_A1 + SIZE*3.5, Y_A1 + SIZE*7)
    """H8"""
    H9 = ('H', '9', X_A1 + SIZE*4.5, Y_A1 + SIZE*7)
    """H9"""
    I5 = ('I', '5', X_A1 + SIZE*0, Y_A1 + SIZE*8)
    """I5"""
    I6 = ('I', '6', X_A1 + SIZE, Y_A1 + SIZE*8)
    """I6"""
    I7 = ('I', '7', X_A1 + SIZE*2, Y_A1 + SIZE*8)
    """I7"""
    I8 = ('I', '8', X_A1 + SIZE*3, Y_A1 + SIZE*8)
    """I8"""
    I9 = ('I', '9', X_A1 + SIZE*4, Y_A1 + SIZE*8)
    """I9"""


class Direction(Enum):
    """Enumeration of the six directions in which marbles can be moved."""
    value: str
    NORTH_EAST = 'north-east'
    """North East (↗), Alias: `NE`"""
    NE = NORTH_EAST
    EAST = 'east'
    """East (→), Alias: `E`"""
    E = EAST
    SOUTH_EAST = 'south-east'
    """South East (↘), Alias: `SE`"""
    SE = SOUTH_EAST
    SOUTH_WEST = 'south-west'
    """South West (↙), Alias: `SW`"""
    SW = SOUTH_WEST
    WEST = 'west'
    """West (←), Alias: `W`"""
    W = WEST
    NORTH_WEST = 'north-west'
    """North West (↖), Alias: `NW`"""
    NW = NORTH_WEST


class InitialPosition(Enum):
    """A small collection of commonly used initial positions."""
    value: list
    DEFAULT = [
        [Marble.WHITE] * 5,
        [Marble.WHITE] * 6,
        [Marble.BLANK] * 2 + [Marble.WHITE] * 3 + [Marble.BLANK] * 2,
        [Marble.BLANK] * 8,
        [Marble.BLANK] * 9,
        [Marble.BLANK] * 8,
        [Marble.BLANK] * 2 + [Marble.BLACK] * 3 + [Marble.BLANK] * 2,
        [Marble.BLACK] * 6,
        [Marble.BLACK] * 5
    ]
    """
    ```
        I O O O O O
       H O O O O O O
      G · · O O O · ·
     F · · · · · · · ·
    E · · · · · · · · ·
     D · · · · · · · · 9
      C · · @ @ @ · · 8
       B @ @ @ @ @ @ 7
        A @ @ @ @ @ 6
           1 2 3 4 5
    ```
    """
    GERMAN_DAISY = [
        [Marble.BLANK] * 5,
        [Marble.WHITE] * 2 + [Marble.BLANK] * 2 + [Marble.BLACK] * 2,
        [Marble.WHITE] * 3 + [Marble.BLANK] * 1 + [Marble.BLACK] * 3,
        [Marble.BLANK] + [Marble.WHITE] * 2 + [Marble.BLANK] * 2 + [Marble.BLACK] * 2 + [Marble.BLANK],
        [Marble.BLANK] * 9,
        [Marble.BLANK] + [Marble.BLACK] * 2 + [Marble.BLANK] * 2 + [Marble.WHITE] * 2 + [Marble.BLANK],
        [Marble.BLACK] * 3 + [Marble.BLANK] * 1 + [Marble.WHITE] * 3,
        [Marble.BLACK] * 2 + [Marble.BLANK] * 2 + [Marble.WHITE] * 2,
        [Marble.BLANK] * 5
    ]
    """
    ```
        I · · · · ·
       H O O · · @ @
      G O O O · @ @ @
     F · O O · · @ @ ·
    E · · · · · · · · ·
     D · @ @ · · O O · 9
      C @ @ @ · O O O 8
       B @ @ · · O O 7
        A · · · · · 6
           1 2 3 4 5
    ```
    """
    BELGIAN_DAISY = [
        [Marble.WHITE] * 2 + [Marble.BLANK] + [Marble.BLACK] * 2,
        [Marble.WHITE] * 3 + [Marble.BLACK] * 3,
        [Marble.BLANK] + [Marble.WHITE] * 2 + [Marble.BLANK] + [Marble.BLACK] * 2 + [Marble.BLANK],
        [Marble.BLANK] * 8,
        [Marble.BLANK] * 9,
        [Marble.BLANK] * 8,
        [Marble.BLANK] + [Marble.BLACK] * 2 + [Marble.BLANK] + [Marble.WHITE] * 2 + [Marble.BLANK],
        [Marble.BLACK] * 3 + [Marble.WHITE] * 3,
        [Marble.BLACK] * 2 + [Marble.BLANK] + [Marble.WHITE] * 2
    ]
    """
    ```
        I O O · @ @
       H O O O @ @ @
      G · O O · @ @ ·
     F · · · · · · · ·
    E · · · · · · · · ·
     D · · · · · · · · 9
      C · @ @ · O O · 8
       B @ @ @ O O O 7
        A @ @ · O O 6
           1 2 3 4 5
    ```
    """

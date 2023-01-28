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

"""This module provides some functions to simplify various operations."""

from typing import List, Tuple, Union

from abalone.enums import Direction, Space, Player, Marble
import numpy as np
import pickle




class Utils:

    with open('neighbors.pkl', 'rb') as f:
        neighbors_table = pickle.load(f)

    @classmethod
    def neighbor(cls, space:Space, direction:Direction) -> Space:
        return Utils.neighbors_table[space.name + direction.name]



def space_to_board_indices(space: Space) -> Tuple[int, int]:
    """Returns the corresponding index for `self.board` of a given `abalone.enums.Space`.

    Args:
        space: The `abalone.enums.Space` for which the indices are wanted.

    Returns:
        An int tuple containing two indices for `self.board`.
    """

    xs = ['I', 'H', 'G', 'F', 'E', 'D', 'C', 'B', 'A']
    ys = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

    x = xs.index(space.value[0])
    y = ys.index(space.value[1])

    # offset because lines 'F' to 'I' don't start with '1'
    if x <= 3:
        y -= 4 - x

    return x, y


def space_to_marble(space: Space, board) -> Marble:
    x,y = space_to_board_indices(space)
    return board[x][y]


def marble_of_player(player: Player) -> Marble:
    """Returns the corresponding `abalone.enums.Marble` for a given `abalone.enums.Player`.

    Args:
        player: The `abalone.enums.Player` whose `abalone.enums.Marble` is wanted.

    Returns:
        The `abalone.enums.Marble` which belongs to `player`.
    """

    return Marble.WHITE if player is Player.WHITE else Marble.BLACK


def get_winner(score: Tuple[int, int]) -> Union[Player, None]:
    """Returns the winner of the game based on the current score.

    Args:
        score: The score tuple returned by `abalone.game.Game.get_score`

    Returns:
        Either the `abalone.enums.Player` who won the game or `None` if no one has won yet.
    """
    if 8 in score:
        return Player.WHITE if score[0] == 8 else Player.BLACK
    return None


def line_from_to(from_space: Space, to_space: Space) -> Union[Tuple[List[Space], Direction], Tuple[None, None]]:
    """Returns all `abalone.enums.Space`s in a straight line from a given starting space to a given ending space. The\
    two bounding spaces are included. The `abalone.enums.Direction` of that line is also returned.

    Example:
        ```python
        line_from_to(Space.A1, Space.D4)
        # ([Space.A1, Space.B2, Space.C3, Space.D4], Direction.NORTH_EAST)
        ```
        ```
            I · · · · ·
           H · · · · · ·
          G · · · · · · ·
         F · · · · · · · ·
        E · · · · · · · · ·
         D · · · X · · · · 9
          C · · X · · · · 8
           B · X · · · · 7
            A X · · · · 6
               1 2 3 4 5
        ```

    Args:
        from_space: The starting `abalone.enums.Space`.
        to_space: The ending `abalone.enums.Space`.

    Returns:
        A tuple containing a list of `abalone.enums.Space`s and a `abalone.enums.Direction` or `(None, None)` in case\
        no line with the given arguments is possible. The latter is also the case if the starting and ending spaces are\
        identical.

    Raises:
        Exception: Spaces must not be `abalone.enums.Space.OFF`
    """
    if from_space is Space.OFF or to_space is Space.OFF:
        raise Exception('Spaces must not be `Space.OFF`')
    for direction in Direction:
        line = [from_space]
        while line[-1] is not Space.OFF:
            next_space = Utils.neighbor(line[-1], direction)
            line.append(next_space)
            if next_space is to_space:
                return line, direction
    return None, None


def line_to_edge(from_space: Space, direction: Direction) -> List[Space]:
    """Returns a straight line of `abalone.enums.Space`s, from a given starting space in a given\
    `abalone.enums.Direction`. The line extends to the edge of the board. The starting space is included.

    Example:
        ```python
        utils.line_to_edge(Space.C4, Direction.SOUTH_EAST)
        # [Space.C4, Space.B4, Space.A4]
        ```
        ```
            I · · · · ·
           H · · · · · ·
          G · · · · · · ·
         F · · · · · · · ·
        E · · · · · · · · ·
         D · · · · · · · · 9
          C · · · X · · · 8
           B · · · X · · 7
            A · · · X · 6
               1 2 3 4 5
        ```

    Args:
        from_space: The starting `abalone.enums.Space`.
        direction: The `abalone.enums.Direction` of the line.

    Returns:
        A list of `abalone.enums.Space`s starting with `from_space`.

    Raises:
        Exception: `from_space` must not be `abalone.enums.Space.OFF`
    """
    if from_space is Space.OFF:
        raise Exception('`from_space` must not be `Space.OFF`')
    line = [from_space]
    while line[-1] is not Space.OFF:
        line.append(Utils.neighbor(line[-1], direction))
    line.pop()  # remove Space.OFF
    return line


def _neighbor(space: Space, direction: Direction) -> Space:
    """Returns the neighboring `abalone.enums.Space` of a given space in a given `abalone.enums.Direction`.

    Example:
        ```python
        utils.neighbor(Space.B2, Direction.EAST)
        # Space.B3
        ```
        ```
            I · · · · ·
           H · · · · · ·
          G · · · · · · ·
         F · · · · · · · ·
        E · · · · · · · · ·
         D · · · · · · · · 9
          C · · · · · · · 8
           B · X N · · · 7
            A · · · · · 6
               1 2 3 4 5
        ```

    Args:
        space: The `abalone.enums.Space` of which the neighbour is returned.
        direction: The `abalone.enums.Direction` in which the neighbour is located.

    Returns:
        The neighboring `abalone.enums.Space` of `space` in `direction`. If `space` is `abalone.enums.Space.OFF`, for\
        any given `direction`, `abalone.enums.Space.OFF` is returned.
    """

    if space is Space.OFF:
        return Space.OFF

    xs = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    ys = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

    xi = xs.index(space.value[0])
    yi = ys.index(space.value[1])

    if direction is Direction.NORTH_EAST:
        xi += 1
        yi += 1
    elif direction is Direction.EAST:
        yi += 1
    elif direction is Direction.SOUTH_EAST:
        xi -= 1
    elif direction is Direction.SOUTH_WEST:
        xi -= 1
        yi -= 1
    elif direction is Direction.WEST:
        yi -= 1
    elif direction is Direction.NORTH_WEST:
        xi += 1

    if xi < 0 or xi >= len(xs) or yi < 0 or yi >= len(ys) or xs[xi] + ys[yi] not in Space.__members__:
        return Space.OFF

    return Space[xs[xi] + ys[yi]]

def distance(space1: Space, space2: Space):
    chars1 = space1.name
    chars2 = space2.name

    ords1 = (ord(chars1[0]), ord(chars1[1]))
    ords2 = (ord(chars2[0]), ord(chars2[1]))

    if ords1[0]==ords2[0]:
        return abs(ords1[1] - ords2[1])

    if ords1[1]==ords2[1]:
        return abs(ords1[0] - ords2[0])

    if (ords1[0] - ords2[0])==(ords1[1] - ords2[1]):
        return abs(ords1[0] - ords2[0])

    top, bottom = (chars1, chars2) if ords1[0] > ords2[0] else (chars2, chars1)
    ords_top = (ord(top[0]), ord(top[1]))
    ords_bottom = (ord(bottom[0]), ord(bottom[1]))

    if top[1] < bottom[1]:
        space_tmp = Space[top[0] + bottom[1]]
    else:
        space_tmp = Space[top[0] + str(int(bottom[1]) + ords_top[0]-ords_bottom[0])]
        
    return distance(space1, space_tmp) + distance(space_tmp, space2)


def distance_from_center(space: Space):
    return distance(space, Space.E5)


def center_of_gravity(spaces: List[Space]):
    center_x = []
    center_y = []
    
    for space in spaces:
        v = space.value
        x = ord(v[0])
        y = ord(v[1])
        center_x.append(x)
        center_y.append(y)

    center_x = np.asarray(center_x)
    center_y = np.asarray(center_y)

    center_x = np.average(center_x)
    center_y = np.average(center_y)

    return center_x, center_y
    
        


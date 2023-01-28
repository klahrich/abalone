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

"""This module serves the representation of game states and the performing of game moves."""

from __future__ import annotations
from copy import deepcopy
from dis import dis
from typing import Generator, List, Tuple, Union, Dict

import colorama
from colorama import Style

from abalone.enums import Direction, InitialPosition, Marble, Player, Space
from abalone.utils import (distance, line_from_to, 
                           line_to_edge, 
                           get_winner, 
                           distance_from_center, 
                           center_of_gravity,
                           space_to_board_indices,
                           marble_of_player)

from easyAI import Human_Player, TwoPlayerGame
from abalone.utils import Utils

from pathlib import Path
import pickle

colorama.init(autoreset=True)




class IllegalMoveException(Exception):
    """Exception that is raised if a player tries to perform an illegal move."""


class Move:

    def __init__(self):
        self.cache: List(Tuple[Space, Marble]) = []
        self.board_hash = 0

    def save_state(self, game: Game, space: Space):
        self.cache.append((space, game.get_marble(space)))

    def undo(self, game):
        for space, marble in self.cache:
            game.set_marble(space, marble)
        game.board_hash = self.board_hash

    def apply(self, game: Game):
        self.board_hash = game.board_hash
        self._apply(game)
        game.board_hash = hash(tuple(tuple(l) for l in game.board))

    def _apply(self, game: Game):
        pass


class MoveInline(Move):

    def __init__(self, caboose: Space, direction: Direction):
        super().__init__()
        self.caboose = caboose
        self.direction = direction

    def __str__(self):
        return str(self.caboose) + ' ' + str(self.direction)

    def _apply(self, game: Game):

        if game.get_marble(self.caboose) is not marble_of_player(game.turn):
            raise IllegalMoveException('Only own marbles may be moved')

        line = line_to_edge(self.caboose, self.direction)
        own_marbles_num, opp_marbles_num = game.inline_marbles_nums(line)

        if own_marbles_num > 3:
            raise IllegalMoveException('Only lines of up to three marbles may be moved')

        if own_marbles_num == len(line):
            raise IllegalMoveException('Own marbles must not be moved off the board')

        # sumito
        if opp_marbles_num > 0:
            if opp_marbles_num >= own_marbles_num:
                raise IllegalMoveException('Only lines that are shorter than the player\'s line can be pushed')
            push_to = Utils.neighbor(line[own_marbles_num + opp_marbles_num - 1], self.direction)
            if push_to is not Space.OFF:
                if game.get_marble(push_to) is marble_of_player(game.turn):
                    raise IllegalMoveException('Marbles must be pushed to an empty space or off the board')
                self.save_state(game, push_to)
                game.set_marble(push_to, marble_of_player(game.not_in_turn_player()))

        self.save_state(game, line[own_marbles_num])
        game.set_marble(line[own_marbles_num], marble_of_player(game.turn))

        self.save_state(game, self.caboose)
        game.set_marble(self.caboose, Marble.BLANK)


class MoveBroadside(Move):

    def __init__(self, boundaries: Tuple[Space, Space], direction: Direction):
        super().__init__()
        self.boundaries = boundaries
        self.direction = direction

    def __str__(self):
        return str(self.boundaries) + ' ' + str(self.direction)

    def _apply(self, game: Game):
        if self.boundaries[0] is Space.OFF or self.boundaries[1] is Space.OFF:
            raise IllegalMoveException('Elements of boundaries must not be `Space.OFF`')
        marbles, direction1 = line_from_to(self.boundaries[0], self.boundaries[1])
        if marbles is None or not (len(marbles) == 2 or len(marbles) == 3):
            raise IllegalMoveException('Only two or three neighboring marbles may be moved with a broadside move')
        _, direction2 = line_from_to(self.boundaries[1], self.boundaries[0])
        if self.direction is direction1 or self.direction is direction2:
            raise IllegalMoveException('The direction of a broadside move must be sideways')
        for marble in marbles:
            if game.get_marble(marble) is not marble_of_player(game.turn):
                raise IllegalMoveException('Only own marbles may be moved')
            destination_space = Utils.neighbor(marble, self.direction)
            if destination_space is Space.OFF or game.get_marble(destination_space) is not Marble.BLANK:
                raise IllegalMoveException('With a broadside move, marbles can only be moved to empty spaces')
        for marble in marbles:
            self.save_state(game, marble)
            game.set_marble(marble, Marble.BLANK)

            neighbor_tmp = Utils.neighbor(marble, self.direction)
            self.save_state(game, neighbor_tmp)
            game.set_marble(neighbor_tmp, marble_of_player(game.turn))



def create_move(marbles: Space|Tuple[Space, Space], direction: Direction) -> Move:
    if isinstance(marbles, Space):
        return MoveInline(marbles, direction)
    elif isinstance(marbles, tuple) and isinstance(marbles[0], Space) and isinstance(marbles[1], Space):
        return MoveBroadside(marbles, direction)
    else:  # pragma: no cover
        # This exception should only be raised if the arguments are not passed according to the type hints. It is
        # only there to prevent a silent failure in such a case.
        raise Exception('Invalid arguments')


class Game(TwoPlayerGame):
    """Represents the mutable state of an Abalone game."""

    def __init__(self, 
                 player1,
                 player2,
                 heuristic_weights,
                 initial_position: InitialPosition = InitialPosition.DEFAULT, 
                 first_turn: Player = Player.BLACK):
        self.board = deepcopy(initial_position.value)
        self.turn = first_turn
    
        self.players = [player1, player2]
        self.nplayer = 1
        self.current_player = 1
        self.heuristic_weights = heuristic_weights
        self.heuristic_table: Dict[int, float] = {}
        if Path('heuristic_table.pkl').is_file():
            with open('heuristic_table.pkl', 'rb') as f:
                self.heuristic_table = pickle.load(f)

        self.board_hash = hash(tuple(tuple(l) for l in self.board))

    def __str__(self) -> str:  # pragma: no cover
        board_lines = list(map(lambda line: ' '.join(map(str, line)), self.board))
        string = ''
        string += Style.DIM + '    I ' + Style.NORMAL + board_lines[0] + '\n'
        string += Style.DIM + '   H ' + Style.NORMAL + board_lines[1] + '\n'
        string += Style.DIM + '  G ' + Style.NORMAL + board_lines[2] + '\n'
        string += Style.DIM + ' F ' + Style.NORMAL + board_lines[3] + '\n'
        string += Style.DIM + 'E ' + Style.NORMAL + board_lines[4] + '\n'
        string += Style.DIM + ' D ' + Style.NORMAL + board_lines[5] + Style.DIM + ' 9\n' + Style.NORMAL
        string += Style.DIM + '  C ' + Style.NORMAL + board_lines[6] + Style.DIM + ' 8\n' + Style.NORMAL
        string += Style.DIM + '   B ' + Style.NORMAL + board_lines[7] + Style.DIM + ' 7\n' + Style.NORMAL
        string += Style.DIM + '    A ' + Style.NORMAL + board_lines[8] + Style.DIM + ' 6\n' + Style.NORMAL
        string += Style.DIM + '       1 2 3 4 5' + Style.NORMAL
        return string

    def ttentry(self):
        return self.board_hash

    def save_heuristic_table(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.heuristic_table, f)

    def not_in_turn_player(self) -> Player:
        """Gets the `abalone.enums.Player` who is currently *not* in turn. Returns `abalone.enums.Player.WHITE` when\
        `abalone.enums.Player.BLACK` is in turn and vice versa. This player is commonly referred to as "opponent" in\
        other places.

        Returns:
            The `abalone.enums.Player` not in turn.
        """

        return Player.BLACK if self.turn is Player.WHITE else Player.WHITE

    def is_player_turn(self, marble: Marble) -> bool:
        return ((marble is Marble.BLACK and self.turn is Player.BLACK) or 
                (marble is Marble.WHITE and self.turn is Player.WHITE))

    def switch_player(self) -> None:
        """Switches the player whose turn it is."""
        super().switch_player()
        self.turn = self.not_in_turn_player()

    def set_marble(self, space: Space, marble: Marble) -> None:
        """Updates the state of a `abalone.enums.Space` on the board.

        Args:
            space: The `abalone.enums.Space` to be updated.
            marble: The new state of `space` of type `abalone.enums.Marble`

        Raises:
            Exception: Cannot set state of `abalone.enums.Space.OFF`
        """

        if space is Space.OFF:
            raise Exception('Cannot set state of `Space.OFF`')

        x, y = space_to_board_indices(space)
        self.board[x][y] = marble

    def get_marble(self, space: Space) -> Marble:
        """Returns the state of a `abalone.enums.Space`.

        Args:
            space: The `abalone.enums.Space` of which the state is to be returned.

        Returns:
            A `abalone.enums.Marble` representing the current state of `space`.

        Raises:
            Exception: Cannot get state of `abalone.enums.Space.OFF`
        """

        if space is Space.OFF:
            raise Exception('Cannot get state of `Space.OFF`')

        x, y = space_to_board_indices(space)

        return self.board[x][y]

    def get_score(self) -> Tuple[int, int]:
        """Counts how many marbles the players still have on the board.

        Returns:
            A tuple with the number of marbles of black and white, in that order.
        """
        black = 0
        white = 0
        for row in self.board:
            for space in row:
                if space is Marble.BLACK:
                    black += 1
                elif space is Marble.WHITE:
                    white += 1
        return black, white

    def inline_marbles_nums(self, line: List[Space]) -> Tuple[int, int]:
        """Counts the number of own and enemy marbles that are in the given line. First the directly adjacent marbles\
        of the player whose turn it is are counted and then the subsequent directly adjacent marbles of the opponent.\
        Therefore only the marbles that are relevant for an inline move are counted. This method serves as an\
        helper method for `abalone.game.Game.move_inline`.

        Args:
            line: A list of `abalone.enums.Space`s that are in a straight line.

        Returns:
            A tuple with the number of 1. own marbles and 2. opponent marbles, according to the counting method\
            described above.
        """
        own_marbles_num = 0
        while own_marbles_num < len(line) and self.get_marble(line[own_marbles_num]) is marble_of_player(self.turn):
            own_marbles_num += 1
        opp_marbles_num = 0
        while opp_marbles_num + own_marbles_num < len(line) and self.get_marble(
                line[opp_marbles_num + own_marbles_num]) is marble_of_player(self.not_in_turn_player()):
            opp_marbles_num += 1
        return own_marbles_num, opp_marbles_num

    def is_illegal_move_inline(self, caboose: Space, direction: Direction):
        if self.get_marble(caboose) is not marble_of_player(self.turn):
            return True

        line = line_to_edge(caboose, direction)
        own_marbles_num, opp_marbles_num = self.inline_marbles_nums(line)

        if own_marbles_num > 3:
            return True

        if own_marbles_num == len(line):
            return True

        if opp_marbles_num > 0:
            if opp_marbles_num >= own_marbles_num:
                return True
            push_to = Utils.neighbor(line[own_marbles_num + opp_marbles_num - 1], direction)
            if push_to is not Space.OFF:
                if self.get_marble(push_to) is marble_of_player(self.turn):
                    return True

        return False

    # def move_inline(self, caboose: Space, direction: Direction) -> None:
    #     """Performs an inline move. An inline move is denoted by the trailing marble ("caboose") of a straight line of\
    #     marbles. Marbles of the opponent can only be pushed with an inline move (as opposed to a broadside move). This\
    #     is possible if the opponent's marbles are directly in front of the line of the player's own marbles, and only\
    #     if the opponent's marbles are outnumbered ("sumito") and are moved to an empty space or off the board.

    #     Args:
    #         caboose: The `abalone.enums.Space` of the trailing marble of a straight line of up to three marbles.
    #         direction: The `abalone.enums.Direction` of movement.

    #     Raises:
    #         IllegalMoveException: Only own marbles may be moved
    #         IllegalMoveException: Only lines of up to three marbles may be moved
    #         IllegalMoveException: Own marbles must not be moved off the board
    #         IllegalMoveException: Only lines that are shorter than the player's line can be pushed
    #         IllegalMoveException: Marbles must be pushed to an empty space or off the board
    #     """

    #     if self.get_marble(caboose) is not marble_of_player(self.turn):
    #         raise IllegalMoveException('Only own marbles may be moved')

    #     line = line_to_edge(caboose, direction)
    #     own_marbles_num, opp_marbles_num = self.inline_marbles_nums(line)

    #     if own_marbles_num > 3:
    #         raise IllegalMoveException('Only lines of up to three marbles may be moved')

    #     if own_marbles_num == len(line):
    #         raise IllegalMoveException('Own marbles must not be moved off the board')

    #     # sumito
    #     if opp_marbles_num > 0:
    #         if opp_marbles_num >= own_marbles_num:
    #             raise IllegalMoveException('Only lines that are shorter than the player\'s line can be pushed')
    #         push_to = neighbor(line[own_marbles_num + opp_marbles_num - 1], direction)
    #         if push_to is not Space.OFF:
    #             if self.get_marble(push_to) is marble_of_player(self.turn):
    #                 raise IllegalMoveException('Marbles must be pushed to an empty space or off the board')
    #             self.set_marble(push_to, marble_of_player(self.not_in_turn_player()))

    #     self.set_marble(line[own_marbles_num], marble_of_player(self.turn))

    #     self.set_marble(caboose, Marble.BLANK)

    def is_illegal_move_broadside(self, boundaries: Tuple[Space, Space], direction: Direction):
        if boundaries[0] is Space.OFF or boundaries[1] is Space.OFF:
            return True

        marbles, direction1 = line_from_to(boundaries[0], boundaries[1])
        if marbles is None or not (len(marbles) == 2 or len(marbles) == 3):
            return True

        _, direction2 = line_from_to(boundaries[1], boundaries[0])
        if direction is direction1 or direction is direction2:
            return True

        for marble in marbles:
            if self.get_marble(marble) is not marble_of_player(self.turn):
                return True
            destination_space = Utils.neighbor(marble, direction)
            if destination_space is Space.OFF or self.get_marble(destination_space) is not Marble.BLANK:
                return True

        return False

    # def move_broadside(self, boundaries: Tuple[Space, Space], direction: Direction) -> None:
    #     """Performs a broadside move. With a broadside move a line of adjacent marbles is moved sideways into empty\
    #     spaces. However, it is not possible to push the opponent's marbles. A broadside move is denoted by the two\
    #     outermost `abalone.enums.Space`s of the line to be moved and the `abalone.enums.Direction` of movement. With a\
    #     broadside move two or three marbles can be moved, i.e. the two boundary marbles are either direct neighbors or\
    #     there is exactly one marble in between.

    #     Args:
    #         boundaries: A tuple of the two outermost `abalone.enums.Space`s of a line of two or three marbles.
    #         direction: The `abalone.enums.Direction` of movement.

    #     Raises:
    #         IllegalMoveException: Elements of boundaries must not be `abalone.enums.Space.OFF`
    #         IllegalMoveException: Only two or three neighboring marbles may be moved with a broadside move
    #         IllegalMoveException: The direction of a broadside move must be sideways
    #         IllegalMoveException: Only own marbles may be moved
    #         IllegalMoveException: With a broadside move, marbles can only be moved to empty spaces
    #     """
    #     if boundaries[0] is Space.OFF or boundaries[1] is Space.OFF:
    #         raise IllegalMoveException('Elements of boundaries must not be `Space.OFF`')
    #     marbles, direction1 = line_from_to(boundaries[0], boundaries[1])
    #     if marbles is None or not (len(marbles) == 2 or len(marbles) == 3):
    #         raise IllegalMoveException('Only two or three neighboring marbles may be moved with a broadside move')
    #     _, direction2 = line_from_to(boundaries[1], boundaries[0])
    #     if direction is direction1 or direction is direction2:
    #         raise IllegalMoveException('The direction of a broadside move must be sideways')
    #     for marble in marbles:
    #         if self.get_marble(marble) is not _marble_of_player(self.turn):
    #             raise IllegalMoveException('Only own marbles may be moved')
    #         destination_space = neighbor(marble, direction)
    #         if destination_space is Space.OFF or self.get_marble(destination_space) is not Marble.BLANK:
    #             raise IllegalMoveException('With a broadside move, marbles can only be moved to empty spaces')
    #     for marble in marbles:
    #         self.set_marble(marble, Marble.BLANK)
    #         neighbor_tmp = neighbor(marble, direction)
    #         self.set_marble(neighbor_tmp, marble_of_player(self.turn))

    def is_illegal_move(self, marbles: Union[Space, Tuple[Space, Space]], direction: Direction):
        if isinstance(marbles, Space):
            return self.is_illegal_move_inline(marbles, direction)
        elif isinstance(marbles, tuple) and isinstance(marbles[0], Space) and isinstance(marbles[1], Space):
            return self.is_illegal_move_broadside(marbles, direction)
        else:
            raise Exception('Invalid arguments')

    # def move(self, marbles: Union[Space, Tuple[Space, Space]], direction: Direction) -> None:
    #     """Performs either an inline or a broadside move, depending on the arguments passed, by calling the according\
    #     method (`abalone.game.Game.move_inline` or `abalone.game.Game.move_broadside`).

    #     Args:
    #         marbles: The `abalone.enums.Space`s with the marbles to be moved. Either a single space for an inline move\
    #             or a tuple of two spaces for a broadside move, in accordance with the parameters of\
    #             `abalone.game.Game.move_inline` resp. `abalone.game.Game.move_broadside`.
    #         direction: The `abalone.enums.Direction` of movement.

    #     Raises:
    #         Exception: Invalid arguments
    #     """
    #     if isinstance(marbles, Space):
    #         self.move_inline(marbles, direction)
    #     elif isinstance(marbles, tuple) and isinstance(marbles[0], Space) and isinstance(marbles[1], Space):
    #         self.move_broadside(marbles, direction)
    #     else:  # pragma: no cover
    #         # This exception should only be raised if the arguments are not passed according to the type hints. It is
    #         # only there to prevent a silent failure in such a case.
    #         raise Exception('Invalid arguments')

    def generate_marble_lines(self, player) -> Generator[Union[Space, Tuple[Space, Space]], None, None]:
        """Generates all adjacent straight lines with up to three marbles of the player whose turn it is.

        Yields:
            Either one or two `abalone.enums.Space`s according to the first parameter of `abalone.game.Game.move`.
        """
        for space in Space:
            if space is Space.OFF or self.get_marble(space) is not marble_of_player(player):
                continue
            yield space
            for direction in [Direction.NORTH_WEST, Direction.NORTH_EAST, Direction.EAST]:
                neighbor1 = Utils.neighbor(space, direction)
                if neighbor1 is not Space.OFF and self.get_marble(neighbor1) is marble_of_player(player):
                    yield space, neighbor1
                    neighbor2 = Utils.neighbor(neighbor1, direction)
                    if neighbor2 is not Space.OFF and self.get_marble(neighbor2) is marble_of_player(player):
                        yield space, neighbor2

    def generate_own_marble_lines(self):
        self.generate_marble_lines(self.turn)

    def generate_legal_moves(self) -> Generator[Move, None, None]:
        """Generates all possible moves that the player whose turn it is can perform. The yielded values are intended\
        to be passed as arguments to `abalone.game.Game.move`.

        Yields:
            A tuple of 1. either one or a tuple of two `abalone.enums.Space`s and 2. a `abalone.enums.Direction`
        """
        for marbles in self.generate_own_marble_lines():
            for direction in Direction:
                if not self.is_illegal_move(marbles, direction):
                    yield create_move(marbles, direction)
                # copy = deepcopy(self)
                # try:
                #     copy.move(marbles, direction)
                # except IllegalMoveException:
                #     continue
                # yield marbles, direction, copy

    def possible_moves(self) -> List[Move]:
        return list(self.generate_legal_moves())

    def make_move(self, move: Move|Tuple[Space | Tuple[Space,Space], Direction]):
        if isinstance(move, Move):
            move.apply(self)
        else:
            move = create_move(move[0], move[1])
            move.apply(self)

    def unmake_move(self, move: Move):
        move.undo(self)

    def is_over(self):
        return get_winner(self.get_score()) is not None

    def scoring(self):
        score = self.get_score()
        score_raw = (score[0] - score[1])*150
        
        if self.board_hash in self.heuristic_table:
            score_adjusted = score_raw + self.heuristic_table[self.board_hash]
        else:
            h_score = self.heuristic_score()
            score_adjusted = score_raw + h_score
            self.heuristic_table[self.board_hash] = h_score

        return score_adjusted

    def count_neighbors(self, space: Space) -> Tuple[int, int]:
        count_f = 0
        count_a = 0
        marble = self.get_marble(space)
        for d in Direction:
            neighbor_space = Utils.neighbor(space, d)
            try:
                neighbor_marble = self.get_marble(neighbor_space)
                if (neighbor_marble is not Marble.BLANK) and (neighbor_marble is marble):
                    count_f += 1
                elif (neighbor_marble is not Marble.BLANK) and (neighbor_marble is not marble):
                    count_a += 1
            except:
                continue
        return count_f, count_a

    def _is_isolated(self, space: Space):
        neighbors_f, neighbors_a = self.count_neighbors(space)
        return neighbors_f == 0 and neighbors_a >= 1

    def _count_isolated(self, player):
        count_isolated = 0
   
        for space in [s for s in Space if (s is not Space.OFF) 
                        and (self.get_marble(s) is marble_of_player(player))]:
            if self._is_isolated(space):
                count_isolated += 1

        return count_isolated

    def _count_threes(self, player):
        lines = self.generate_marble_lines(player)
        count_threes = 0
        for t in lines:
            if isinstance(t, tuple) and len(t)==2 and distance(t[0], t[1])==2:
                count_threes += 1

        return count_threes

    def _distance_center(self, player):
        total_marbles = 0
        distance_center = 0

        for space in [s for s in Space if (s is not Space.OFF) 
                        and (self.get_marble(s) is marble_of_player(player))]:

            total_marbles += 1
            distance_center += distance_from_center(space)
        
        distance_center /= total_marbles
        return distance_center

    def _heuristic_score(self, player):
        total_marbles = 0
        distance_center = 0
        count_isolated = 0
   
        for space in [s for s in Space if (s is not Space.OFF) 
                        and (self.get_marble(s) is marble_of_player(player))]:

            lines = self.generate_marble_lines(player)
            count_threes = 0
            for t in lines:
                if isinstance(t, tuple) and len(t)==2 and distance(t[0], t[1])==2:
                    count_threes += 1

            if self._is_isolated(space):
                count_isolated += 1

            total_marbles += 1
            distance_center += distance_from_center(space)
            
        distance_center /= total_marbles

        return  (count_threes * self.heuristic_weights['count_threes']
                    - count_isolated * self.heuristic_weights['count_isolated'] 
                    - distance_center * self.heuristic_weights['distance_center'])

    def heuristic_score(self):
        return self._heuristic_score(Player.BLACK) - self._heuristic_score(Player.WHITE)


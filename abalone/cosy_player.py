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

"""This module is an example implementation for a player that performs random moves."""
from random import choice
from typing import List, Tuple, Union

from abalone.abstract_player import AbstractPlayer
from abalone.enums import Space, Direction, Marble
from abalone.game import Game
from abalone.utils import distance_from_center, center_of_gravity


class CosyPlayer(AbstractPlayer):

    def __init__(self, anti_marbles_weight=5, distance_center_weight=1, anti_distance_center_weight=1,
                total_neighbors_weight=1, total_anti_neighbors_weight=1, distance_to_enemy_weight=1):
        super().__init__()
        self.anti_marbles_weight = anti_marbles_weight
        self.distance_center_weight = distance_center_weight
        self.anti_distance_center_weight = anti_distance_center_weight
        self.total_neighbors_weight = total_neighbors_weight
        self.total_anti_neighbors_weight = total_anti_neighbors_weight
        self.distance_to_enemy_weight = distance_to_enemy_weight


    def turn(self, game: Game) \
            -> Tuple[Union[Space, Tuple[Space, Space]], Direction]:

        possible_moves = list(game.generate_legal_moves())

        best_move = None
        best_score = -999999
        best_total_neighbors = None
        best_total_anti_neighbors = None
        best_total_anti_marbles = None
        best_distance_center = None
        best_anti_distance_center = None

        for move in possible_moves:
            total_neighbors = 0
            total_anti_neighbors = 0
            total_marbles = 0
            total_anti_marbles = 0
            distance_center = 0
            anti_distance_center = 0
            friendly_spaces = []
            anti_spaces = []
            marbles, direction, game = move
            for space in [s for s in Space if (s is not Space.OFF) and (game.get_marble(s) is not Marble.BLANK)]:
                f_neighbors = game.count_friendly_neighbors(space)
                if game.is_player_turn(game.get_marble(space)):
                    friendly_spaces.append(space)
                    total_neighbors += f_neighbors
                    total_marbles += 1
                    distance_center += distance_from_center(space)
                else:
                    anti_spaces.append(space)
                    total_anti_neighbors += f_neighbors
                    total_anti_marbles += 1
                    anti_distance_center += distance_from_center(space)
            distance_center /= total_marbles
            anti_distance_center /= total_anti_marbles
            cg_x, cg_y = center_of_gravity(friendly_spaces)
            anti_cg_x, anti_cg_y = center_of_gravity(anti_spaces)
            distance_to_enemy = abs(cg_x - anti_cg_x) + abs(cg_y - anti_cg_y)
            score = (total_neighbors * self.total_neighbors_weight
                        - total_anti_neighbors * self.total_anti_neighbors_weight
                        - total_anti_marbles * self.anti_marbles_weight
                        - distance_center * self.distance_center_weight
                        + anti_distance_center * self.anti_distance_center_weight
                        - distance_to_enemy * self.distance_to_enemy_weight)
            if score > best_score:    
                best_move = move
                best_marbles = marbles
                best_direction = direction
                best_score = score
                best_total_neighbors = total_neighbors
                best_total_anti_neighbors = total_anti_neighbors
                best_total_anti_marbles = total_anti_marbles
                best_distance_center = distance_center
                best_anti_distance_center = anti_distance_center
                best_distance_to_enemy = distance_to_enemy

        print(f'best_total_neighbors: {best_total_neighbors}', 
              f'best_total_anti_neighbors: {best_total_anti_neighbors}', 
              f'best_total_anti_marbles: {best_total_anti_marbles}', 
              f'best_distance_center: {best_distance_center}', 
              f'best_anti_distance_center: {best_anti_distance_center}',
              f'distance_to_enemy: {distance_to_enemy}')

        return best_marbles, best_direction

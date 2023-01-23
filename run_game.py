#!/usr/bin/env python
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

"""This module runs a `abalone.game.Game`."""

from traceback import format_exc
from typing import Generator, List, Tuple, Union

from abalone.abstract_player import AbstractPlayer
from abalone.enums import Direction, Player, Space
from abalone.game import Game, IllegalMoveException
from abalone.utils import line_from_to, get_winner
import random
from abalone.cosy_player import CosyPlayer


def _format_move(turn: Player, move: Tuple[Union[Space, Tuple[Space, Space]], Direction], moves: int) -> str:
    """Formats a player's move as a string with a single line.

    Args:
        turn: The `Player` who performs the move
        move: The move as returned by `abalone.abstract_player.AbstractPlayer.turn`
        moves: The number of total moves made so far (not including this move)
    """
    marbles = [move[0]] if isinstance(move[0], Space) else line_from_to(*move[0])[0]
    marbles = map(lambda space: space.name, marbles)
    return f'{moves + 1}: {turn.name} moves {", ".join(marbles)} in direction {move[1].name}'


def run_game(black: AbstractPlayer, white: AbstractPlayer, **kwargs) \
        -> Generator[Tuple[Game, List[Tuple[Union[Space, Tuple[Space, Space]], Direction]]], None, None]:
    """Runs a game instance and prints the progress / current state at every turn.

    Args:
        black: An `abalone.abstract_player.AbstractPlayer`
        white: An `abalone.abstract_player.AbstractPlayer`
        **kwargs: These arguments are passed to `abalone.game.Game.__init__`

    Yields:
        A tuple of the current `abalone.game.Game` instance and the move history at the start of the game and after\
        every legal turn.
    """
    game = Game()
    moves_history = []
    #yield game, moves_history

    i = 0
    prev_score = (14, 14)
    while True:
        score = game.get_score()
        score_str = f'BLACK {score[0]} - WHITE {score[1]}'
        if score != prev_score:
            print(score_str)
            prev_score = score
        #print(score_str, game, '', sep='\n')

        winner = get_winner(score)
        if winner is not None:
            print(f'{winner.name} won!')
            break

        try:
            move = black.turn(game, moves_history) if game.turn is Player.BLACK else white.turn(game, moves_history)
            #print(_format_move(game.turn, move, len(moves_history)), end='\n\n')

            game.move(*move)
            game.switch_player()
            moves_history.append(move)

            i += 1

            if i > 100 and score==(14,14):
                print('No progress after 100 moves')
                print(score_str)
                break

            if i > 500:
                print('No winner after 500 moves')
                print(score_str)
                break

            #yield game, moves_history
        except IllegalMoveException as ex:
            print(f'{game.turn.name}\'s tried to perform an illegal move ({ex})\n')
            break
        except:
            print(f'{game.turn.name}\'s move caused an exception\n')
            print(format_exc())
            break
    return winner, score


if __name__ == '__main__':  # pragma: no cover
    # Run a game from the command line with default configuration.
    import importlib
    import sys

    # if len(sys.argv) != 3:
    #     sys.exit(1)
    # black = sys.argv[1].rsplit('.', 1)
    # black = getattr(importlib.import_module(black[0]), black[1])
    # white = sys.argv[2].rsplit('.', 1)
    # white = getattr(importlib.import_module(white[0]), white[1])
    
    anti_marbles_weight=random.uniform(0.1, 10)
    distance_center_weight=random.uniform(0.1, 10)
    anti_distance_center_weight=random.uniform(0.1, 10)
    total_neighbors_weight=random.uniform(0.1, 10)
    total_anti_neighbors_weight=random.uniform(0.1, 10)
    distance_to_enemy_weight=random.uniform(0.1, 10)

    black_config = {'anti_marbles_weight': 8.63, 
                    'distance_center_weight': 6.75, 
                    'anti_distance_center_weight': 1.48, 
                    'total_neighbors_weight': 0.56, 
                    'total_anti_neighbors_weight': 8.95, 
                    'distance_to_enemy_weight': 2.86}

    white_config = {'anti_marbles_weight': 4.17, 
                    'distance_center_weight': 2.21, 
                    'anti_distance_center_weight': 9.28, 
                    'total_neighbors_weight': 1.75, 
                    'total_anti_neighbors_weight': 9.12, 
                    'distance_to_enemy_weight': 6.25}

    # white_config = {'anti_marbles_weight': 9.79, 
    #                 'distance_center_weight': 4.48, 
    #                 'anti_distance_center_weight': 6.70, 
    #                 'total_neighbors_weight': 3.15, 
    #                 'total_anti_neighbors_weight': 7.42, 
    #                 'distance_to_enemy_weight': 4.13}

    black = CosyPlayer(black_config)
    white = CosyPlayer(white_config)

    run_game(black, white)

    # for i in range(20):
    #     print(f'Game {i}')
    #     white_config = {
    #         'anti_marbles_weight': random.uniform(0.1, 10),
    #         'distance_center_weight': random.uniform(0.1, 10),
    #         'anti_distance_center_weight': random.uniform(0.1, 10),
    #         'total_neighbors_weight': random.uniform(0.1, 10),
    #         'total_anti_neighbors_weight': random.uniform(0.1, 10),
    #         'distance_to_enemy_weight': random.uniform(0.1, 10)
    #     }

    #     print("WHITE:")
    #     print(white_config)

    #     white = CosyPlayer(white_config)

    #     winner, score = run_game(black, white)

    #     if (score != (14, 14)) and (score[1] > score[0]):
    #         print("Taking white's config")
    #         black_config = white_config
    #         black = CosyPlayer(black_config)

    # print('Winning config:')
    # print(black_config)

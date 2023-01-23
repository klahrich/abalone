import gym
from gym import spaces
import numpy as np
import string
from abalone.game import Game
from abalone.enums import Marble, Direction, Space, Player
from abalone.utils import get_winner
import itertools



def marble_to_int(marble: Marble):
    match marble:
        case Marble.BLANK:
            return 0
        case Marble.BLACK:
            return 1
        case Marble.WHITE:
            return 2

def convert_gym_direction(d: int):
    match d:
        case 0: return Direction.NE
        case 1: return Direction.E
        case 2: return Direction.SE
        case 3: return Direction.SW
        case 4: return Direction.W
        case 5: return Direction.NW
        case x: raise ValueError(f'Unsupported direction {x}: allowed values are 0-5')

def board_to_observation(board):
        rows = []

        for row in board:
            rows.append([marble_to_int(marble) for marble in row])

        return np.array(rows)


class AbaloneEnv(gym.Env):

    def __init__(self, game):
        self.game = game

        # 0 is blank, 1 is black, 2 is white
        self.observation_space = spaces.Tuple(
            (
                spaces.MultiDiscrete(np.full((5), 3)),
                spaces.MultiDiscrete(np.full((6), 3)),
                spaces.MultiDiscrete(np.full((7), 3)),
                spaces.MultiDiscrete(np.full((8), 3)),
                spaces.MultiDiscrete(np.full((9), 3)),
                spaces.MultiDiscrete(np.full((8), 3)),
                spaces.MultiDiscrete(np.full((7), 3)),
                spaces.MultiDiscrete(np.full((6), 3)),
                spaces.MultiDiscrete(np.full((5), 3))
            )
        )

        self.score = (14, 14)


    @property
    def action_space(self):
        valid_moves = list(self.game.generate_legal_moves())
        return spaces.Discrete(len(valid_moves))
        

    def reset(self, seed=None, options=None):
        self.game = Game()
        observation = self.board_to_observation(self.game.board)
        info = {}
        return observation, info

    def step(self, action):
        valid_moves = list(self.game.generate_legal_moves())
        move = valid_moves[action]
        space, direction = move[0], move[1]
        self.game.move(space, direction)

        observation = board_to_observation(self.game.board)

        score = self.game.get_score()
        winner = get_winner(score)

        reward = 0

        if winner is not None:
            reward = 10 if winner is Player.BLACK else -10
            done = True
        else:
            done = False
            if score != self.score:
                if score[0] < self.score[0]:
                    reward = -1
                elif score[1] < self.score[1]:
                    reward = +1
                self.score = score

        info = {}

        return observation, reward, done, info

    def render(self):
        print(self.game)
        score_str = f'BLACK {self.score[0]} - WHITE {self.score[1]}'
        print(score_str)
        print()

    def close(self):
        super().close()

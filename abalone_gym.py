from abalone.abalone_env import AbaloneEnv
from abalone.game import Game
from itertools import cycle

game = Game()
env1 = AbaloneEnv(game)
env2 = AbaloneEnv(game)

env1.render()

envs = cycle([env1, env2])
players = cycle(['BLACK', 'WHITE'])


for env, player in zip(envs, players):
    print(f'Player: {player}')

    action = env.action_space.sample()
    obs, reward, done, info = env.step(action)

    env.render()

    if done == True:
        break
    
    game.switch_player()
    
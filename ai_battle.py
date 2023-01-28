from easyAI.AI import SSS, Negamax
from easyAI import AI_Player
from abalone.game import Game
from abalone.random_player import RandomPlayer
from profilehooks import profile
import time
from easyAI.AI import TranspositionTable
from pathlib import Path


def main():
    weights = {
        'anti_marbles_weight': 8, 
        'distance_center_weight': 2.5, 
        'anti_distance_center_weight': 2.5, 
        'total_neighbors_weight': 5, 
        'total_anti_neighbors_weight': 5, 
        'distance_to_enemy_weight': 0.1
    }

    tt = TranspositionTable()
    if Path('tt.pkl').is_file():
        tt.from_file('tt.pkl')

    player1 = AI_Player(Negamax(3))
    player2 = AI_Player(RandomPlayer())
    game = Game(player1, player2, heuristic_weights=weights)
    print(game)

    score = game.get_score()

    while not game.is_over():
        t = time.time()
        print(f'Current player: {game.turn}')
        move = game.get_move()
        print(move)
        game.play_move(move)
        delta_t = round(time.time() - t, 2)
        print(f'Score: {game.get_score()}')
        print(f'Elapsed: {delta_t} sec')
        print(game)
        if game.get_score() != score:
            score = game.get_score()
            r = input('Press any key to continue or q to exit: ')
            if r.lower() == 'q':
                break

    print('Final score: ', game.get_score())
    tt.to_file('tt.pkl')
    game.save_heuristic_table('heuristic_table.pkl')


if __name__ == '__main__':
    main()
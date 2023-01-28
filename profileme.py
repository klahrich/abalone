from easyAI.AI import SSS, Negamax
from easyAI import AI_Player
from abalone.game import Game
from profilehooks import profile

weights = {
            'anti_marbles_weight': 8, 
            'distance_center_weight': 2.5, 
            'anti_distance_center_weight': 2.5, 
            'total_neighbors_weight': 5, 
            'total_anti_neighbors_weight': 5, 
            'distance_to_enemy_weight': 0.1
        }

ai = AI_Player(Negamax(3))
game = Game(ai, heuristic_weights=weights)

@profile(sort='time')
def one_step():
    ai.ask_move(game)

one_step()
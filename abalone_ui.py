import arcade
from abalone.enums import X_A1, Y_A1, SIZE, Space, InitialPosition, Marble, Player
from abalone.game import Game, MoveBroadside, MoveInline, marble_of_player
from typing import List, Dict, Set
from abalone.sprites import SpaceSprite, MarbleSprite, ArrowSprite
from abalone.utils import get_winner
from abalone.cosy_player import CosyPlayer
import time
import numpy as np
from easyAI import AI_Player, Human_Player, Negamax
from easyAI.AI import TranspositionTable
from pathlib import Path


class AbaloneUI(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, game: Game):

        # Call the parent class and set up the window
        super().__init__(10*SIZE + 220, 10*SIZE+100, "Abalone")
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        self.space_sprites = None
        self.marble_sprites = None
        self.arrows_sprites = None
        self.score = None
        self.winner = None
        self.game = game
        self.clicked_marble_sprites: Set[SpaceSprite] = set()
        self.move_marbles = False
        self.space_to_sprite:Dict[Space, SpaceSprite] = dict()
        self.bell_sound = arcade.load_sound("sounds/bell.wav")
        self.bell_long_sound = arcade.load_sound("sounds/bell-long.wav")
        self.previous_marble_count = 28
        self.ai_move_times: List[float] = []

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        self.space_sprites = arcade.SpriteList(use_spatial_hash=True)
        self.marble_sprites = arcade.SpriteList(use_spatial_hash=True)
        self.arrows_sprites = arcade.SpriteList(use_spatial_hash=True)
        
        _sprites = arcade.SpriteList(use_spatial_hash=True)

        spaces = [member for member in Space if member.name != "OFF"]
        
        for s in spaces:
            pos = s.value[2:4]
            spr = SpaceSprite(self, s)
            self.space_to_sprite[s] = spr
            spr.set_position(pos[0], pos[1])
            self.space_sprites.append(spr)
            marble = spr.get_marble()
            if marble in [Marble.WHITE, Marble.BLACK]:
                marble_spr = spr.add_marble_sprite(MarbleSprite(self, marble))
                self.marble_sprites.append(marble_spr)
        
        if isinstance(self.game.player, AI_Player):
            arcade.schedule(self.move_ai, 1)

    def move_ai(self, dt=0):
        self.ai_move_times.append(time.time())
        #move = self.player_ai.turn(self.game)
        move = self.game.get_move()
        self.game.play_move(move)        
        if isinstance(move, MoveInline):
            self.draw_arrows([(move.caboose, move.direction)])
        elif isinstance(move, MoveBroadside):
            self.draw_arrows([(move.boundaries[0], move.direction), (move.boundaries[1], move.direction)])
        #self.game.switch_player()
        self.move_marbles = True
        arcade.unschedule(self.move_ai)
        if len(self.ai_move_times) > 1:
            print('Average AI turn time: ', round(np.average(np.diff(self.ai_move_times)), 2), 'sec')

    def draw_arrows(self, spaces_directions):
        self.arrows_sprites.clear()
        for sd in spaces_directions:
            space = sd[0]
            direction = sd[1]
            spr = ArrowSprite(direction)
            spr.center_x = self.space_to_sprite[space].center_x
            spr.center_y = self.space_to_sprite[space].center_y
            self.arrows_sprites.append(spr)

    def on_update(self, delta_time: float):
        self.score = self.game.get_score()
        self.winner = get_winner(self.score)

        if self.move_marbles:
            self.marble_sprites = arcade.SpriteList(use_spatial_hash=True)
            marble_count = 0
            for spr in self.space_sprites:
                spr.clear_marble_sprite()
                marble = spr.get_marble()
                if marble in [Marble.WHITE, Marble.BLACK]:
                    marble_count += 1
                    marble_spr = spr.add_marble_sprite(MarbleSprite(self, marble))
                    self.marble_sprites.append(marble_spr)
            if marble_count < self.previous_marble_count:
                arcade.play_sound(self.bell_sound)
                self.previous_marble_count = marble_count
            self.move_marbles = False
            self.clicked_marble_sprites: Set[SpaceSprite] = set()
    
            if self.winner is not None:
                print(f'{self.winner.name} won!')
                arcade.play_sound(self.bell_long_sound)

            if isinstance(self.game.player, AI_Player):
                arcade.schedule(self.move_ai, 1)

    def on_mouse_press(self, x, y, button, modifiers):
        if not isinstance(self.game.player, AI_Player):
            space_sprites = arcade.get_sprites_at_point((x, y), self.space_sprites)
            for spr in space_sprites:
                m = spr.get_marble_sprite()
                if m is not None:
                    m.click()
                else:
                    spr.click()
    
    def click_marble_sprite(self, spr: MarbleSprite):
        self.clicked_marble_sprites.add(spr)

    def unclick_marble_sprite(self, spr: MarbleSprite):
        self.clicked_marble_sprites.remove(spr)   

    def on_draw(self):
        """Render the screen."""
        arcade.start_render()
        self.space_sprites.draw()
        self.marble_sprites.draw()
        self.arrows_sprites.draw()
        
        if self.winner is None:
            arcade.draw_text(f"{self.game.turn}'s turn",
                             0,
                             10*SIZE+50,
                             arcade.color.BLACK if self.game.turn is Player.BLACK else arcade.color.DARK_RED,
                             20,
                            width=10*SIZE,
                            align="center"
            )
            arcade.draw_text("Black: " + str(14-self.score[1]),
                            0,
                            10*SIZE + 25,
                            arcade.color.BLACK,
                            20,
                            width=10*SIZE/2,
                            align="center")
            arcade.draw_text("Red: " + str(14-self.score[0]),
                            10*SIZE/2,
                            10*SIZE + 25,
                            arcade.color.DARK_RED,
                            20,
                            width=10*SIZE/2,
                            align="center")
            arcade.draw_text("Black heuristic score: " + str(round(self.game._heuristic_score(Player.BLACK), 0)),
                             10*SIZE + 10,
                             10*SIZE - 25,
                             arcade.color.BLACK,
                             width=190,
                             align="left")
            arcade.draw_text("Black count threes: " + str(self.game._count_threes(Player.BLACK)),
                             10*SIZE + 10,
                             10*SIZE - 50,
                             arcade.color.BLACK,
                             width=190,
                             align="left")
            arcade.draw_text("Black count isolated: " + str(self.game._count_isolated(Player.BLACK)),
                             10*SIZE + 10,
                             10*SIZE - 75,
                             arcade.color.BLACK,
                             width=190,
                             align="left")
            arcade.draw_text("Black distance center: " + str(round(self.game._distance_center(Player.BLACK), 1)),
                             10*SIZE + 10,
                             10*SIZE - 100,
                             arcade.color.BLACK,
                             width=190,
                             align="left")
            arcade.draw_text("Red heuristic score:  " + str(round(self.game._heuristic_score(Player.WHITE), 0)),
                             10*SIZE + 10,
                             10*SIZE - 125,
                             arcade.color.DARK_RED,
                             width=190,
                             align="left")
            arcade.draw_text("Red count threes: " + str(self.game._count_threes(Player.WHITE)),
                             10*SIZE + 10,
                             10*SIZE - 150,
                             arcade.color.DARK_RED,
                             width=190,
                             align="left")
            arcade.draw_text("Red count isolated: " + str(self.game._count_isolated(Player.WHITE)),
                             10*SIZE + 10,
                             10*SIZE - 175,
                             arcade.color.DARK_RED,
                             width=190,
                             align="left")
            arcade.draw_text("Red distance center: " + str(round(self.game._distance_center(Player.WHITE), 1)),
                             10*SIZE + 10,
                             10*SIZE - 200,
                             arcade.color.DARK_RED,
                             width=190,
                             align="left")

        elif self.winner is not None:
            arcade.draw_text(f'{self.winner.name} won!',
                            0,
                            10*SIZE + 25,
                            arcade.color.BLACK if self.winner is Player.BLACK else arcade.color.DARK_RED,
                            20,
                            width=10*SIZE,
                            align="center")


def main(game: Game):
    """Main function"""
    window = AbaloneUI(game)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    # tt = TranspositionTable()
    # if Path('tt.pkl').is_file():
    #     tt.from_file('tt.pkl')

    ai = AI_Player(Negamax(2))
    weights = {
            'distance_center': 2.5, 
            'count_threes': 5,
            'count_isolated': 10
        }
    game = Game(Human_Player(), Human_Player(), weights)

    main(game)

    # tt.to_file('tt.pkl')
    # game.save_heuristic_table()



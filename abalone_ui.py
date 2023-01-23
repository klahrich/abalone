import arcade
from abalone.enums import X_A1, Y_A1, SIZE, Space, InitialPosition, Marble, Player
from abalone.game import Game, _marble_of_player, _space_to_marble, Action
from typing import List
from abalone.sprites import SpaceSprite, MarbleSprite, ArrowSprite
from abalone.utils import get_winner
from abalone.cosy_player import CosyPlayer
import time
from mcts.searcher.mcts import MCTS


class AbaloneUI(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, game: Game):

        # Call the parent class and set up the window
        super().__init__(10*SIZE, 10*SIZE+100, "Abalone")
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        self.space_sprites = None
        self.marble_sprites = None
        self.arrows_sprites = None
        self.score = None
        self.winner = None
        self.game = game
        self.clicked_marble_sprites = set()
        self.move_marbles = False
        config = {
            'anti_marbles_weight': 8.63, 
            'distance_center_weight': 6.75,
            'anti_distance_center_weight': 1.48,
            'total_neighbors_weight': 0.56,
            'total_anti_neighbors_weight': 8.95,
            'distance_to_enemy_weight': 2.86
        }
        #self.player_ai = CosyPlayer(config)
        self.player_ai = MCTS(time_limit=1000)
        self.player_ai_turn = Player.BLACK
        self.space_to_sprite = dict()
        self.bell_sound = arcade.load_sound("sounds/bell.wav")
        self.bell_long_sound = arcade.load_sound("sounds/bell-long.wav")
        self.previous_marble_count = 28

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
        
        if self.game.turn is self.player_ai_turn:
            arcade.schedule(self.move_ai, 1)

    def move_ai(self, dt=0):
        #move = self.player_ai.turn(self.game)
        action, reward = self.player_ai.search(initial_state=self.game, need_details=True)
        print(action)
        print(reward)
        move = (action.marbles, action.direction)
        self.game.move(*move)
        space, direction = move
        if isinstance(space, Space):
            self.draw_arrows([(space, direction)])
        elif isinstance(space, tuple):
            self.draw_arrows([(space[0], direction), (space[1], direction)])
        self.game.switch_player()
        self.move_marbles = True
        arcade.unschedule(self.move_ai)

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
            self.clicked_marble_sprites = set()
            self.score = self.game.get_score()
            #print('score:', self.score)
            self.winner = get_winner(self.score)
            if self.winner is not None:
                print(f'{self.winner.name} won!')
                arcade.play_sound(self.bell_long_sound)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game.turn is not self.player_ai_turn:
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
        if self.score is not None and self.winner is None:
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
    game = Game()
    main(game)



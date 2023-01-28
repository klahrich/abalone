from arcade import SpriteCircle
from abalone.enums import Direction, Space
import arcade
from abalone.enums import SIZE, Marble
from abalone.utils import line_from_to, space_to_marble, marble_of_player


class SpaceSprite(SpriteCircle):

    def __init__(self, abalone_ui, space: Space):
        super().__init__(int(SIZE/2.0), arcade.csscolor.WHITE, False)
        self.space = space
        self.abalone_ui = abalone_ui
        self.is_clicked = False
        self.marble_sprite = None
        
    def get_marble(self):
        return space_to_marble(self.space, self.abalone_ui.game.board)

    def get_marble_sprite(self):
        return self.marble_sprite

    def clear_marble_sprite(self):
        self.marble_sprite = None

    def add_marble_sprite(self, marble_sprite):
        self.marble_sprite = marble_sprite
        marble_sprite.set_space_sprite(self)
        return marble_sprite

    def remove_marble_sprite(self):
        self.marble_sprite = None

    def click(self):
        clicked_marble_sprites = list(self.abalone_ui.clicked_marble_sprites)
        if len(clicked_marble_sprites)==1:
            m = clicked_marble_sprites[0]
            spaces, direction = line_from_to(m.space_sprite.space, self.space)
            if direction is not None:
                #self.abalone_ui.game.move(m.space_sprite.space, direction)
                #self.abalone_ui.game.switch_player()
                self.abalone_ui.game.play_move((m.space_sprite.space, direction))
                self.abalone_ui.move_marbles = True
                
        elif len(clicked_marble_sprites)==2:
            m1, m2 = (clicked_marble_sprites[0], clicked_marble_sprites[1])
            spaces, direction = line_from_to(m1.space_sprite.space, self.space)
            if direction is None:
                spaces, direction = line_from_to(m2.space_sprite.space, self.space)
            if direction is not None:
                # self.abalone_ui.game.move((m1.space_sprite.space, m2.space_sprite.space), direction)
                # self.abalone_ui.game.switch_player()
                self.abalone_ui.game.play_move(((m1.space_sprite.space, m2.space_sprite.space), direction))
                self.abalone_ui.move_marbles = True
        

class MarbleSprite(SpriteCircle):

    def __init__(self, abalone_ui, marble: Marble):
        super().__init__(int(SIZE/2.0), 
                        arcade.color.BLACK if marble is Marble.BLACK else arcade.color.DARK_RED, 
                        False)
        self.abalone_ui = abalone_ui
        self.marble = marble
        self.space_sprite = None
        self.is_clicked = False

    def set_space_sprite(self, space_sprite):
        self.space_sprite = space_sprite
        self.set_position(space_sprite.position[0], space_sprite.position[1])

    def click(self):
        if self.marble is marble_of_player(self.abalone_ui.game.turn):
            self.is_clicked = not self.is_clicked
            if self.is_clicked:
                self.alpha = 150
                self.abalone_ui.click_marble_sprite(self)
            else:
                self.alpha = 255
                self.abalone_ui.unclick_marble_sprite(self)
        else:
            self.space_sprite.click()


class ArrowSprite(arcade.Sprite):

    def __init__(self, direction:Direction):
        match direction:
            case Direction.NORTH_EAST:
                super().__init__('img/arrow_up_right.png')
            case Direction.SOUTH_EAST:
                super().__init__('img/arrow_down_right.png')
            case Direction.SOUTH_WEST:
                super().__init__('img/arrow_down_left.png')
            case Direction.NORTH_WEST:
                super().__init__('img/arrow_up_left.png')
            case Direction.EAST:
                super().__init__('img/arrow_right.png')
            case Direction.WEST:
                super().__init__('img/arrow_left.png')

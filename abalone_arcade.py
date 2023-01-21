import arcade
from arcade import SpriteCircle
from abalone.enums import X_A1, Y_A1, SIZE, Space, InitialPosition, Marble
from abalone.game import _space_to_board_indices

# Open the window. Set the window title and dimensions (width and height)
arcade.open_window(10*SIZE, 10*SIZE, "Drawing Primitives Example")

# Set the background color to white
# For a list of named colors see
# https://api.arcade.academy/en/latest/arcade.color.html
# Colors can also be specified in (red, green, blue) format and
# (red, green, blue, alpha) format.
arcade.set_background_color(arcade.color.WHITE)

# Start the render process. This must be done before any drawing commands.
arcade.start_render()

board = InitialPosition.DEFAULT.value

#arcade.draw_circle_filled(X_A1, Y_A1, SIZE, arcade.color.GREEN)
spaces = [member for member in Space if member.name != "OFF"]
sprites = []
for s in spaces:
    x,y = _space_to_board_indices(s)
    if board[x][y] is Marble.WHITE:
        col = arcade.color.LIGHT_GRAY
    elif  board[x][y] is Marble.BLACK:
        col = arcade.color.BLACK
    else:
        col = arcade.color.WHITE
    pos = s.value[2:4]
    spr = SpriteCircle(SIZE/2.0, col)
    spr.set_position([pos[0], pos[1])
    sprites.append(spr)

arcade.finish_render()

arcade.run()
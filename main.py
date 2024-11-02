import cv2
from player import Player
from sprite_objects import *
from ray_casting import ray_casting_walls
from drawing import Drawing
from interaction import Interaction
from camera import camera_input, close_game, get_state

pygame.init()
sc = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
clock = pygame.time.Clock()

sc_map = pygame.Surface(MAP_RES)
sprites = Sprites()
player = Player(sprites)
drawing = Drawing(sc, sc_map, player, clock)
interaction = Interaction(player, sprites, drawing)

drawing.menu()
pygame.mouse.set_visible(False)
interaction.play_music()

cap = cv2.VideoCapture()
use_camera_frame = True

while True:

    use_camera_frame, image, biggest = camera_input(cap, use_camera_frame)
    cam_state = None

    if not use_camera_frame:
        cv2.imshow("Camera", image)
        cam_state = get_state(image, biggest)

    player.movement(cam_state)
    drawing.background()
    walls, wall_shot = ray_casting_walls(player, drawing.textures)
    drawing.world(walls + [obj.object_locate(player) for obj in sprites.list_of_objects])
    drawing.fps(clock)
    drawing.mini_map()
    drawing.player_weapon([wall_shot, sprites.sprite_shot])

    interaction.interaction_objects()
    interaction.npc_action()
    interaction.clear_world()
    interaction.check_win()

    pygame.display.flip()
    clock.tick()

    if close_game():
        break
import cv2
import numpy as np

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

if not cap.isOpened():
    cap.open(0)
ret, image = cap.read()

image_flip = cv2.flip(image, 1)

x, y, w, h = 215, 160, 210, 160  # simply hardcoded the values
img2 = cv2.rectangle(image_flip, (x, y), (x + w, y + h), 255, 2)
cv2.imshow('Camera', img2)
cv2.waitKey()

track_window = (x, y, w, h)

roi = image_flip[y:y + h, x:x + w]
hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv_roi, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)

term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

ret, frame = cap.read()

mouseX = 0
mouseY = 0
mouse2X = 0
mouse2Y = 0

def reposition(event, x, y, flag, _):
    global mouseX, mouseY, mouse2X, mouse2Y

    if event == cv2.EVENT_LBUTTONDOWN:
        mouseX, mouseY = x, y
        print(mouseX, mouseY)
    if event == cv2.EVENT_LBUTTONUP:
        mouse2X, mouse2Y = x, y
        print(mouse2X, mouse2Y)

while True:

    pad = (mouseX, mouseY, mouse2X, mouse2Y)
    use_camera_frame, image, track_window, roi_hist = camera_input(cap, use_camera_frame, roi_hist, track_window, term_crit, pad)
    cam_state = None

    if not use_camera_frame:
        cv2.imshow("Camera", image)
        cam_state = get_state(image, track_window)
        cv2.setMouseCallback('Camera', reposition)

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



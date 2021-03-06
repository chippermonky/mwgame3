from MW_datatypes import *

gamemode = 1
isFull = 1
lightingmode = 0

if isFull:
    DISPLAY_FLAGS = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.FULLSCREEN
else:
    DISPLAY_FLAGS = pygame.HWSURFACE|pygame.DOUBLEBUF
if gamemode == 1:
    SCREEN_SIZE = WIDTH, HEIGHT = 640,480
    LIGHTING = 1
    CAMERA_MODE = "force"
elif gamemode == 2:
    SCREEN_SIZE = WIDTH, HEIGHT = 1200,800
    LIGHTING = 0
    CAMERA_MODE = "nothing"
elif gamemode == 3:
    SCREEN_SIZE = WIDTH, HEIGHT = 800,600
    LIGHTING = 0
    CAMERA_MODE = "nothing"
elif gamemode == 4:
    SCREEN_SIZE = WIDTH, HEIGHT = 1200,800
    LIGHTING = 0
    CAMERA_MODE = "force"

FRAMERATE = 25
MSPERFRAME = 1000/FRAMERATE
TILING_SIZE = Vector2d(20,20)


#colors
COLOR_RED = 255,0,0
COLOR_WHITE = 255,255,255
COLOR_LIGHT_BLUE = 127,127,255
COLOR_BLACK = 0,0,0
COLOR_GREEN = 0,255,0
COLOR_DARK = 100,100,100
COLOR_KEY = COLOR_BLACK

#game constants
TORCH_RADIUS = 100,150
PLAYER_LIGHT_RADIUS = 50,75

MAN_START = Vector2d(-540,-40)
WOMAN_START = Vector2d(-780,-40)
#MAN_START = Vector2d(600,1640)
#WOMAN_START = Vector2d(0,1280)
#MAN_START = Vector2d(1300,1920)     #exit
#WOMAN_START = Vector2d(-320,840)
#MAN_START = Vector2d(760,740)
#MAN_START = Vector2d(520,1280)

SHADOW_LADY_START = Vector2d(120,-300)

#engine constants
dirMap = dict()
dirMap["RIGHT"] = 1
dirMap["LEFT"] = -1


def blankfcn(arg01 = None, arg02 = None):
    pass

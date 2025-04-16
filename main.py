# Define number of steps in each animation
WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]

import pygame
from pygame import mixer
from fighter import Fighter
import os

mixer.init()
pygame.init()

#create game window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

#set display to be centered on screen
os.environ['SDL_VIDEO_CENTERED'] = '1'
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fighting Game")

#set framerate
clock = pygame.time.Clock()
FPS = 60

#define colours
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

#define game variables
intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0, 0]#player scores. [P1, P2]
round_over = False
ROUND_OVER_COOLDOWN = 2000

#define fighter variables
WARRIOR_SIZE = 162
WARRIOR_SCALE = 4
WARRIOR_OFFSET = [72, 56]
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
WIZARD_SIZE = 250
WIZARD_SCALE = 3
WIZARD_OFFSET = [112, 107]
WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]

# Define base asset path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current file

# Load music and sounds
try:
    pygame.mixer.music.load(os.path.join(BASE_DIR, "assets", "audio", "assets_audio_music.mp3"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1, 0.0, 5000)
except:
    print("Warning: Could not load music file. Continuing without music.")

try:
    sword_fx = pygame.mixer.Sound(os.path.join(BASE_DIR, "assets", "audio", "assets_audio_sword.wav"))
    sword_fx.set_volume(0.5)
except:
    print("Warning: Could not load sword sound. Using empty sound.")
    sword_fx = pygame.mixer.Sound(buffer=bytes([]))

try:
    magic_fx = pygame.mixer.Sound(os.path.join(BASE_DIR, "assets", "audio", "assets_audio_magic (1).wav"))
    magic_fx.set_volume(0.75)
except:
    print("Warning: Could not load magic sound. Using empty sound.")
    magic_fx = pygame.mixer.Sound(buffer=bytes([]))

#load background image
try:
    bg_image = pygame.image.load(os.path.join(BASE_DIR, "assets", "images", "background.jpg")).convert_alpha()
except:
    print("Warning: Could not load background image. Creating blank background.")
    bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    bg_image.fill((50, 50, 50))  # Dark gray background

#load spritesheets
try:
    warrior_sheet = pygame.image.load(os.path.join(BASE_DIR, "assets", "images", "hero", "warrior.png")).convert_alpha()
except:
    print("Warning: Could not load hero spritesheet. Creating placeholder.")
    # Calculate the required size based on animation steps
    max_frames = max(WARRIOR_ANIMATION_STEPS)
    total_rows = len(WARRIOR_ANIMATION_STEPS)
    warrior_sheet = pygame.Surface((WARRIOR_SIZE * max_frames, WARRIOR_SIZE * total_rows))
    warrior_sheet.fill(RED)  # Red placeholder for warrior

try:
    wizard_sheet = pygame.image.load(os.path.join(BASE_DIR, "assets", "images", "evil_wizard", "wizard.png")).convert_alpha()
except:
    print("Warning: Could not load wizard spritesheet. Creating placeholder.")
    # Calculate the required size based on animation steps
    max_frames = max(WIZARD_ANIMATION_STEPS)
    total_rows = len(WIZARD_ANIMATION_STEPS)
    wizard_sheet = pygame.Surface((WIZARD_SIZE * max_frames, WIZARD_SIZE * total_rows))
    wizard_sheet.fill(BLUE)  # Blue placeholder for wizard

#load vicory image
try:
    victory_img = pygame.image.load(os.path.join(BASE_DIR, "assets", "images", "victory.png")).convert_alpha()
except:
    print("Warning: Could not load victory image. Creating placeholder.")
    victory_img = pygame.Surface((200, 100))
    victory_img.fill(YELLOW)  # Yellow placeholder

#define font
try:
    count_font = pygame.font.Font(os.path.join(BASE_DIR, "assets", "fonts", "turok.ttf"), 80)
    score_font = pygame.font.Font(os.path.join(BASE_DIR, "assets", "fonts", "turok.ttf"), 30)
except:
    print("Warning: Could not load custom font. Using system font.")
    count_font = pygame.font.SysFont(None, 80)
    score_font = pygame.font.SysFont(None, 30)

#function for drawing text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    text_rect = img.get_rect(center=(x, y))
    screen.blit(img, text_rect)

#function for drawing background
def draw_bg():
    scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))

#function for drawing fighter health bars
def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))


#create two instances of fighters
fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)

# Create gesture controller only for player 1
from gesture_controls import GestureController
gesture_controller_1 = GestureController(player_num=1)

# Start the gesture controller
gesture_controller_1.start()

#game loop
run = True
print("Starting game loop...")

while run:
  clock.tick(FPS)

  #draw background
  draw_bg()

  #show player stats
  draw_health_bar(fighter_1.health, 20, 20)
  draw_health_bar(fighter_2.health, 580, 20)
  draw_text("P1: " + str(score[0]), score_font, RED, 20, 60)
  draw_text("P2: " + str(score[1]), score_font, RED, 580, 60)

  #update countdown
  if intro_count <= 0:
    # Get gesture-based key states and merge them with keyboard input
    gesture_keys_1 = gesture_controller_1.get_current_keys()
    
    # Create a dictionary for key states
    key_state = {}
    real_keys = pygame.key.get_pressed()
    
    # Add keyboard keys to the dictionary
    for key_code in [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_r, pygame.K_t]:
        key_state[key_code] = real_keys[key_code] if key_code < len(real_keys) else False
    
    # Add gesture keys to the dictionary
    for key in gesture_keys_1:
        key_state[key] = True
        print(f"Active gesture key: {key}")

    #move fighters
    fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over, key_state)
    
    # AI movement for fighter 2 (make it stand still)
    fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over, {})
  else:
    #display count timer
    draw_text(str(intro_count), count_font, RED, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
    #update count timer
    if (pygame.time.get_ticks() - last_count_update) >= 1000:
      intro_count -= 1
      last_count_update = pygame.time.get_ticks()
      print(f"Countdown: {intro_count}")

  #update fighters
  fighter_1.update()
  fighter_2.update()

  #draw fighters
  fighter_1.draw(screen)
  fighter_2.draw(screen)

  #check for player defeat
  if round_over == False:
    if fighter_1.alive == False:
      score[1] += 1
      round_over = True
      round_over_time = pygame.time.get_ticks()
      print("Player 2 wins!")
    elif fighter_2.alive == False:
      score[0] += 1
      round_over = True
      round_over_time = pygame.time.get_ticks()
      print("Player 1 wins!")
  else:
    #display victory image
    screen.blit(victory_img, (360, 150))
    if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
      round_over = False
      intro_count = 3
      print("Starting new round...")
      fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
      fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)

  #event handler
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      print("Game closing...")
      # Clean up gesture controller before quitting
      gesture_controller_1.stop()
      run = False

  #update display
  pygame.display.update()

print("Game ended.")
# Clean up gesture controller
gesture_controller_1.stop()

#exit pygame
pygame.quit()
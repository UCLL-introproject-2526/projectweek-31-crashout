import pygame
from fighter1 import Fighter

pygame.init()

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("brawler")

clock = pygame.time.Clock()
FPS = 60
#colors
YELLOW = (255 ,255 ,0)
RED = (255 ,0, 0)
WHITE = (255,255,255)
BLACK = (0,0,0)

#define fight variables
DRIFTER_SIZE = 128
DRIFTER_SCALE = 5
DRIFTER_OFFSET = [43 ,56]
DRIFTER_DATA = [DRIFTER_SIZE, DRIFTER_SCALE, DRIFTER_OFFSET]
BIKER_SIZE = 48
BIKER_SCALE = 10
BIKER_OFFSET = [25, 12]
BIKER_DATA = [BIKER_SIZE, BIKER_SCALE,BIKER_OFFSET]
#load background
bg_image = pygame.image.load("images/background/forest.jpg").convert_alpha()

#load characters
Drifter_sheet = pygame.image.load("images/characters/Drifter/untitled.png").convert_alpha()
Biker_sheet = pygame.image.load("images/characters/Biker/gooder.png").convert_alpha()

#define number steps
DRIFTER_ANIMATION_STEPS = [7, 10, 10, 6, 6, 4, 5] 
BIKER_ANIMATION_STEPS = [4, 6, 4, 6, 8, 2, 6]     


def draw_bg():
    scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0,0))
def draw_health_bar(health,x,y):
     ratio = health / 100
     pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 604, 44))
     pygame.draw.rect(screen, RED, (x, y, 600, 40))
     pygame.draw.rect(screen, YELLOW, (x, y, 600 * ratio, 40))
     
fighter_1 = Fighter(320, 620, False, DRIFTER_DATA, Drifter_sheet, DRIFTER_ANIMATION_STEPS)
fighter_2 = Fighter(1400, 450, True, BIKER_DATA, Biker_sheet, BIKER_ANIMATION_STEPS)


running = True
while running:
    
    clock.tick(FPS)
    #draw background
    draw_bg()
    #draw health bar
    draw_health_bar(fighter_1.health, 200,100)
    draw_health_bar(fighter_2.health, 1120,100)
    
    fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2)
    

    #update fighters
    fighter_1.update()
    fighter_2.update()
    #draw fighters
    fighter_1.draw(screen)
    fighter_2.draw(screen)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                running = False

    pygame.display.update()    

pygame.quit()




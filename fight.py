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

#define game variables
intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0, 0]
round_over = False
round_over_time = 0
ROUND_OVER_COOLDOWN = 2000

#define fight variables
DRIFTER_SIZE = 128
DRIFTER_SCALE = 5
DRIFTER_OFFSET = [45, 56]
DRIFTER_DATA = [DRIFTER_SIZE, DRIFTER_SCALE, DRIFTER_OFFSET]
BIKER_SIZE = 128
BIKER_SCALE = 5
BIKER_OFFSET = [43 ,56]
BIKER_DATA = [BIKER_SIZE, BIKER_SCALE,BIKER_OFFSET]
#load background
bg_image = pygame.image.load("images/background/forest.jpg").convert_alpha()

#load characters
Drifter_sheet = pygame.image.load("images/characters/Drifter/full2.png").convert_alpha()
Biker_sheet = pygame.image.load("images/characters/Biker/untitled.png").convert_alpha()

#load victory
victory_img = pygame.image.load("images/victory/victory.png").convert_alpha()
victory_img = pygame.transform.scale(victory_img, (1000, 200))


#define number steps
DRIFTER_ANIMATION_STEPS = [11, 8, 16, 5, 3, 3, 4]
BIKER_ANIMATION_STEPS = [7, 10, 10, 6, 6, 4, 5] 
     

count_font = pygame.font.Font("images/font/Turok.ttf", 80)
score_font = pygame.font.Font("images/font/Turok.ttf", 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))
def draw_bg():
    scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0,0))
def draw_health_bar(health,x,y):
     ratio = health / 100
     pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 604, 44))
     pygame.draw.rect(screen, RED, (x, y, 600, 40))
     pygame.draw.rect(screen, YELLOW, (x, y, 600 * ratio, 40))
     
fighter_1 = Fighter(1, 320, 620, False, DRIFTER_DATA, Drifter_sheet, DRIFTER_ANIMATION_STEPS, is_cpu=False)
fighter_2 = Fighter(2, 1400, 450, True, BIKER_DATA, Biker_sheet, BIKER_ANIMATION_STEPS, is_cpu=True)


running = True
while running:
    
    clock.tick(FPS)
    #draw background
    draw_bg()
    #draw health bar
    draw_health_bar(fighter_1.health, 200,100)
    draw_health_bar(fighter_2.health, 1120,100)
    draw_text("P1: " + str(score[0]), score_font, RED, 750, 140)
    draw_text("AI: " + str(score[1]), score_font, RED, 1130, 140)

    
    if intro_count <= 0:
        fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over)
        fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen,fighter_1, round_over)
    else:
        img = score_font.render(str(intro_count), True, RED)
        screen.blit(img, (SCREEN_WIDTH /2 , SCREEN_HEIGHT /3))

        if (pygame.time.get_ticks() - last_count_update) >= 1000:
            intro_count -= 1
            last_count_update = pygame.time.get_ticks()
    #update fightersd
    fighter_1.update()
    fighter_2.update()
    #draw fighters
    fighter_1.draw(screen)
    fighter_2.draw(screen)
    
    if round_over == False:
        if fighter_1.alive == False:
            score[1] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
            print(score)
        elif fighter_2.alive == False:
            score[0] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
    else:
        screen.blit(victory_img,(440,150))
        if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
            round_over = False
            fighter_1 = Fighter(1, 320, 620, False, DRIFTER_DATA, Drifter_sheet, DRIFTER_ANIMATION_STEPS, is_cpu=False)
            fighter_2 = Fighter(2, 1400, 450, True, BIKER_DATA, Biker_sheet, BIKER_ANIMATION_STEPS, is_cpu=True)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                running = False

    pygame.display.update()    

pygame.quit()




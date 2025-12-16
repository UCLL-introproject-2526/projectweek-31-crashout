import pygame
from fighter1 import Fighter

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("brawler")

clock = pygame.time.Clock()
FPS = 60

bg_image = pygame.image.load("images/background/background.png").convert_alpha()

    
def draw_bg():
    scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0,0))
    
fighter_1 = Fighter(200, 310)
fighter_2 = Fighter(500, 310)


running = True
while running:
    
    clock.tick(FPS)
    
    draw_bg()
    
    fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    
    fighter_1.draw(screen)
    fighter_2.draw(screen)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                running = False

    pygame.display.update()    

pygame.quit()




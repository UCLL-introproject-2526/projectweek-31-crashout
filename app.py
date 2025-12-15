import pygame

pygame.init()
screen_size = (800,600)
screen = pygame.display.set_mode(screen_size)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

pygame.quit()

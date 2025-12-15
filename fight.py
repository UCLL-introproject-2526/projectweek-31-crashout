import pygame

def create_main_surface():
    screen_size = (800, 600)
    screen = pygame.display.set_mode(screen_size)
    return screen

def main():
    pygame.init()

    screen = create_main_surface()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()

    pygame.quit()

main() 
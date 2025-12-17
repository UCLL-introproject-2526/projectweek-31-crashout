import pygame

pygame.init()
pygame.display.set_mode((1, 1))   # tiny hidden window, just for convert_alpha

img = pygame.image.load("images/characters/Drifter/full.png").convert_alpha()
print("full sheet size:", img.get_size())

SIZE = 128
frame0 = img.subsurface(0, 0, SIZE, SIZE)
print("frame0 size:", frame0.get_size())

import pygame
class HitSpark:
    def __init__(self, x, y, flip):
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.alive = True

        try:
            # 1. Load your new horizontal strip
            # (Make sure the file name matches exactly!)
            img = pygame.image.load("images/fx/just.png").convert_alpha()
            
            # 2. Simplified Math
            cols = 14 # Looking at your image, it looks like 15 frames
            width = img.get_width() // cols
            height = img.get_height()

            for i in range(cols):
                # We only move on the X axis (i * width), Y is always 0
                rect = pygame.Rect(i * width, 0, width, height)
                frame = img.subsurface(rect)
                
                # Scale it up (adjust 300, 300 to fit your characters)
                frame = pygame.transform.scale(frame, (300, 300))
                
                if flip:
                    frame = pygame.transform.flip(frame, True, False)
                self.animation_list.append(frame)

        except Exception as e:
            print(f"!!! IMAGE ERROR: {e}")
            # Red cube fallback
            fallback = pygame.Surface((50, 50))
            fallback.fill((255, 0, 0))
            self.animation_list = [fallback]

        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, surface):
        if self.frame_index < len(self.animation_list):
            surface.blit(self.animation_list[self.frame_index], self.rect)
            
            # Speed: 30ms per frame makes the hit feel snappy
            if pygame.time.get_ticks() - self.update_time > 30: 
                self.frame_index += 1
                self.update_time = pygame.time.get_ticks()
        else:
            self.alive = False
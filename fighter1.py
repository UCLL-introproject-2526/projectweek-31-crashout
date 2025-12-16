import pygame

class Fighter():
    def __init__(self, x, y):
        self.rect= pygame.Rect((x,y, 80, 180))
        self.vel_y = 0
        
    
    def move(self, screen_width, screen_height):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            dx = -SPEED
        if key[pygame.K_d]:
            dx = +SPEED
            
        if key[pygame.K_w]:
            self.vel_y = -30
            
        self.vel_y += GRAVITY
        dy += self.vel_y
        
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            dy = screen_height - 110 - self.rect.bottom
            
        
        self.rect.x += dx 
        self.rect.y += dy 
            
    
    
    def draw(self, surface):
        pygame.draw.rect(surface, (255,0,0), self.rect)
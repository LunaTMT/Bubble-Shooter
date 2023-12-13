import pygame
import random
import sys


pygame.init()






class Bubble(pygame.sprite.Sprite):
    
    IMAGES = [
        'assets/images/bubbles/bubbles_1.png',
        'assets/images/bubbles/bubbles_2.png',
        'assets/images/bubbles/bubbles_3.png',
        'assets/images/bubbles/bubbles_4.png',
        'assets/images/bubbles/bubbles_5.png',
        'assets/images/bubbles/bubbles_6.png'] 



    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(random.choice(Bubble.IMAGES)).convert_alpha()  # Randomly select a bubble image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = random.randint(1, 2)  # Random speed

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()  # Remove the bubble when it goes off the screen
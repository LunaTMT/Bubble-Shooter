import pygame
import random
import sys
from .constants import screen

# Fish class
class Fish(pygame.sprite.Sprite):

    IMAGES = [
        #'assets/images/fishes/fish.png',
        'assets/images/fishes/fish_one.png',
        'assets/images/fishes/fish_three.png',
        #'assets/images/fishes/fish1.png',
        'assets/images/fishes/fish1_one.png',
        'assets/images/fishes/fish1_three.png',
        #'assets/images/fishes/fish2.png',
        'assets/images/fishes/fish2_one.png',
        'assets/images/fishes/fish2_three.png',
        #'assets/images/fishes/fish3.png',
        'assets/images/fishes/fish3_one.png',
        'assets/images/fishes/fish3_three.png',
        #'assets/images/fishes/fish4.png',
        'assets/images/fishes/fish4_one.png',
        'assets/images/fishes/fish4_three.png']
    
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(random.choice(Fish.IMAGES)).convert_alpha()
        self.image.set_alpha(random.randint(100, 200))  # Set random transparency
        self.rect = self.image.get_rect()
        self.rect.x = screen.WIDTH  # Start from the right side of the screen
        self.rect.y = random.randint(0, screen.HEIGHT - self.rect.height)  # Random y position
        self.speed = random.randint(1, 2)  # Random speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()  # Remove the fish when it goes off the screen

        
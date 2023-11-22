import pygame
from pygame.sprite import Group
from pygame.math import Vector2
import math
import random

WIDTH = 800
HEIGHT = 1000

WHITE = (255, 255, 255) 
BLACK = (0,0,0)
RED = (255,0,0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
GREY = (128, 128, 128)


GRID_WIDTH = 16
GRID_HEIGHT = 20
CELL_SIZE = 50 # Each cell is 40x40 pixels

class Game:

    def __init__(self):
        self.running = True

        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Create the main surface

        self.center_x = WIDTH // 2
        self.center_y = HEIGHT // 2

        self.ball_colours = (RED, GREEN, BLACK, YELLOW, BLUE, WHITE)

        #default shoot ball
        self.ball = Ball(self, 
                        position = (self.center_x, HEIGHT-100),
                        radius = 25,
                        colour = random.choice(self.ball_colours),
                        velocity = (0, 0))
        self.ball.shoot = True

        self.top_balls = [[Ball(self, 
                                position = (i * CELL_SIZE, j * CELL_SIZE),
                                radius = 25,
                                colour = random.choice(self.ball_colours),
                                velocity = (0, 0))
                                for i in range(1, 16)] for j in range(1, 6)]
        
        print(self.top_balls)
        
        self.all_sprites = Group(ball for row in self.top_balls for ball in row)
        
        # Euclidean distance.
        self.calc_distance = lambda collided_ball, : math.sqrt((self.ball.rect.x - collided_ball.rect.x) ** 2 + (self.ball.rect.y - collided_ball.rect.y) ** 2)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            for sprite in self.all_sprites:
                sprite.handle_events(event)
            
            self.ball.handle_events(event)

    def update(self):
        collisions = pygame.sprite.spritecollide(self.ball, self.all_sprites, False)

        if collisions:
            #Unfortunately must sort by euclidean distance because there is more than one collision at times
            collisions.sort(key=self.calc_distance) 
            collided_ball = collisions[0] #closest

            self.ball.velocity = pygame.math.Vector2(0, 0)
            self.ball.rect.center = Vector2(collided_ball.rect.center) + Vector2(0, collided_ball.radius * 2)
            self.ball.moving = False


        for sprite in self.all_sprites:
            sprite.update()
        self.ball.update()


    def render(self):
        self.screen.fill(GREY)
        self.all_sprites.draw(self.screen)
        pygame.draw.line(self.screen, RED, (self.center_x, 0), (self.center_x, HEIGHT), 5)  # (start), (end), (line thickness)
        
        if not self.ball.shot:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            direction = pygame.math.Vector2(mouse_x - self.ball.x, mouse_y - self.ball.y)
            direction.normalize_ip()
            endpoint = (self.ball.x + direction.x * 200, self.ball.y + direction.y * 200)
            pygame.draw.line(self.screen, BLACK, self.ball.rect.center, endpoint, 5)  

        self.ball.draw(self.screen)


    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            pygame.display.flip() 
        pygame.quit()
        


class Ball(pygame.sprite.Sprite):

    def __init__(self, game, position, radius, colour, velocity):
        super().__init__() 

        self.game = game
        self.radius = radius
        self.colour = colour
        self.position = self.x, self.y = position
        self.diameter = self.radius * 2
        
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, colour, (radius, radius), radius)
        self.rect = self.image.get_rect(center=position)
        self.velocity = pygame.math.Vector2(velocity)

        self.shoot = False
        self.shot = False
        self.moving = False
        self.speed = 10
  

    def __str__(self) -> str:
        return f"{self.position} {self.colour}"

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
 
    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.moving and self.shoot: 
            mouse_x, mouse_y = pygame.mouse.get_pos()


            self.velocity = pygame.math.Vector2(mouse_x - self.x, mouse_y - self.y).normalize() * self.speed

            self.velocity.normalize() # * self.speed

            self.moving = True
            self.shot = True

    def update(self):
        
        if self.moving:
            self.rect.move_ip(self.velocity)
            self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
            
            if self.rect.left == 0 or self.rect.right == WIDTH:
                self.velocity.x *= -1
                
            if self.rect.top == 0 or self.rect.bottom == HEIGHT:
                self.velocity.y *= -1
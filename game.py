import pygame
from pygame.sprite import Group
from pygame.sprite import Sprite
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
        self.generate_shooting_ball()

        self.top_balls = [[Ball(self, 
                                position = (i * CELL_SIZE, j * CELL_SIZE),
                                radius = 25,
                                colour = random.choice(self.ball_colours),
                                velocity = (0, 0))
                                for i in range(1, 16)] for j in range(1, 6)]
        
        for row in self.top_balls:
            for ball in row:
                ball.position.x -= ball.radius * 2  # Adjust the x-coordinate to align with the top edge
                ball.position.y += ball.radius * 2  # Adjust the y-coordinate to align with the top edge
        
        self.all_sprites = Group(ball for row in self.top_balls for ball in row)

        
        # Euclidean distance.
        self.calc_distance = lambda collided_ball, : math.sqrt((self.ball.rect.centerx - collided_ball.rect.centerx) ** 2 + (self.ball.rect.centery - collided_ball.rect.centery) ** 2)

    def generate_shooting_ball(self):
        self.ball = Ball(self, 
                        position = (self.center_x, HEIGHT-100),
                        radius = 25,
                        colour = random.choice(self.ball_colours),
                        velocity = (0, 0))
        self.ball.shooter = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            for sprite in self.all_sprites:
                sprite.handle_events(event)
            
            self.ball.handle_events(event)

    def update(self):
        collisions = pygame.sprite.spritecollide(self.ball, self.all_sprites, dokill=False, collided=pygame.sprite.collide_mask)

        
        if collisions:
            
            collisions.sort(key=self.calc_distance) 
            collided_ball = collisions[0] 
            self.ball.velocity = Vector2(0, 0)
            self.ball.moving = False
            print(collided_ball)
            side = self.detect_collision_side(self.ball.rect, collided_ball.rect)
            
            match side:
                case "bottom":
                    self.ball.rect.center = Vector2(collided_ball.rect.center) + Vector2(0, collided_ball.diameter)
                case "top":
                    self.ball.rect.center = Vector2(collided_ball.rect.center) - Vector2(0, collided_ball.diameter)
                case "right":
                    self.ball.rect.center = Vector2(collided_ball.rect.center) + Vector2(collided_ball.diameter, 0)
                case "left":
                    self.ball.rect.center = Vector2(collided_ball.rect.center) - Vector2(collided_ball.diameter, 0)


            print(side)
            self.all_sprites.add(self.ball)
            self.generate_shooting_ball() 
           
        for sprite in self.all_sprites:
            sprite.update()

        self.ball.update()


    def detect_collision_side(self, rect1, rect2):
        if rect1.colliderect(rect2):
            # Calculate the distances between the centers in both x and y axes
            dx = rect2.centerx - rect1.centerx
            dy = rect2.centery - rect1.centery

            # Calculate the combined half-widths and half-heights of the rectangles
            combined_half_width = (rect1.width + rect2.width) / 2
            combined_half_height = (rect1.height + rect2.height) / 2

            # Determine the side of collision based on the distances and combined sizes
            if abs(dx) <= combined_half_width and abs(dy) <= combined_half_height:
                overlap_x = combined_half_width - abs(dx)
                overlap_y = combined_half_height - abs(dy)

                if overlap_x >= overlap_y:
                    if dy > 0:
                        return "top"  # Collision on the bottom side of rect1
                    else:
                        return "bottom"  # Collision on the top side of rect1
                else:
                    if dx > 0:
                        return "left"  # Collision on the right side of rect1
                    else:
                        return "right"  # Collision on the left side of rect1

        return None  # No collision detected or partial overlap



    def render(self):
        self.screen.fill(GREY)
        self.all_sprites.draw(self.screen)
        pygame.draw.line(self.screen, RED, (self.center_x, 0), (self.center_x, HEIGHT), 5)  # (start), (end), (line thickness)
        
        if not self.ball.shot:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            direction = pygame.math.Vector2(mouse_x - self.ball.rect.centerx, mouse_y - self.ball.rect.centery)
            direction.normalize_ip()
            endpoint = (self.ball.rect.centerx + direction.x * 200, self.ball.rect.centery + direction.y * 200)
            
            # Draw a line from the ball's center to the calculated endpoint
            pygame.draw.line(self.screen, BLACK, self.ball.rect.center, endpoint, 5)

        self.ball.draw(self.screen)


    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            pygame.display.flip() 
        pygame.quit()
        


class Ball(Sprite):
    def __init__(self, game, position, radius, colour, velocity):
        super().__init__()

        """
        self.game = game
        self.radius = radius
        self.diameter = radius * 2
        self.color = colour
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, colour, (radius, radius), radius)
        self.rect = self.image.get_rect(center=position)
        """
        self.x, self.y = position
        self.game = game
        self.radius = radius
        self.diameter = radius * 2
        self.width = radius*2
        self.height = radius*2
        self.colour = colour
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, colour, (0, 0, self.width, self.height))  # Draw a rectangle
        self.rect = self.image.get_rect(center=position)

        # Set a circular mask for collision detection
       # self.mask = pygame.mask.from_surface(self.image)

        self.position = Vector2(position)
        self.velocity = Vector2(velocity)

        self.shooter = False
        self.shot = False
        self.moving = False
        self.speed = 10
  

    def __str__(self) -> str:
        return f"{self.position} {self.colour}"

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
 
    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.moving and self.shooter: 
            mouse_x, mouse_y = pygame.mouse.get_pos()
            direction_vector = pygame.math.Vector2(mouse_x - self.position.x, mouse_y - self.position.y)
            self.velocity = direction_vector.normalize() * self.speed
           
            self.moving = True
            self.shooter = False
            self.shot = True
            
            
            

    def update(self):
        if self.moving:
            self.position += self.velocity
            self.rect.center = self.position  # Update the rectangle position to match the circle
            self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))


            if self.rect.left == 0 or self.rect.right == WIDTH:
                self.velocity.x *= -1
                
            if self.rect.top == 0 or self.rect.bottom == HEIGHT:
                self.velocity.y *= -1
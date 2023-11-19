import pygame
import random

WIDTH = 800
HEIGHT = 1000

WHITE = (255, 255, 255) 
BLACK = (0,0,0)
RED = (255,0,0)

class Game:

    def __init__(self):
        self.running = True

        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Create the main surface

        self.center_x = WIDTH // 2
        self.center_y = HEIGHT // 2

        self.ball = Ball(self, 25, BLACK, (self.center_x, HEIGHT-100))

        self.ball_colours = ('R', 'G', 'B', 'Y', 'B', 'W')
        self.top_balls = [[random.choice(self.ball_colours) for i in range(32)] for j in range(5)]
        print(self.top_balls)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            self.ball.handle_events(event)
            
    def update(self):
        self.ball.update()

    def render(self):
        self.screen.fill(WHITE)
        self.ball.draw(self.screen)
        pygame.draw.line(self.screen, RED, (self.center_x, 0), (self.center_x, HEIGHT), 5)  # (start), (end), (line thickness)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            pygame.display.flip() 
        pygame.quit()
        
    

class Ball(pygame.sprite.Sprite):

    def __init__(self, game, radius, colour, pos):
        super().__init__() 

        self.game = game
        self.radius = radius
        self.colour = colour
        self.x, self.y = pos
        self.diameter = self.radius * 2
        
        self.surface = pygame.Surface((self.diameter, self.diameter), pygame.SRCALPHA)
        pygame.draw.circle(self.surface, colour, (radius, radius), radius)
        self.rect = self.surface.get_rect()
        self.rect.center = (pos[0], pos[1])

        self.shot = False
        self.moving = False
        self.speed = 5
        self.direction = [0, 0]


    def draw(self, screen):
        screen.blit(self.surface, self.rect.topleft)
        pygame.draw.line(self.game.screen, BLACK, self.rect.center, pygame.mouse.get_pos(), 5)  # (start), (end), (line thickness)

        
    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.moving: 
            self.moving = True
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.direction = pygame.math.Vector2(mouse_x - self.rect.x, mouse_y - self.rect.y).normalize() * self.speed



    def update(self):
        self.rect.x += self.direction[0]
        self.rect.y += self.direction[1]

        if not (0 < self.rect.left < WIDTH):
            self.direction.x *= -1
        if not (0 < self.rect.top < HEIGHT):
            self.direction.y *= -1   
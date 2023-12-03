import pygame
from pygame.sprite import Group
from pygame.sprite import Sprite
from pygame.math import Vector2
import math
import random
from collections import deque


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

        self.shoot_ball_colours = (RED, GREEN, BLACK, YELLOW, BLUE, WHITE)

        #default shoot ball
        self.generate_shooting_ball()

        self.top_balls = [[Ball(self, 
                                position = (i * CELL_SIZE, j * CELL_SIZE),
                                radius = 25,
                                colour = random.choice(self.shoot_ball_colours),
                                velocity = (0, 0))
                                for i in range(1, 16)] for j in range(1, 6)]
        
        #The maximum number of rows for a ball is 17
        # Draw a line on 17th row
        #As soon as 18th row passed -> game over
        
        self.all_balls = self.top_balls + [[0] * 16 for _ in range(10)]
        self.rows, self.columns = len(self.all_balls[0]), len(self.all_balls)

        for row in self.top_balls:
            for ball in row:
                ball.position.x -= ball.radius * 2  
                ball.position.y += ball.radius * 2  
        
        self.all_sprites = Group(ball for row in self.top_balls for ball in row)

        # Euclidean distance.
        self.calc_distance = lambda collided_ball, : math.sqrt((self.shoot_ball.rect.centerx - collided_ball.rect.centerx) ** 2 + (self.shoot_ball.rect.centery - collided_ball.rect.centery) ** 2)

    def generate_shooting_ball(self):
        self.shoot_ball = Ball(self, 
                        position = (self.center_x, HEIGHT-100),
                        radius = 25,
                        colour = random.choice(self.shoot_ball_colours),
                        velocity = (0, 0))
        self.shoot_ball.shooter = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            for sprite in self.all_sprites:
                sprite.handle_events(event)
            
            self.shoot_ball.handle_events(event)

    def update(self):
        collisions = pygame.sprite.spritecollide(self.shoot_ball, self.all_sprites, dokill=False, collided=pygame.sprite.collide_mask)

        if collisions:
            collisions.sort(key=self.calc_distance) 
            collided_ball = collisions[0] 
            self.shoot_ball.velocity = Vector2(0, 0)
            self.shoot_ball.moving = False
            side = self.detect_collision_side(self.shoot_ball.rect, collided_ball.rect)
            
            match side:
                case "bottom":
                    self.shoot_ball.rect.center = Vector2(collided_ball.rect.center) + Vector2(0, collided_ball.diameter)
                case "top":
                    self.shoot_ball.rect.center = Vector2(collided_ball.rect.center) - Vector2(0, collided_ball.diameter)
                case "right":
                    self.shoot_ball.rect.center = Vector2(collided_ball.rect.center) + Vector2(collided_ball.diameter, 0)
                case "left":
                    self.shoot_ball.rect.center = Vector2(collided_ball.rect.center) - Vector2(collided_ball.diameter, 0)


            """Once collided, we want to check the balls surrounding collided_ball only if it is the same colour as self.shoot_ball
            We do this using BFS 
            If it is same colour as self.shoot_ball then we kill it
            Afterwards we check every item in visited to see if they are connected to anything
            """ 

            #Set the shooter ball into the correct array position based ont the ball it collided with
            r, c = self.shoot_ball.get_array_position()
            print(self.shoot_ball, r, c)
            self.all_balls[r][c] = self.shoot_ball

            #Have any bubbles been poped?
            popped_any = self.check_pop()
            
            #If bubble has been popped, we must check for disconnected islands and deal with them (kill)
            #Else : #The current shooter ball must now be added to the rest of the balls (all_sprites) for special handling
            if popped_any: self.remove_disconnected_islands()
            else:  self.all_sprites.add(self.shoot_ball) 
 
            #A new ball a player can shoot must always be generated upon clicking
            self.generate_shooting_ball() 
           

        #Update for 'static' balls
        for sprite in self.all_sprites:
            sprite.update()
        
        # Special update 
        self.shoot_ball.update()

    def remove_disconnected_islands(self):
        
        visited = [[False for i in range(self.columns)] for _ in range(self.rows)]
        islands = []

        def DFS(i, j, island_locations):
            directions = [(0, -1), (-1, 0), (0, 1), (1, 0)]
            visited[i][j] = True
            island_locations.append((i, j))

            for (new_row, new_col) in self.get_valid_neighbours((i, j)):
                if self.in_bounds((new_row, new_col)) and self.all_balls[new_row][new_col] and not visited[new_row][new_col]:
                    DFS(new_row, new_col, island_locations)
    
        def get_islands():
            for i in range(self.rows):
                for j in range(self.columns):
                    if self.all_balls[i][j] and not visited[i][j]:
                        island_locations = []
                        DFS(i, j, island_locations)
                        if not any(pos[0] == 0 for pos in island_locations):
                            islands.append(island_locations)
            return islands
        
        for island in get_islands():
            for r, c in island:
                self.all_balls[r][c].fall = True
                self.all_balls[r][r] = 0
                
                        
    def get_valid_neighbours(self, position):
        x, y = position
        return [tup for tup in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)) if self.in_bounds(tup)]

    def in_bounds(self, pos):
        return (0 <= pos[0] < 15 and 0 <= pos[1] < 15)

    def check_pop(self):
        
        kill = {self.shoot_ball}  # Using a set to avoid duplicate balls
        visited = set()  # To track visited nodes
        queue = deque([self.shoot_ball.get_array_position()])  # Initialize a queue with the starting node

    
        while queue:
            node = queue.popleft()  # Dequeue the node from the queue
            if node not in visited:
                visited.add(node)  # Mark node as visited

                x, y = node
                current_ball = self.all_balls[x][y]

                if current_ball and current_ball.colour == self.shoot_ball.colour:
                    kill.add(current_ball)  # Add ball to kill set

                    # Enqueue adjacent nodes that have not been visited
                    for pos in self.get_valid_neighbours(current_ball.get_array_position()):
                        queue.append(pos)

        if len(kill) >= 3:
            for ball in kill:
                x, y = ball.get_array_position()
                print(x, y)
                self.all_balls[x][y] = 0
                ball.kill()
            return True
        return False
                                  
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
        
        if not self.shoot_ball.shot:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            direction = pygame.math.Vector2(mouse_x - self.shoot_ball.rect.centerx, mouse_y - self.shoot_ball.rect.centery)
            direction.normalize_ip()
            endpoint = (self.shoot_ball.rect.centerx + direction.x * 200, self.shoot_ball.rect.centery + direction.y * 200)
            
            # Draw a line from the ball's center to the calculated endpoint
            pygame.draw.line(self.screen, BLACK, self.shoot_ball.rect.center, endpoint, 5)

        self.shoot_ball.draw(self.screen)


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

        
        self.game = game
        self.radius = radius
        self.diameter = radius * 2
        self.colour = colour
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, colour, (radius, radius), radius)
        self.rect = self.image.get_rect(center=position)

        self.color_map = {
            (255, 255, 255): 'WHIT',
            (0, 0, 0): 'BLAC',
            (255, 0, 0): 'RED_',
            (0, 0, 255): 'BLUE',
            (255, 255, 0): 'YELL',
            (0, 255, 0): 'GREE',
            (128, 128, 128): 'GREY'}
        
        """self.x, self.y = position
        self.game = game
        self.radius = radius
        self.diameter = radius * 2
        self.width = radius*2
        self.height = radius*2
        self.colour = colour
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, colour, (0, 0, self.width, self.height))  # Draw a rectangle
        self.rect = self.image.get_rect(center=position)"""

        # Set a circular mask for collision detection
        self.mask = pygame.mask.from_surface(self.image)

        self.position = Vector2(position)
        self.velocity = Vector2(velocity)

        self.shooter = False
        self.shot = False
        self.moving = False
        self.speed = 10
        self.fall = False
  

    def __str__(self) -> str:
        return f"{self.position} {self.colour}"

    def __repr__(self) -> str:
        return str(self.color_map[self.colour])

    def get_array_position(self):
        return (int(self.rect.centery / 50) - 1, int(self.rect.centerx / 50) - 1)

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
        
        if self.fall:
            self.rect.y += 10

            if self.rect.y > HEIGHT: 
                self.kill()
            
            



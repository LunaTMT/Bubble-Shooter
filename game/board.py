
from collections import deque
import pprint
import os
from .ball import Ball
from .constants import screen


import pygame
import sys

class Board(list):

    SHIFT_SOUND = pygame.mixer.Sound('assets/sounds/shift.mp3')
    END_GAME_SOUND = pygame.mixer.Sound('assets/sounds/end.wav')

    def __init__(self, data):
        super().__init__(data)
        self.rows = len(data)
        self.columns = len(data[0])
        
        self.total_misses = 0
        self.shift_count = 6

        #For every x (shift_count) misses we add new top row and decrease shift_count by 1
        
    def remove_disconnected_islands(self):
        visited = [[False for _ in range(self.columns)] for _ in range(self.rows)]
        islands = []

        def DFS(r, c, island_locations):
            visited[r][c] = True
            island_locations.append((r, c))
            directions = ((r, c-1), (r-1, c), (r, c+1), (r+1, c))

            for (new_row, new_col) in directions: # self.get_valid_neighbours((r, c)):
                if self.in_bounds((new_row, new_col)) and self[new_row][new_col] and not visited[new_row][new_col]:
                    DFS(new_row, new_col, island_locations)
    
        def get_islands():
            for r in range(self.rows):
                for c in range(self.columns):
                    if self[r][c] and not visited[r][c]:
                        island_locations = []
                        DFS(r, c, island_locations)
                        if not any(pos[0] == 0 for pos in island_locations):
                            islands.append(island_locations)
            return islands
        
        for island in get_islands():
            for r, c in island:
                #Getting rid of falling mechanism for now and just poping bubbles as other versions do
                self[r][c].fall = True
                self[r][c].fall_position = (r, c)
                self.game.static_balls.remove(self[r][c])
                self.game.all_falling_balls.add(self[r][c])
                self.game.points +=  int(self.game.point_multiplier * 15)
            Ball.FALL_SOUND.play()
             
    def get_valid_neighbours(self, position):
        r, c  = position
        left_right = ((r, c-1), (r,c+1))

        if r%2: # if row is odd:
            directions = ((r-1, c), (r-1, c+1), (r+1, c), (r+1, c+1))  # UP, UP-RIGHT, DOWN, DOWN_RIGHT
        else:
            directions = ((r-1, c), (r-1, c-1), (r+1,c-1), (r+1,c))   #UP, UP-LEFT, DOWN-LEFT, DOWN
        
        return [tup for tup in (directions + left_right) if self.in_bounds(tup)]

    def get_static_balls(self):
        return [ball for row in self for ball in row if isinstance(ball, Ball)]


    def check_pop(self):
        to_kill = set()  # Using a set to avoid duplicate balls
        visited = set()  # To track visited nodes
        queue = deque([self.game.shoot_ball.array_position])  # Initialize a queue with the starting node
        
        while queue:
            node = queue.popleft()  # Dequeue the node from the queue
            if node not in visited:
                visited.add(node)  # Mark node as visited

                r, c = node
                current_ball = self[r][c]

                if current_ball and current_ball.colour == self.game.shoot_ball.colour:
                    to_kill.add(current_ball)  # Add ball to kill set

                    # Enqueue adjacent nodes that have not been visited
                    for pos in self.get_valid_neighbours(current_ball.array_position):
                        queue.append(pos)

        #os.system('cls' if os.name == 'nt' else 'clear')

        if len(to_kill) >= 3:
            for ball in to_kill:
                r, c = ball.array_position
                ball.kill()
                self[r][c] = 0
                self.game.points +=  int(self.game.point_multiplier * 10)
            ball.POP_SOUND.play()
            self.remove_disconnected_islands()






        # Rest of your code interacting with 'to_kill' list...




        
        


        if len(to_kill) == 1:
            self.total_misses += 1

    def check_shift(self):    
        #If the user has missed (self.shift_count) times then we shift  
        if self.total_misses == self.shift_count:
            for ball in self.get_static_balls():
                if ball.row == self.rows-1:
                    self.game.end_game = True
                ball.row += 1   
                
            temp = self.shift_count - 1
            if temp < 3:
                temp = 3
                
            self.__init__([[Ball(self.game, (0, c)) for c in range(screen.GRID_WIDTH)]] + self[:-1])
            Board.SHIFT_SOUND.play()
            self.shift_count = temp
            
            self.game.level += 1
            self.game.point_multiplier += 0.1


    def in_bounds(self, position):
        row, column = position
        return (0 <= row < self.rows and 0 <= column < self.columns)
    
    def balls_are_in_out_of_bounds_zone(self): 
        return any(1 for ball in self[-1] if ball)
    
    def print_board(self):
        os.system('clear') 
        pp = pprint.PrettyPrinter(width=50, compact=True)
        pp.pprint(self)
           
               
    def update(self):
        #Get the new position of the shooter ball
        row, column = new_position = self.game.shoot_ball.array_position

        #We check if the ball is in bounds - if not then it is the end game
        if not self.in_bounds(new_position):
            self.game.end_game = True
            Board.END_GAME_SOUND.play()
            return

        #It is valid and update its position to the board
        self[row][column] = self.game.shoot_ball
        self.game.static_balls.add(self.game.shoot_ball) 
        
        #We check if there are any balls we can pop
        self.check_pop()
        
        #if the player has missed x number of times we make a shift of the board
        self.check_shift()
        
        if self.balls_are_in_out_of_bounds_zone():
            Board.END_GAME_SOUND.play()
            self.game.end_game = True
    
    
     
        

        

        
    


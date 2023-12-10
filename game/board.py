
from collections import deque


class Board(list):
    def __init__(self, *args):
        super().__init__(*args)
        self.rows, self.columns = len(self[0]), len(self)
        
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
             
    def get_valid_neighbours(self, position):
        r, c  = position
        left_right = ((r, c-1), (r,c+1))

        if r%2: # if row is odd:
            directions = ((r-1, c), (r-1, c+1), (r+1, c), (r+1, c+1))  # UP, UP-RIGHT, DOWN, DOWN_RIGHT
        else:
            directions = ((r-1, c), (r-1, c-1), (r+1,c-1), (r+1,c))   #UP, UP-LEFT, DOWN-LEFT, DOWN
        
        return [tup for tup in (directions + left_right) if self.in_bounds(tup)]

    def in_bounds(self, pos):
        return (0 <= pos[0] < 15 and 0 <= pos[1] < 15)

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
                x, y = ball.array_position
                ball.kill()
                self[x][y] = 0
            self.remove_disconnected_islands()
                                
    def update(self):

        r, c = self.game.shoot_ball.array_position
        self[r][c] = self.game.shoot_ball

        self.game.static_balls.add(self.game.shoot_ball) 
    
        self.check_pop()
        self.remove_disconnected_islands()

        self.game.generate_shooting_ball()
        
    


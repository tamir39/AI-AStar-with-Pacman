# Library
import pygame
import heapq
import copy
import itertools
from collections import deque

# Class Pacman
class Pacman:
    def __init__(self):
        self.position = None
        self.map = []
        self.goals = []
        self.actions = []

    def __str__(self):
        line = "Map:\n" + "\n".join("".join(row) for row in self.map)
        return line
    
    def print(self):
        print(str(self))
    
    def search(self):
        expanded = set()
        path = []
        relationship = {}
        frontier = []

        goal = None
        start = State(self.map, self.position, self.goals, 0, 0, None, [], self.preHeuristic())

        heapq.heappush(frontier, (start.f(), start))

        while frontier:
            _, state = heapq.heappop(frontier)
            
            if state in expanded: continue

            expanded.add(state)

            if not state.getGoals(): 
                goal = state
                break

            for next_state in state.getNextState():
                heapq.heappush(frontier, (next_state.f(), next_state))
                if next_state not in relationship:
                    relationship[next_state] = state

        review = goal
        while review in relationship:
            path.append(review)
            review = relationship[review]

        path.reverse()
        return path

    def bfs_distance(self, grid, start, goal):
        rows, cols = len(grid), len(grid[0])
        queue = deque([(start[0], start[1], 0, 0)])
        visited = set()
        visited.add((start[0], start[1], 0))
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        corners = {
            (1, 1): (rows - 2, cols - 2),
            (1, cols - 2): (rows - 2, 1),
            (rows - 2, 1): (1, cols - 2),
            (rows - 2, cols - 2): (1, 1)
        }
        
        while queue:
            x, y, step, power = queue.popleft()
            if (x, y) == goal:
                return step
            
            if (x, y) in corners:
                teleport_x, teleport_y = corners[(x, y)]
                queue.append((teleport_x, teleport_y, step + 1, max(power - 1, 0)))
                visited.add((teleport_x, teleport_y, max(power - 1, 0)))
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols:
                    if grid[nx][ny] != '%' or power > 0:
                        new_power = max(power - 1, 0) if grid[nx][ny] == '%' else power
                        if grid[nx][ny] == 'O':
                            new_power = 5
                        if (nx, ny, new_power) not in visited:
                            visited.add((nx, ny, new_power))
                            queue.append((nx, ny, step + 1, new_power))

    def heuristic_of_the_path(self, map, position, goals):
        if not goals:
            return 0
        
        total_cost = 0
        current_pos = position
        goals = set(goals)
        
        while goals:
            nearest_goal = min(goals, key=lambda g: self.bfs_distance(map, current_pos, g))
            cost = self.bfs_distance(map, current_pos, nearest_goal)
            if cost == 0:
                return 0
            total_cost += cost
            current_pos = nearest_goal
            goals.remove(nearest_goal)
        
        return total_cost

    def preHeuristic(self):
        pre_heuristic = {}
        goals = copy.deepcopy(self.goals)

        for g in goals:
            remaining_goals = [goal for goal in goals if goal != g]

            for i in range(1, len(remaining_goals) + 1):
                for each in itertools.combinations(remaining_goals, i):
                    formatted_each = tuple(each) if len(each) == 1 else each
                    pre_heuristic[(g, formatted_each)] = self.heuristic_of_the_path(self.map, g, list(each))

        return pre_heuristic
    
    def load_file(self, fileName):
        with open(fileName, "r") as f:
            self.map = [[char for char in line.rstrip()] for line in f]
        for i, row in enumerate(self.map):
            for j, char in enumerate(row):
                if char == 'P':
                    self.position = (i, j)
                elif char == '.':
                    self.goals.append((i, j))
                    
    def get_path(self):
        path = self.search()
        self.actions = [state.getAction() for state in path if state.getAction() != "Teleport"]
        return [each.position for each in path], [state.getAction() for state in path], len(self.actions)
    
    def output(self):
        return self.actions, len(self.actions)

# Class State
class State:
    def __init__(self, map, position, goals, step, power, action, explored, pre_heuristic):
        self.map = copy.deepcopy(map)
        self.goals = copy.deepcopy(goals)
        self.explored = copy.deepcopy(explored)
        self.pre_heuristic = copy.deepcopy(pre_heuristic)
        
        self.position = position
        self.step = step
        self.power = power
        self.action = action

        if self.position in self.goals:
            self.goals.remove(self.position)
            self.explored.clear()

    def __lt__(self, other):
        return self.f() < other.f()
    
    def getGoals(self):
        return self.goals
    
    def getAction(self):
        return self.action

    def getNextState(self):
        p = self.position
        m = self.map
        g = self.goals
        e = self.explored
        states = []
        num_rows = len(m)
        num_cols = len(m[0]) if num_rows > 0 else 0
        directions = [(-1, 0, "North"), (1, 0, "South"), (0, -1, "West"), (0, 1, "East")]

        if m[p[0]][p[1]] == "O":
                self.power = 5
                m[p[0]][p[1]] = " "

        if self.isCorner(p): 
            o_c = self.oppositeCorner(p)

            if len(e) > 0 and not self.isCorner(e[-1]):
                return [State(m, o_c, g, self.step, self.power, "Teleport", e + [p], self.pre_heuristic)]
            else:
                states.append(State(m, o_c, g, self.step + 1, max(self.power - 1, 0), "Stop", e + [p], self.pre_heuristic))

        if self.power > 0:
            for dx, dy, action in directions:
                neighbor = (p[0] + dx, p[1] + dy)
                if 1 <= neighbor[0] < num_rows - 1 and 1 <= neighbor[1] < num_cols - 1 and neighbor not in e:
                    states.append(State(m, neighbor, g, self.step + 1, self.power - 1, action, e + [p], self.pre_heuristic))
            return states

        for dx, dy, actions in directions:
            neighbor = (p[0] + dx, p[1] + dy)
            if m[neighbor[0]][neighbor[1]] != "%" and 1 <= neighbor[0] < num_rows - 1 and 1 <= neighbor[1] < num_cols - 1 and neighbor not in e:
                states.append(State(m, neighbor, g, self.step + 1, 0, actions, e + [p], self.pre_heuristic))

        return states

    def f(self):
        heuristic = self.heuristic()
        return self.step + heuristic
    
    def heuristic(self):
        h, goal = self.findNearestGoal()
        goals = tuple(g for g in self.goals if g != goal)
        
        heuristic = (h + self.pre_heuristic.get((goal, goals), 0))
        return heuristic

    def findNearestGoal(self):
        if not self.goals:
            return 0, None  

        p = self.position
        corners = [
            (1, 1),
            (1, len(self.map[0]) - 2),
            (len(self.map) - 2, 1),
            (len(self.map) - 2, len(self.map[0]) - 2)
        ]
        
        h1, goal1 = min((abs(p[0] - each[0]) + abs(p[1] - each[1]), each) for each in self.goals)

        teleport_options = []
        for c, opposite_c in zip(corners, reversed(corners)):
                h2, goal2 = min((abs(c[0] - p[0]) + abs(c[1] - p[1]) + abs(opposite_c[0] - each[0]) + abs(opposite_c[1] - each[1]), each) for each in self.goals)
                teleport_options.append((h2, goal2))

        h_min, goal_min = min([(h1, goal1)] + teleport_options, key=lambda x: x[0])

        return h_min, goal_min

    def isCorner(self, p):
        corners = [
            (1,1),
            (1, len(self.map[0])-2),
            (len(self.map)-2, 1),
            (len(self.map)-2, len(self.map[0])-2)
        ]
        return p in corners
    
    def oppositeCorner(self, p):
        opposite_corner = {
            (1,1) : (len(self.map)-2, len(self.map[0])-2),
            (1, len(self.map[0])-2) : (len(self.map)-2, 1),
            (len(self.map)-2, 1) : (1, len(self.map[0])-2),
            (len(self.map)-2, len(self.map[0])-2) : (1,1)
        }

        if p in opposite_corner:
            return opposite_corner[p]
        else: return False


#Load file
p = Pacman()
p.load_file("task02_pacman_example_map.txt")
path, actions, cost = p.get_path()
actions, total = p.output()
print(actions)
print(f"Total cost: {total}")


# Pygame
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1500, 800
CELL_SIZE = 35

ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
DARK_GRAY = (30, 30, 30)
WALL_COLOR = (25, 50, 112)
WALL_OUTLINE = (100, 149, 237)
PELLET_COLOR = (0, 255, 255)
POWER_COLOR = (255, 0, 255)
PACMAN_COLOR = (255, 204, 0)
EXPANDED_COLOR = (255, 99, 71)
PATH_COLOR = (50, 205, 50)
TEXT_COLOR = (200, 200, 200) 

pygame.display.set_caption("Pacman Astar")

pacman_pos = p.position
map = p.map
num_rows = len(map)
num_cols = len(map[0]) if num_rows > 0 else 0

map_width = num_cols * CELL_SIZE
map_height = num_rows * CELL_SIZE
offset_x = (SCREEN_WIDTH - map_width) // 2
offset_y = (SCREEN_HEIGHT - map_height) // 2
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
button_rect = pygame.Rect(offset_x + (map_width // 2) - (200 // 2), offset_y - 65, 200, 55)

start = False

def drawStartButton():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    button_color = (50, 220, 90) if button_rect.collidepoint((mouse_x, mouse_y)) else (34, 177, 76)

    pygame.draw.rect(screen, button_color, button_rect, border_radius=10)
    pygame.draw.rect(screen, (0, 255, 0) , button_rect, width=2, border_radius=10)

    text_surface = font.render("Start", True, (255, 255, 255))
    shadow_surface = font.render("Start", True, (0, 0, 0) )

    text_rect = text_surface.get_rect(center=button_rect.center)
    shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))

    screen.blit(shadow_surface, shadow_rect.topleft)
    screen.blit(text_surface, text_rect.topleft)

    pygame.display.update()

def drawObjects(pacman_pos):
    global start
    screen.fill(DARK_GRAY)

    for row_index, row in enumerate(p.map):
        for col_index, cell in enumerate(row):
            x = offset_x + col_index * CELL_SIZE
            y = offset_y + row_index * CELL_SIZE

            if cell == "%":
                pygame.draw.rect(screen, WALL_COLOR, (x, y, CELL_SIZE, CELL_SIZE), border_radius=5)
                pygame.draw.rect(screen, WALL_OUTLINE, (x+3, y+3, CELL_SIZE-6, CELL_SIZE-6), width=2, border_radius=5)

            elif cell == ".":
                pygame.draw.circle(screen, PELLET_COLOR, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 5)
                pygame.draw.circle(screen, (0, 255, 255, 50), (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 10)

            elif cell == "O":
                pygame.draw.circle(screen, POWER_COLOR, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 10)
                pygame.draw.circle(screen, (255, 0, 255, 80), (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 15) 

    p_x = offset_x + pacman_pos[1] * CELL_SIZE
    p_y = offset_y + pacman_pos[0] * CELL_SIZE
    pygame.draw.circle(screen, PACMAN_COLOR, (p_x + CELL_SIZE // 2, p_y + CELL_SIZE // 2), CELL_SIZE // 2 - 2)
    pygame.draw.circle(screen, (255, 204, 0, 100), (p_x + CELL_SIZE // 2, p_y + CELL_SIZE // 2), CELL_SIZE // 2)

    if not start: drawStartButton()

def movePacman(path, actions):
    for step, (row,col) in enumerate(path):
        p.position = (row, col)
        if p.map[row][col] != "%": p.map[row][col] = " "
        pygame.time.delay(200)
        
        drawObjects((row, col))
        drawActions(actions, step)
        
        pygame.display.update()
    pygame.time.delay(300)
pygame.font.init()
font = pygame.font.Font(None, 60)

def drawText(text, color, position):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(midbottom=position)

    glow_color = (min(color[0] + 50, 255), min(color[1] + 50, 255), min(color[2] + 50, 255))
    glow_surface = font.render(text, True, glow_color)
    glow_rect = glow_surface.get_rect(center=text_rect.center)
        
    screen.blit(glow_surface, glow_rect)

    screen.blit(text_surface, text_rect)
    pygame.display.update()

def drawActions(actions, step):
    neon_green = (0, 255, 127)
    if step < len(actions):
        action_text = f"Action: {actions[step]}" if actions[step] != "Teleport" else f"Teleport!"
        drawText(action_text, neon_green, (offset_x + map_width // 2, offset_y - 10))

def drawCost(cost):
    text_color = YELLOW
    cost_text = f"Finish! Total: {cost}"
    drawText(cost_text, text_color, (offset_x + map_width // 2, offset_y - 10))

running = True

while running:
    drawObjects(p.position)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not start:
            if button_rect.collidepoint(event.pos):
                start = True
    if start: break

if start:
    movePacman(path,actions)
    drawObjects(p.position)
    pygame.display.update()

drawObjects(p.position)
drawCost(cost)
pygame.time.wait(2000)
pygame.quit()



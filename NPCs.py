import pygame
import map
import sprites
import random
import entries
import hitboxes
import Notebook

villager_speed = 1
villagers = []

def nearest_path_tile(px, py):
    col, row = (px + 12) // 25, (py + 12) // 25
    for dc, dr in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]:
        nc, nr = col+dc, row+dr
        if map.grid[nr][nc] == 1:
            return (nc, nr)

def BFS(start_coords: tuple, end_coords: tuple):

    # convert pixel coords to nearest path tile
    start = nearest_path_tile(*start_coords)
    end = nearest_path_tile(*end_coords)

    queue = [start]
    came_from = {start: None}  # visited tiles and where they came from

    while queue != []:
        inspect = queue.pop(0)  # take from the front

        if inspect == end:
            # trace back through came_from to build the path
            path = []
            while came_from[inspect] != None:
                addition = came_from[inspect][0] * 25 +13, came_from[inspect][1] * 25 +13
                path.append(addition)
                inspect = came_from[inspect]
            return path

        local_tiles = [(inspect[0] + 1, inspect[1]),
                       (inspect[0] - 1, inspect[1]),
                       (inspect[0], inspect[1]+ 1),
                       (inspect[0], inspect[1] - 1)
                        ]
        for tile in local_tiles:
            if map.grid[tile[1]][tile[0]] != 1 or tile in came_from:
                continue
            tile_rect = pygame.Rect(tile[0] * 25 + 1, tile[1] * 25 + 1, 23, 23)
            if any(tile_rect.colliderect(wall) for wall in hitboxes.walls):
                continue
            came_from[tile] = inspect
            queue.append(tile)

    return None



class Villager:
    def __init__(self, start_building: str, idle_spritesheet, walking_spritesheet, dimensions: tuple):
        #animation stuff
        self.direction = 'down'
        self.frame = 0    #pointer
        self.frame_counter = 0     #counter
        self.current_image = None
        self.idle_sprite_sheet = pygame.image.load(f'img/sprites/{idle_spritesheet}.png')
        self.walking_sprite_sheet = pygame.image.load(f'img/sprites/{walking_spritesheet}.png')

        #movement stuff
        self.start_building = start_building
        self.x, self.y = entries.building_entries[start_building]     #fetch the coordinates of the start buiding's door
        self.end_point = random.choice(stop_spots)    #choose random stop spot
        self.hitbox = pygame.Rect(self.x, self.y, 20, 20)


        #print(map.grid[self.y // 25][self.x // 25])  #debugging start position
        self.at_home = True
        self.arrived = False
        self.is_tapping_foot = False
        self.wait_timer = None
        self.wait_length = 600

        self.make_sheets()
        self.route = BFS((self.x, self.y), self.end_point[0])


        villagers.append(self)

    def find_route(self):
        if self.arrived:
            x = self.end_point
            self.end_point = random.choice(stop_spots)
            stop_spots.append(x)
        else:
            self.end_point = random.choice(stop_spots)
        stop_spots.remove(self.end_point)

        self.route = BFS((self.x, self.y), self.end_point[0])  # find the applicable path
        self.arrived = False

    def walk_to_destination(self, screen, notebook_open):
        if not notebook_open:
            if self.is_tapping_foot:
              self.wait_timer += 1
              if self.wait_timer > self.wait_length:
                  self.wait_timer = None
                  self.is_tapping_foot = False

            elif self.route != []:
                target = self.route[-1]
                relative_positon = target[0] - self.x, target[1] - self.y

                # snap to node on path when close enough (may look weird)
                if self.x > target[0] - villager_speed and self.x < target[0] + villager_speed and self.y > target[1] - villager_speed and self.y < target[1] + villager_speed:
                    self.x = target[0]
                    self.y = target[1]
                    self.route.remove(self.route[-1])

                # adjust x coord
                elif relative_positon[0] > 0:
                    self.x += villager_speed
                    self.direction = 'right'
                elif relative_positon[0] < 0:
                    self.x -= villager_speed
                    self.direction = 'left'

                # adjust y coord
                if relative_positon[1] > 0:
                    self.y += villager_speed
                    self.direction = 'down'
                elif relative_positon[1] < 0:
                    self.y -= villager_speed
                    self.direction = 'up'

            self.frame_counter = (self.frame_counter + 1) % (10 * 4)  # Adjust 15 for speed
            if self.frame_counter % 10 == 0:
                self.frame = (self.frame + 1) % 4

        self.choose_image()

        #pygame.draw.rect(screen, (255, 255, 0), (self.x, self.y, 10, 10))       #print yellow rectangles instead of sprite images
        screen.blit(self.current_image,(self.x - 13, self.y - 30))       #print sprite images
        if self.route == []:
            self.arrived = True
            self.wait_timer = 0
            self.is_tapping_foot = True

    def show_path(self):      # for debugging
        print(f'route: {self.start_building} -> {self.end_point[2]}')
        print(self.route)

    def choose_image(self):
        if self.is_tapping_foot:        #if idle
            if self.end_point[1] == 'up':
                self.direction = 'up'
                self.current_image = self.up_idle[self.frame]
            elif self.end_point[1] == 'down':
                self.direction = 'down'
                self.current_image = self.down_idle[self.frame]
            elif self.end_point[1] == 'left':
                self.direction = 'left'
                self.current_image = self.left_idle[self.frame]
            elif self.end_point[1] == 'right':
                self.direction = 'right'
                self.current_image = self.right_idle[self.frame]

        else:                           #if walking
            if self.direction == 'up':
                self.current_image = self.up_run[self.frame]
            elif self.direction == 'down':
                self.current_image = self.down_run[self.frame]
            elif self.direction == 'left':
                self.current_image = self.left_run[self.frame]
            elif self.direction == 'right':
                self.current_image = self.right_run[self.frame]

    def make_sheets(self):
        self.down_run = sprites.take_row(0, 'walking', (311, 601))
        self.up_run = sprites.take_row(1, 'walking', (311, 601))
        self.left_run = sprites.take_row(2, 'walking', (311, 601))
        self.right_run = sprites.take_row(3, 'walking', (311, 601))

        self.down_idle = sprites.take_row(0, 'idle', (316, 643))
        self.up_idle = sprites.take_row(1, 'idle', (316, 643))
        self.left_idle = sprites.take_row(2, 'idle', (316, 643))
        self.right_idle = sprites.take_row(3, 'idle', (316, 643))


stop_spots = [  #format: [coords, direction]
    [(286,345),'up', 'bridge'],# on the bridge
    [(103,309),'down', 'gate'],# under the gate
    [(560,369),'right', 'pond'],# by the pond
    [(885,300),'down', 'bell tower'],# by the bell tower
    #[(283,594),'up', 'fish box'],# by the fish box                     ERROR
    #[(364,582),'down', 'fish shop'],# by the fish shop                ERROR
    #[(481,591),'up', 'main shop'],# by the main shop                ERROR
    [(5* 25, 26* 25),'down', 'bottom corner'],# by the bottom corner
    [(1198,490),'down', 'dojo'],# by the dojo
    [(625,576),'right', 'tree']# by the tree
]

def show_positions(screen, frame):
    for item in stop_spots:
        if item[1] == 'up':
            current_image = sprites.up_idle[frame]
        elif item[1] == 'down':
            current_image = sprites.down_idle[frame]
        elif item[1] == 'left':
            current_image = sprites.left_idle[frame]
        elif item[1] == 'right':
            current_image = sprites.right_idle[frame]
            
        screen.blit(current_image, (item[0][0], item[0][1]))

def update(screen, notebook_open):
    for character in villagers:
        if character.route == []:
            character.find_route()
        else:
            character.walk_to_destination(screen, notebook_open)


#villager instantiations  (needs tidying up)
Arthur = Villager('bell tower', 'sprite_idle_sheet','sprite_walking_sheet', (27,48))
Dean = Villager('dojo', 'sprite_idle_sheet','sprite_walking_sheet', (27,48))
James = Villager('tall palace', 'sprite_idle_sheet','sprite_walking_sheet', (27,48))
Rowan = Villager('tall house', 'sprite_idle_sheet','sprite_walking_sheet', (27,48))
#Villagerno5 = Villager('food shop', 'sprite_idle_sheet','sprite_walking_sheet', (27,48))
#Villagerno6 = Villager('shop', 'sprite_idle_sheet','sprite_walking_sheet', (27,48))
Lemonie = Villager('big house', 'sprite_idle_sheet','sprite_walking_sheet', (27,48))
Olex = Villager('square house', 'sprite_idle_sheet','sprite_walking_sheet', (27,48))





#NPCs = ['Arthur','Dean','James','Rowan','Lemonie','Olex']
def show_villager_hitboxes(screen):
    #for NPC in NPCs:
    screen.blit(NPC.hitbox)














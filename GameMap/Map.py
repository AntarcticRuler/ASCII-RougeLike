import libtcodpy as tcod
from random import randint, choice

from GameMap.tile import Tile
from GameMap.shapes import Rect, Circle
from Entities.entity import Entity

from components import classes
from components import enemyAI

from renderer import RenderOrder

from Entities.items import *
from Entities.enemies import *

class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    # Initializes the tiles variable
    def initialize_tiles(self):
        tiles = [[Tile(True, x, y) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def copy_tiles(self, oldTiles):
        tiles = [[Tile(oldTiles[x][y].blocked, x, y) for y in range(self.height)] for x in range(self.width)]
        return tiles

    # Generates the map
    def generate(self, player, entities, rooms=[], max_monsters_per_room=3, max_items_per_room=2, room_max_size=10, room_min_size = 5, max_rooms = 75, num_rooms = 0, maxIterations = 800, iterations = 0):
        print (num_rooms)

        if (num_rooms == max_rooms):
            return
        elif iterations == maxIterations:
            return

        # random width and height
        # if (iterations > 2/3 * maxIterations):
        #     w = randint(int (room_min_size * 1/2), int (room_max_size * 1/2))
        #     h = randint(int (room_min_size * 1/2), int (room_max_size * 1/2))
        #     r = int((w + h) / 3)
        if (iterations > 2/3 * maxIterations):
            w = randint(int (room_min_size * 2/3), int (room_max_size * 2/3))
            h = randint(int (room_min_size * 2/3), int (room_max_size * 2/3))
            r = int((w + h) / 2.5)
        else:
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            r = int((w + h) / 2.2)

        print (iterations)

        # "Rect" class makes rectangles easier to work with
        if randint(0, 100) < 50:
            (x, y) = self.getXY_Rect(w, h)
            new_room = Rect(x, y, w, h)
        else:
            (x, y) = self.getXY_Circle(r)
            new_room = Circle(x, y, r)

        # run through the other rooms and see if they intersect with this one
        for other_room in rooms:
            if new_room.intersect(other_room):
                return self.generate (player, entities, rooms=rooms, max_monsters_per_room=3, room_max_size=10, room_min_size = 5, max_rooms = max_rooms, num_rooms=num_rooms, iterations = iterations + 1)
        else:
            # this means there are no intersections, so this room is valid

            # "paint" it to the map's tiles
            self.create_room(new_room)

            # center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                # this is the first room, where the player starts at
                player.x = new_x
                player.y = new_y

            # Places entities in the room
            self.place_entities(new_room, entities, max_monsters_per_room, max_items_per_room)

            # finally, append the new room to the list
            rooms.append(new_room)
            self.create_room (new_room)

            return self.generate (player, entities, rooms=rooms, max_monsters_per_room=3, room_max_size=10, room_min_size = 5, max_rooms = max_rooms, num_rooms=num_rooms + 1, iterations = iterations + 1)

    def create_room(self, room):
        # go through the tiles in the rectangle and make them passable
        print (room.type)

        doors = room.door()
        try:
            for door in doors:
                door_x, door_y = door
                self.tiles[door_x][door_y].door = True
        except:
            pass

        if (room.type == 'Rect'):
            for x in range(room.x1 + 1, room.x2):
                for y in range(room.y1 + 1, room.y2):
                    self.tiles[x][y].blocked = False
                    self.tiles[x][y].block_sight = False
        elif (room.type == 'Circle'):
            for coord in room.coords:
                self.tiles[coord[0]][coord[1]].blocked = False
                self.tiles[coord[0]][coord[1]].block_sight = False

    def getXY_Rect (self, w, h):
        x = randint(w, self.width - w - 1)
        y = randint(h, self.height - h - 1)
        if not self.is_blocked(x, y):
            return self.getXY_Rect(w, h)
        else:
            return (x, y)

    def getXY_Circle (self, r):
        x = randint(r, self.width - r - 1)
        y = randint(r, self.height - r - 1)
        if not self.is_blocked(x, y):
            return self.getXY_Circle(r)
        else:
            return (x, y)

    # Generates out of room tunnels
    def genMainTunnels (self):
        newTiles = self.copy_tiles (self.tiles)
        for tileList in self.tiles:
            for tile in tileList:
                if tile.blocked:
                    if not self.on_exterior(tile) and self.intersect_room(newTiles, tile):
                        tile.blocked = False
                        tile.block_sight = False

    # Generates the doors on the map
    def genDoors (self):
        for tileList in self.tiles:
            for tile in tileList:
                if (tile.door):
                    tile.blocked = False
                    tile.block_sight = False

    # Does the tile intersect a room?
    def intersect_room (self, tiles, tile):
        return tiles[tile.x + 1][tile.y].blocked and tiles[tile.x - 1][tile.y].blocked and tiles[tile.x][tile.y + 1].blocked and tiles[tile.x][tile.y - 1].blocked and tiles[tile.x - 1][tile.y - 1].blocked and tiles[tile.x + 1][tile.y + 1].blocked and tiles[tile.x + 1][tile.y - 1].blocked and tiles[tile.x - 1][tile.y + 1].blocked

    # Does the tile fall on the exterior of the map?
    def on_exterior (self, tile):
        return tile.x <= 1 or tile.x >= self.width - 1 or tile.y <= 1 or tile.y >= self.height - 1

    # Places all entites on the map
    def place_entities(self, room, entities, max_monsters_per_room, max_items_per_room):
        # Get a random number of monsters
        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)

        for i in range(number_of_monsters):
            # Choose a random location in the room
            if (room.type == 'Rect'):
                x = randint(room.x1 + 1, room.x2 - 1)
                y = randint(room.y1 + 1, room.y2 - 1)
            elif (room.type == 'Circle'):
                x, y = choice (room.coords)

            player = entities[0]

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                if randint(0, 100) < 80:
                    monster = Orc(x, y, target=player).get()
                else:
                    monster = Troll(x, y, target=player).get()

                entities.append(monster)
            
        for i in range(number_of_items):
            if (room.type == 'Rect'):
                x = randint(room.x1 + 1, room.x2 - 1)
                y = randint(room.y1 + 1, room.y2 - 1)
            elif (room.type == 'Circle'):
                x, y = choice (room.coords)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                entities.append(HealingPotion(x, y).get())
    
    def get_blocking_entities_at_location(self, entities, destination_x, destination_y):
        for entity in entities:
            if entity.blocks and entity.x == destination_x and entity.y == destination_y:
                return entity

        return None

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False
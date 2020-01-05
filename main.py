# http://rogueliketutorials.com/tutorials/tcod/part-1/

import libtcodpy as tcod
import tcod.event as event
from tcod import Key
from random import randint

from threading import Thread

from Entities.entity import Entity
from GameMap.Map import GameMap
from GameMap.FOV import initialize_fov, recompute_fov
from game_states import GameStates
from components import classes
from components.death_functions import kill_monster, kill_player
from renderer import *
from message_log import MessageLog, Message

from time import sleep

from components.inventory import Inventory

FRAME_RATE = 20

SCREEN_WIDTH = 80
R_PANEL_WIDTH = 26

SCREEN_HEIGHT = 50
PANEL_HEIGHT = 10

player_x = int(SCREEN_WIDTH / 2)
player_y = int(SCREEN_HEIGHT / 2)

font_flags = tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD
tcod.console_set_custom_font("./assets/arial12x12.png", font_flags)

player = Entity(player_x, player_y, '@', tcod.black, 'Player', blocks=True, inventory=Inventory(20), renderOrder=RenderOrder.ACTOR, _class=classes.Fighter(30, 5, 10))

entities = [player]

game_map = GameMap(SCREEN_WIDTH, SCREEN_HEIGHT)
game_map.generate(player, entities, max_monsters_per_room=3, room_max_size = 12, room_min_size = 6, max_rooms = 75)
game_map.genMainTunnels()
game_map.genDoors()

fov_algorithm = 0
fov_light_walls = True
fov_radius = 10
fov_recompute = True

message_log = MessageLog(22, SCREEN_WIDTH - 22, PANEL_HEIGHT)

fov_map = initialize_fov(game_map)

game_state = GameStates.PLAYERS_TURN

colors = {
        'dark_wall': tcod.Color(2, 2, 2),
        'dark_ground': tcod.Color(50, 50, 50),
        'light_wall': tcod.Color(120, 120, 120),
        'light_ground': tcod.Color(200, 200, 200),
        'black': tcod.Color(200, 200, 200)
    }

def main ():
    with tcod.console_init_root(SCREEN_WIDTH + R_PANEL_WIDTH, SCREEN_HEIGHT + PANEL_HEIGHT, order="F") as root_console:
        renderThread = Thread(target=render, args=(root_console ,))
        renderThread.start()
        while True:
            update (root_console)        
            for events in event.wait():
                if events.type == "QUIT":
                    renderThread.join()
                    renderThread.exit()
                    raise SystemExit()
                    exit()

def update (console):
    global player_x, player_y, entities, game_state

    clear_all(console, entities)

    event.KeyDown(event.SCANCODE_UP, event.K_UP, event.KMOD_NONE)

    key = tcod.console_wait_for_keypress(True).vk

    action = keyHandler(key)

    if action.get('fullscreen'):
        tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

    print (game_state)

    if game_state == GameStates.PLAYERS_TURN:
        playerTurn(action, console)

    # Loops through all the entities and runs their AI if they have one
    elif game_state == GameStates.ENEMY_TURN:
        enemyTurn(action, console)

def enemyTurn (action, console):
    global game_state

    for entity in entities:
        if entity.ai:
            enemy_turn_results = entity.ai.take_turn(fov_map, game_map, entities)

            # Runs through the turn_result commands
            for turn_result in enemy_turn_results:
                if turn_result.get('message'):
                    message_log.add_message (turn_result.get('message'))

                if turn_result.get('dead'):
                    dead_entity = turn_result.get('dead')
                    if dead_entity == player:
                        message, game_state = kill_player(dead_entity)
                    else:
                        message = kill_monster(dead_entity)

                    message_log.add_message(message)
    
    endEnemyTurn()

# The players turn
def playerTurn (action, console):
    global game_state
    
    player_turn_results = []

    # IF PICKING UP ITEM
    if action.get('pickup'):
        for entity in entities:
            if entity.item and entity.x == player.x and entity.y == player.y:
                pickup_results = player.inventory.add_item(entity)
                player_turn_results.extend(pickup_results)
                break
        else:
            message_log.add_message(Message('There is nothing here to pick up.', tcod.yellow))

    # Player has chosen to move
    if action.get('move'):
        tcod.console_put_char(console, player_x, player_y, event.K_PERIOD, tcod.BKGND_DEFAULT)

        dx, dy = action.get('move')

        destination_x = player.x + dx
        destination_y = player.y + dy

        if not game_map.is_blocked(destination_x, destination_y):
                target = game_map.get_blocking_entities_at_location(entities, destination_x, destination_y)
                    
                if target:
                    attack_results = player._class.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)

                    fov_recompute = True

        endPlayerTurn()
    else:
        fov_recompute = False

    # Runs through the turn_result commands
    for turn_result in player_turn_results:
        if turn_result.get('message'):
            message_log.add_message(turn_result.get('message'))
            
        if turn_result.get('dead'):
            dead_entity = turn_result.get('dead')
            if dead_entity == player:
                message, game_state = kill_player(dead_entity)
            else:
                message = kill_monster(dead_entity)

            message_log.add_message(message)

            if game_state == GameStates.PLAYER_DEAD:
                break
        
        if turn_result.get ('item_added'):
            entities.remove(turn_result.get ('item_added'))

        if game_state == GameStates.PLAYER_DEAD:
            break

def endPlayerTurn ():
    global game_state
    message_log.add_message(Message("Enemy Turn", tcod.white))
    game_state = GameStates.ENEMY_TURN

def endEnemyTurn ():
    global game_state
    message_log.add_message(Message("Player Turn", tcod.white))
    game_state = GameStates.PLAYERS_TURN

def keyHandler(key):

    if key == tcod.KEY_UP:
        return {'move': (0, -1)}
    elif key == tcod.KEY_DOWN:
        return {'move': (0, 1)}
    elif key == tcod.KEY_LEFT:
        return {'move': (-1, 0)}
    elif key == tcod.KEY_RIGHT:
        return {'move': (1, 0)}

    # PLAYER ENTERS G
    if key == 65:
        return {'pickup': True}

    if key == tcod.KEY_ENTER and tcod.KEY_ALT:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    return {}

# The render function called every frame
def render (console):
    global entities, player, fov_recompute

    while (True):
        # Refreshes the screen
        tcod.console_set_default_background(console, tcod.black)
        tcod.console_clear(console)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        render_all(console, entities, player, game_map, fov_map, fov_recompute, SCREEN_WIDTH, SCREEN_HEIGHT, colors)

        tcod.console_set_default_background(console, tcod.black)
        renderBottomPanel(console, message_log, player)
        renderSidePanel(console, entities, fov_map)

        tcod.console_flush()

        tcod.console_blit(console, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

        sleep (1/FRAME_RATE)


if __name__ == '__main__':
    main()
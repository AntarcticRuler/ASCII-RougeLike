import libtcodpy as tcod

from enum import Enum

SCREEN_WIDTH = 80
R_PANEL_WIDTH = 26

SCREEN_HEIGHT = 50
PANEL_HEIGHT = 10

class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3

# Renders all entities in the visible area
def render_all(con, entities, player, game_map, fov_map, fov_recompute, screen_width, screen_height, colors):
    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = tcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        tcod.console_set_char_background(con, x, y, colors.get('light_wall'), tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(con, x, y, colors.get('light_ground'), tcod.BKGND_SET)
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    if wall:
                        tcod.console_set_char_background(con, x, y, colors.get('dark_wall'), tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(con, x, y, colors.get('dark_ground'), tcod.BKGND_SET)

    # Draw all entities in the list
    entities_in_render_order = sorted(entities, key=lambda x: x.renderOrder.value)

    for entity in entities_in_render_order:
        draw_entity(con, entity, fov_map)

    tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

def renderBottomPanel (console, message_log, player):
    y_zero = SCREEN_HEIGHT + 1

    render_bar(console, 1, y_zero + 1, 20, 'HP', player._class.hp, player._class.max_hp,
               tcod.light_red, tcod.darker_red)

    render_bar(console, 1, y_zero + 2, 20, 'MANA', player._class.hp, player._class.max_hp,
               tcod.blue, tcod.darker_azure)

    # Print the game messages, one line at a time
    y = y_zero + 1
    for message in message_log.messages:
        tcod.console_set_default_foreground(console, message.color)
        tcod.console_print_ex(console, message_log.x, y, tcod.BKGND_NONE, tcod.LEFT, message.text)
        y += 1

def renderSidePanel (console, entities, fov_map):
    mouse = tcod.mouse_get_status()

    x_zero = SCREEN_WIDTH + 1
    entitiesHighlighted = get_entity_under_mouse(mouse, entities, fov_map)

    if (entitiesHighlighted):
        for entity in entitiesHighlighted:
            # Prints name of entity
            tcod.console_set_default_background(console, tcod.white)
            tcod.console_print_ex(console, x_zero + 1, 1, tcod.BKGND_NONE, tcod.LEFT, entity.name)

            # Prints health bar of entity
            if (entity.ai):
                render_bar(console, x_zero + 1, 3, 20, 'HP', entity._class.hp, entity._class.max_hp,
                        tcod.light_red, tcod.darker_red)

# Renders a bar for health/stamina/mana
def render_bar(console, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    tcod.console_set_default_background(console, back_color)
    tcod.console_rect(console, x, y, total_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_background(console, bar_color)
    if bar_width > 0:
        tcod.console_rect(console, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_background(console, tcod.black)
    tcod.console_print_ex(console, int(x + total_width / 2), y, tcod.BKGND_NONE, tcod.CENTER,
                             '{0}: {1}/{2}'.format(name, value, maximum))

def get_entity_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)

    entitiesHighlighted = [entity for entity in entities
            if entity.x == x and entity.y == y and tcod.map_is_in_fov(fov_map, entity.x, entity.y)]

    return entitiesHighlighted

# Clears all entities off the screen
def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)

# Draws all entities in the entity array
def draw_entity(con, entity, fov_map):
    if tcod.map_is_in_fov(fov_map, entity.x, entity.y):
        tcod.console_set_default_foreground(con, entity.color)
        tcod.console_put_char(con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)

def clear_entity(con, entity):
    # erase the character that represents this object
    tcod.console_put_char(con, entity.x, entity.y, ' ', tcod.BKGND_NONE)
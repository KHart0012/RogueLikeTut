import tcod
from enum import Enum

class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3

def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, screen_width, screen_height, 
                bar_width, panel_height, panel_y, colors):
    # Draw all tiles in the game map
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

    # Draws all entities in the list
    entities_in_order = sorted(entities, key=lambda x: x.render_order.value)
    for entity in entities_in_order:
        draw_entity(con, entity, fov_map)
    
    tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    tcod.console_set_default_background(panel, tcod.black)
    tcod.console_clear(panel)

    render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.figher.max_hp,
                tcod.light_red, tcod.darker_red)

    tcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)
    tcod.console_set_default_background(panel, back_color)
    tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)
    tcod.console_set_default_foreground(panel, tcod.white)
    tcod.console_print_ex(panel, int(x + total_width / 2), y, tcod.BKGND_NONE, tcod.CENTER,
                        '{0}: {1}/{2}'.format(name, value, maximum))

def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)

def draw_entity(con, entity, fov_map):
    if tcod.map_is_in_fov(fov_map, entity.x, entity.y):
        tcod.console_set_default_foreground(con, entity.color)
        tcod.console_put_char(con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)

def clear_entity(con, entity):
    tcod.console_put_char(con, entity.x, entity.y, ' ', tcod.BKGND_NONE)
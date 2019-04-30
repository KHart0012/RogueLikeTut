import tcod

from game_states import GameStates

def handle_keys(key, game_state):
    if game_state == GameStates.PLAYER_TURN:
        return handle_player_turn_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_player_inventory_keys(key)
    return {}

def handle_player_turn_keys(key):
    key_char = chr(key.c)

    # Movement Keys
    if key.vk == tcod.KEY_UP or key_char == 'k':
        return {'move': (0, -1)}
    elif key.vk == tcod.KEY_DOWN or key_char == 'j':
        return {'move': (0, 1)}
    elif key.vk == tcod.KEY_LEFT or key_char == 'h':
        return {'move': (-1, 0)}
    elif key.vk == tcod.KEY_RIGHT or key_char == 'l':
        return {'move': (1, 0)}
    elif key_char == 'y':
        return {'move': (-1, -1)}
    elif key_char == 'u':
        return {'move': (1, -1)}
    elif key_char == 'b':
        return {'move': (-1, 1)}
    elif key_char == 'n':
        return {'move': (1, 1)}

    # Pickup items
    if key_char == 'g':
        return {'pickup': True}

    # Show Inventory
    if key_char == 'i':
        return {'show_inventory': True}

    # Drop items
    if key_char == 'd':
        return {'drop_inventory': True}
    
    # Alt+Enter: toggle full screen
    if key.vk == tcod.KEY_ENTER and key.lalt:
        return {'fullscreen': True}

    # Exit the game
    elif key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}

    # No key was pressed
    return {}

def handle_player_dead_keys(key):
    key_char = chr(key.c)

    # Show Inventory
    if key_char == 'i':
        return {'show_inventory': True}
    
    # Alt+Enter: toggle full screen
    if key.vk == tcod.KEY_ENTER and key.lalt:
        return {'fullscreen': True}

    # Exit the game
    elif key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}

def handle_player_inventory_keys(key):
    index = key.c - ord('a')
    
    # Selects item in inventory
    if index >= 0:
        return {'inventory_index': index}
    
    # Alt+Enter: toggle full screen
    if key.vk == tcod.KEY_ENTER and key.lalt:
        return {'fullscreen': True}

    # Exit the menu
    elif key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}
    
    return {}

def handle_targeting_keys(key):
    # Exit the menu
    if key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}
    
    return {}

def handle_mouse(mouse):
    (x, y) = (mouse.cx, mouse.cy)
    
    if mouse.lbutton_pressed:
        return {'left_click': (x, y)}
    elif mouse.rbutton_pressed:
        return {'right_click': (x, y)}

    return {}
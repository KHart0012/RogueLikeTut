import tcod

def menu(con, header, options, width, screen_width, screen_height):
    if len(options) > 26: 
        raise ValueError('Cannot have a menu with more than 26 options.')
    
    header_height = tcod.console_get_height_rect(con, 0, 0, width, screen_height, header)
    height = len(options) + header_height

    window = tcod.console_new(width, height)

    tcod.console_set_default_foreground(window, tcod.white)
    tcod.console_print_rect_ex(window, 0, 0, width, height, tcod.BKGND_NONE, tcod.LEFT, header)

    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        tcod.console_print_ex(window, 0, y, tcod.BKGND_NONE, tcod.LEFT, text)
        y += 1
        letter_index += 1

    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    tcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

def inventory_menu(con, header, inventory, inventory_width, screen_width, screen_height):
    if len(inventory.items) == 0:
        options = ['Inventory is empty']
    else:
        options = [item.name for item in inventory.items]
    
    menu(con, header, options, inventory_width, screen_width, screen_height)

def main_menu(con, screen_width, screen_height):
    tcod.console_set_default_foreground(0, tcod.light_yellow)
    tcod.console_print_ex(0, int(screen_width / 2), int(screen_height / 2) - 4, tcod.BKGND_NONE,
                         tcod.CENTER, 'SCOLTON')
    tcod.console_print_ex(0, int(screen_width / 2), int(screen_height / 2) - 2, tcod.BKGND_NONE,
                         tcod.CENTER, 'CREATED BY: KEVIN HART')
    menu(con, '', ['New Game', 'Continue', 'Quit'], 24, screen_width, screen_height)

def message_box(con, header, width, screen_width, screen_height):
    menu(con, header, [], width, screen_width, screen_height)
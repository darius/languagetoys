"""
ANSI terminal control
"""

prefix = '\x1b['

home            = prefix + 'H'
clear_to_bottom = prefix + 'J'
clear_screen    = prefix + '2J' + home
clear_to_eol    = prefix + 'K'

def goto(x, y):
    return prefix + ('%d;%dH' % (y, x))

black, red, green, yellow, blue, magenta, cyan, white = range(8)

def bright(color):
    return 60 + color

def set_foreground(color):
    return (prefix + '%dm') % (30 + color)

def set_background(color):
    return (prefix + '%dm') % (40 + color)

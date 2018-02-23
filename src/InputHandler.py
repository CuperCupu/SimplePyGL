from OpenGL.GLUT import *

# Keyboard handler
_pressed_key = {}

def key_up(key, x, y):
    '''Called when a keyboard key is released.'''
    _pressed_key[key] = False

def key_down(key, x, y):
    '''Called when a keyboard key is pressed.'''
    _pressed_key[key] = True

def is_key_down(key):
    '''Returns true if the key is pressed; otherwise false.'''
    return key in _pressed_key and _pressed_key[key]

def is_key_up(key):
    '''Returns false if the key is pressed; otherwise true.'''
    return not is_key_down(key)

def initialize_keyboard():
    '''Initialize keyboard event listener to GLUT.'''
    glutKeyboardFunc(key_down)
    glutKeyboardUpFunc(key_up)

# Mouse Handler
_pressed_mouse = {}
_mouse_position = (0, 0)

def get_mouse_position():
    return _mouse_position

def get_mouse_x():
    return _mouse_position[0]

def get_mouse_y():
    return _mouse_position[1]

def mouse(key, state, x, y):
    '''Called as mouse action callback from GLUT.'''
    _pressed_mouse[key] = False if state else True
    global _mouse_position
    _mouse_position = (x, y)

def mouse_active_drag(x, y):
    '''Called when the mouse is moved while being pressed.'''
    global _mouse_position
    _mouse_position = (x, y)

def mouse_passive_drag(x, y):
    '''Called when the mouse is moved while no button is being pressed.'''
    global _mouse_position
    _mouse_position = (x, y)

def is_mouse_down(button):
    '''Returns true if the button is pressed; otherwise false'''
    return button in _pressed_mouse and _pressed_mouse[button]

def is_mouse_up(button):
    '''Returns false if the button is pressed; otherwise true'''
    return not is_mouse_down(button)

def initialize_mouse():
    '''Initialize mouse event listener to GLUT.'''
    glutMouseFunc(mouse)
    glutMotionFunc(mouse_active_drag)
    glutPassiveMotionFunc(mouse_passive_drag)
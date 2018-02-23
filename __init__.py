#!usr/bin/env python3
# -*- coding:utf-8 -*-
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import threading
import sys
import time
import signal
from GLHelper.glHelper import *
import GLHelper.builder
import GLHelper.glutHelper

# Global variables.
# List of renderable to render.
to_render = []
# List of transformation.
transformation = []
# List of all animators thread.
animators = []
# The default position of the camera.
DEFAULT_CAMERA_POSITION = (0, 0, -100)
# The default orientation of the camera.
DEFAULT_CAMERA_ROTATION = (0, 0, 0)

selection = -1

clearColor = (1.0,1.0,1.0,1.0)

prerender = None 
postrender = None
inputhandler = None

title = b''
running = True
width, height = 600, 600
# Settings.
FOV, ASPECT_RATIO, NEAR, FAR = 60.0, width / height, 1.0, 2000.0

# Set up camera
camera = glutHelper.Camera(DEFAULT_CAMERA_POSITION, DEFAULT_CAMERA_ROTATION)
camera_controller = None


def main(argv):
    global title, running
    global width, height
    global FOV, ASPECT_RATIO, NEAR, FAR
    global inputhandler
    FOV, ASPECT_RATIO, NEAR, FAR = 60.0, width / height, 1.0, 2000.0
    
    # Initialize window.
    glutInit(argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    windowid = glutCreateWindow(title)
        
    def handlesignal(signo, frame):
        # Called when termination signal is received.
        global running
        running = False

    signal.signal(signal.SIGINT, handlesignal)
    signal.signal(signal.SIGTERM, handlesignal)

    def exitprog():
        # Exit from the program.
        for animator in animators:
            animator.stop()
        signal.alarm(1)
        if camera_controller:
            camera_controller.stop_listening()
        glutDestroyWindow(windowid)
        sys.exit(0)

    def resize(w, h):
        # Reset the settings.
        global ASPECT_RATIO, width, height
        width = w
        height = h
        ASPECT_RATIO = w / h
        glViewport(0, 0, w, h)
        
    def idle():
        global offset, running
        if running:
            glutPostRedisplay()
        else:
            exitprog()

    def render():
        global camera
        global FOV, ASPECT_RATIO, NEAR, FAR
        global prerender, postrender
        try:
            # Set matrix mode
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(FOV, ASPECT_RATIO, NEAR, FAR)
            glMatrixMode(GL_MODELVIEW)
            # Clear the window
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            # Reset Camera
            glPushMatrix()
            glMultMatrixf(camera.matrix.c_values())
            if prerender:
                prerender()
            # Render all renderables
            glPushMatrix()
            for matrix in transformation:
                if isinstance(matrix, TransformationMatrix):
                    glMultMatrixf(matrix.c_values())
            for obj in to_render:
                obj.render()
            glPopMatrix()
            if postrender:
                postrender()
            glPopMatrix()
            glutSwapBuffers()
        except Exception as e:
            running = False
            print(e)
            exitprog()

    # Initialize renderer
    glClearColor(*clearColor)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # Set binding
    glutDisplayFunc(render)
    glutReshapeFunc(resize)
    glutHelper.initialize_keyboard()
    glutHelper.initialize_mouse()
    glutIdleFunc(idle)
    # Initialize keyboard input handler
    inputThread = threading.Thread(None, inputhandler)
    inputThread.start()
    if camera_controller:
        camera_controller.start()
    # Run the main loop
    glutMainLoop()
    # No hope of ever reaching here


'''Help string
A section is typed as dict.
Each subsection can be either str or dict notating the nested subsection.
'''
HELP_DOC_STRING = {}

def doc_get(section, *subnames):
    '''Get the help doc string of a specific section and name.
    Args:
        section (str): the name of the section to get.
        args (*): nested name of the subsection.
    '''
    global HELP_DOC_STRING
    retval = None
    if section not in HELP_DOC_STRING:
        raise ValueError("the section '{}' doesn't exists".format(section))
    # Empty name means no retval.
    retval = HELP_DOC_STRING[section]
    if subnames:
        name = subnames[0]
        subnames = subnames[1:]
        if name in retval:
            retval = retval[name]
            i = 0
            while i < len(subnames):
                name = subnames[i]
                if isinstance(retval, dict):
                    # If the parent section was not a dict that means the child section doesn't exists.
                    if name in retval: # If the child section exists in the parent section.
                        retval = retval[name]
                    else: # If the child section doesn't exists.
                        retval = None
                elif (isinstance(retval, list) or isinstance(retval, tuple)) and isinstance(subnames[i], int) and subnames[i] < len(retval):
                    retval = retval[i]
                else:
                    retval = None
                if retval == None: # Only continue searching if the parent section exists.
                    i = len(subnames)
                else: # Parent section still exists.
                    i += 1
        else:
            retval = None
    # If the retval is a dict, only returns if there is a key of empty string.
    if isinstance(retval, dict):
        if "" in retval:
            retval = retval[""]
    return retval

def doc_get_usage(*args, raw=False):
    global HELP_DOC_STRING
    retval = None
    if args:
        retval = doc_get('usage', *args)
        if retval:
            if isinstance(retval, dict):
                if "" in retval:
                    retval = retval[""]
                elif not raw:
                    retval = None
            if retval and not raw:
                name = " ".join(args)
                if isinstance(retval, str):
                    retval = "usage: {} {}".format(name, retval)
                elif isinstance(retval, list) or isinstance(retval, tuple):
                    result = "usage:"
                    for v in retval:
                        result += "\n - {} {}".format(name, v)
                    retval = result
    if not raw and retval == None:
        retval = "no help string found for '{}'.".format(' '.join(args))
    return retval

def remove_animation(animator):
    '''Remove an animation from the list of animators.'''
    global animators
    if animator in animators:
        animators.remove(animator)

def start_animation(animator):
    '''Start an animation'''
    global animators
    animators.append(animator)
    # Automatically start the animation and set the callback to remove the object from the list.
    animator.callback = remove_animation
    animator.start()

def push_matrix(transMatrix):
    '''Push a transformation matrix to current renderable.'''
    global selection, transformation, transformation_history
    if selection > -1:
        renderable = to_render[selection]
        if isinstance(transMatrix, TransformationMatrix):
            renderable.transformation.append(transMatrix)
        elif isinstance(transMatrix, list) or isinstance(transMatrix, tuple):
            renderable.transformation.extend(transMatrix)
    else:
        if isinstance(transMatrix, TransformationMatrix):
            transformation.append(transMatrix)
        elif isinstance(transMatrix, list) or isinstance(transMatrix, tuple):
            transformation.extend(transMatrix)
    transformation_history.clear()

def pop_matrix():
    '''Pop a transformation matrix from current renderable.'''
    global selection, transformation
    trans = transformation
    if selection > -1:
        renderable = to_render[selection]
        trans = renderable.transformation
    if trans:
        val = trans.pop()
        retval = [val]
        if isinstance(val, int):
            retval = []
            for _ in range(0, val):
                retval.insert(0, trans.pop())
        return retval
    else:
        raise ValueError("no action to undo")

def add_renderable(renderable):
    '''Add a new renderable to render
    Args:
        renderable (Renderable): renderable to add and select.
    '''
    global to_render, selection
    to_render.append(renderable)
    selection = len(to_render) - 1
    transformation_history.clear()

def delete_renderable():
    '''Remove the selected renderable and select the top most renderable.
    Currently, the selected renderable is always the top most in the stack.
    '''
    global to_render, selection, transformation_history
    if selection > -1:
        to_render = to_render[:selection] + to_render[selection+1:]
        if selection >= len(to_render):
            selection = len(to_render) - 1
        transformation_history.clear()

def pop_renderable():
    '''Remove top most renderable'''
    global to_render, selection, transformation_history
    if to_render:
        to_render = to_render[:-1]
        if selection >= len(to_render):
            selection = len(to_render) - 1
        transformation_history.clear()

transformation_history = []
def undo():
    '''Undo a transformation'''
    global tansformation_history, transformation
    matrix = pop_matrix()
    transformation_history.append((get_selected_renderable(), matrix))

def redo():
    '''Redo a transformation'''
    global tansformation_history, transformation
    if transformation_history:
        renderable, matrix = transformation_history.pop()
        if renderable and renderable in to_render:
            renderable.transformation.extend(matrix)
            if len(matrix) > 1:
                renderable.transformation.append(len(matrix))
        elif renderable == None:
            transformation.extend(matrix)
            if len(matrix) > 1:
                transformation.append(len(matrix))
        else:
            print("no action to redo")
    else:
        print("no action to redo")

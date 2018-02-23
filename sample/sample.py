#!usr/bin/env python3
# -*- coding:utf-8 -*-

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
# Imports the 3D opengl helper Module.
import SimplePyToolKit as main
from SimplePyToolKit import doc_get, add_renderable
from SimplePyToolKit.Executor import *
import SimplePyToolKit.Builder as Builder
import SimplePyToolKit.Camera as Camera

selection = -1
main.HELP_DOC_STRING = {
    "about": {
        "author": [
            {
                "name": "Suhendi",
                "Student ID Number": "13516048",
                "Profile": "I am a student at ITB.",
            }
        ],
        "About": '''This program is a sample program made to demonstrate the usage of this helper module.''',
    },
    "usage": {
        "help": "[command_name]",
    },
    "help": {
        "":"Use the keyboard button w, a, s and d to move forward, leftward, downward and right ward. Use the keyboard button x to zoom in and space to zoom out.\
Drag the mouse to look around.",
        "help": "show help for this program.",
        "about": "show information about this program.",
    },
}
lines = []
points = []

def about():
    section = doc_get("about")
    if "author" in section:
        def print_author(author):
            if 'name' in author:
                print(author['name'])
                for k, v in author.items():
                    print("  ", k + ":", v) if k.lower() != 'name' else None
        if isinstance(section['author'], dict):
            print("Author: ")
            print_author(section['author'])
        elif isinstance(section['author'], list) or isinstance(section['author'], tuple):
            print("Author{}:".format('s' if len(section['author']) > 1 else ''))
            for author in section['author']:
                print_author(author)
    for k, v in section.items():
        if k.lower() != 'author':
            print(k + ":")
            print(v)

def ShowHelp(*args):
    print(main.help(*args))

command_executor = Executor() # Executor for user-level commands.
command_executor.register("help", ShowHelp)
command_executor.register("about", about)

def Sample():
    global running, to_render, points
    # Prints welcome message.
    print(main.title.decode('utf-8'))
    print("Type 'help' for more information.")
    print("Type 'help <command_name>' for more information about a specific command.")
    # Add some stuff to render.
    add_renderable(Builder.block((0, 50, 0), 25, 25, 25))
    add_renderable(Builder.line((10, 5, 0), (-25, -10, 0)))
    add_renderable(Builder.block((0, 0, 200), 25, 25, 25))
    # Run the program.
    while main.running:
        try:
            # Poll command from the user.
            sys.stdout.write("> ")
            sys.stdout.flush()
            command, args = poll_command()
            if command:
                # Run respective commands.
                if command == "exit":
                    main.running = False
                    print("Exiting")
                elif command_executor.has(command):
                    command_executor(command, *args)
                else:
                    print("unknown command:", command)
        except EOFError:
            main.running = False
        except Exception as e:
            print(e.__class__.__name__ +":", str(e))


if __name__ == '__main__':
    main.title = b'Sample Program'
    main.camera_controller = Camera.CameraController(main.camera, 50, 270, b'x', b' ', b'a', b'd', b'w', b's')
    main.func_main = Sample
    main.camera.set_position((0, 0, -150))
    main.Start(sys.argv)

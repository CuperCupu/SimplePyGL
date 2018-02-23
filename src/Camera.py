from OpenGL.GLUT import *
from .Renderable import TransformationMatrix
from .Renderable import Transform
from .Renderable import Vector
import math
import threading
import time
from functools import reduce
from .InputHandler import *

class Camera:

    def __init__(self, position, rotation):
        self.transform = Transform(position, rotation)
        self.matrix = self.transform.matrix
        self.reset()

    def get_position(self):
        return self.transform.position

    def set_position(self, position):
        self.transform.position = position
        self.reset()

    def get_rotation(self):
        return self.transform.rotation

    def set_rotation(self, rotation):
        self.transform.rotation = rotation
        self.reset()

    position = property(get_position, set_position)
    rotation = property(get_rotation, set_rotation)

    def reset(self):
        # Set positional matrix.
        x, y, z = self.transform.position
        self.positional_matrix = TransformationMatrix.translate(x, y, z)
        # Set rotational matrix.
        rx, ry, rz = self.transform.rotation
        self.rotational_matrix = TransformationMatrix.from_euler_angles(rx, -ry, rz)
        # Set the actual matrix of the camera.
        self.matrix.set_identity()
        self.matrix.multiply(self.positional_matrix)
        self.matrix.multiply(self.rotational_matrix)
    
class CameraController(threading.Thread):

    def __init__(self, camera, movement_speed, rotation_speed, key_forward=b'w', key_backward=b's', key_leftward=b'a', key_rightward=b'd', key_upward=b' ', key_downward=b'x'):
        super().__init__()
        # The camera to controll.
        self.camera = camera
        # Movement speed of the camera (unit/s).
        self.movement_speed = movement_speed
        # Rotation speed of the camera (deg/s)
        self.rotation_speed = rotation_speed
        # Whether this thread is running or not.
        self.running = False
        # Key Bindings.
        self.key_forward = key_forward
        self.key_backward = key_backward
        self.key_leftward = key_leftward
        self.key_rightward = key_rightward
        self.key_upward = key_upward
        self.key_downward = key_downward
        
    def stop_listening(self):
        self.running = False
        
    def run(self):
        global mouse_position
        # Horizontal movement keybind.
        binded = [self.key_forward, self.key_leftward, self.key_backward, self.key_rightward]
        # Set this thread as running.
        self.running = True
        # Delay between the loops.
        delay = 0.01
        # Previous time before current loop.
        last_time = time.time()
        # Store the position of the mouse in the last loop.
        last_mouse_position = get_mouse_position()
        # Whether the camera is rotating; used for ignoring the first mouse click.
        # The first click is ignored as to initialize the last_mouse_position.
        rotating_camera = False
        while self.running:
            # Handle time changes.
            current_time = time.time()
            delta = (current_time - last_time)
            # Handles camera movements.
            if (self.movement_speed != 0):
                # The combination of the keybind.
                combination = tuple(is_key_down(x) for x in binded)
                # True if any key is pressed; otherwise false.
                any_down = reduce(lambda x, y: x or y, combination)
                # The movement direction of the camera.
                direction = (0, 0, 0)
                if any_down: # Get horizontal movement, only if a key binded to the movement is pressed.
                    # -1 notates that no movement should be made.
                    angle = -1
                    if combination == (1, 0, 0, 0):
                        # Forward.
                        angle = 0
                    elif combination == (0, 1, 0, 0):
                        # Left.
                        angle = 90
                    elif combination == (0, 0, 1, 0):
                        # Backward.
                        angle = 180
                    elif combination == (0, 0, 0, 1):
                        # Right.
                        angle = 270
                    elif combination == (1, 1, 0, 0):
                        # Forward Left.
                        angle = 45
                    elif combination == (1, 0, 0, 1):
                        # Forward Right.
                        angle = 315
                    elif combination == (0, 1, 1, 0):
                        # Backward Left.
                        angle = 135
                    elif combination == (0, 0, 1, 1):
                        # Backward Right.
                        angle = 225
                    if angle != -1:
                        # Set the x and z components of the direction based on the movement angle.
                        angle = math.radians(angle)
                        direction = (math.sin(angle), 0, math.cos(angle))   
                if is_key_down(self.key_upward) and not is_key_down(self.key_downward): # Get upwards movement.
                    direction = (direction[0], 1, direction[2])
                elif not is_key_down(self.key_upward) and is_key_down(self.key_downward): # Get downwards movement.
                    direction = (direction[0], -1, direction[2])
                # Apply changes if changes were made.
                if direction != (0, 0, 0):
                    # Normalize the direction vector.
                    direction = Vector.normalize(direction)
                    # Seperate the x, y and z component of the vector.
                    x, y, z = direction
                    # Reverse the y component, this is primarily because the renderer is reversed for y axis.
                    y = -y
                    # Rotate the direction based on the camera's rotation.
                    # Doesn't use rotation through z axis.
                    rx, ry, _ = self.camera.rotation
                    # Convert the angle to radians.
                    rx = math.radians(-rx)
                    ry = math.radians(ry)
                    # Set the new direction vector.
                    direction = (
                        x * math.cos(ry) + y * math.sin(rx) * math.sin(math.pi - ry) + z * math.cos(rx) * math.sin(-ry),
                        y * math.cos(rx) + z * math.sin(rx),
                        x * math.sin(ry) + y * math.sin(rx) * math.cos(math.pi - ry) + z * math.cos(rx) * math.cos(-ry),
                    )
                    # Offset the camera's position.
                    self.camera.position = tuple(self.camera.position[i] + (self.movement_speed * delta * direction[i]) for i in range(0, 3))
                    self.camera.reset()
            # Handles camera rotation.
            if rotating_camera:
                # Handles mouse position delta.
                dx, dy = get_mouse_x() - last_mouse_position[0], get_mouse_y() - last_mouse_position[1]
                # Only triggers if there is any changes to the mouse position.
                if dx != 0 and dy != 0:
                    # Get the window size.
                    width = glutGet(GLUT_WINDOW_WIDTH)
                    height = glutGet(GLUT_WINDOW_HEIGHT)
                    x, y, z = self.camera.rotation
                    if dy != 0:
                        x += dy / height * self.rotation_speed
                    if dx != 0:
                        y += -dx / width * self.rotation_speed
                    self.camera.rotation = (x, y, z)
                    self.camera.reset()
            # Camera only rotates if the left mouse button is pressed.
            rotating_camera = (self.rotation_speed != 0) and is_mouse_down(0)
            # Save the mouse position for the next loops.
            last_mouse_position = get_mouse_position()
            # Updates time for the next loops.
            last_time = current_time
            time.sleep(delay)


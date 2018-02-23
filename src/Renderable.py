from OpenGL.GL import *
import math
from functools import reduce
import threading
import time

class Vector:
    '''Constains the x, y and z information'''

    def __init__(self, x, y, z = 0):
        self.vector = (x, y, z)

    def set_x(self, val):
        self.vector = (val, self.vector[1], self.vector[2])

    def get_x(self):
        return self.vector[0]

    def set_y(self, val):
        self.vector = (self.vector[0], val, self.vector[2])

    def get_y(self):
        return self.vector[1]

    def set_z(self, val):
        self.vector = (self.vector[0], self.vector[1], val)

    def get_z(self):
        return self.vector[2]

    def __str__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ')'

    def normalize(self):
        '''Normalize the vector, length = 1
        Args:
            vector (Vector or list or tuple; if list or tuple, then len(vector) = 3): Vector to normalize.
        Returns:
            normalized vector.
        '''
        if isinstance(self, Vector):
            x, y, z = self.vector
        elif (isinstance(self, tuple) or (isinstance(self, list))) and len(self) == 3:
            x, y, z = self
        else:
            raise TypeError("unable to normalize type: {}".format(self.__class__.__name__))
        length = Vector.length(self)
        if isinstance(self, Vector):
            return Vector(x / length, y / length, z / length)
        elif isinstance(self, tuple):
            return (x / length, y / length, z / length)
        elif isinstance(self, list):
            return [x / length, y / length, z / length]

    def length(self):
        '''Length of the vector
        Args:
            vector (Vector or list or tuple; if list or tuple, then len(vector) = 3): Vector to get the length of.
        Returns:
            float: length of the vector.
        '''
        if isinstance(self, Vector):
            x, y, z = self.vector
        elif (isinstance(self, tuple) or (isinstance(self, list))) and len(self) == 3:
            x, y, z = self
        else:
            raise TypeError("unable to get the vector length of type: {}".format(self.__class__.__name__))
        return (x**2 + y**2 + z**2)**0.5

    x = property(get_x, set_x)
    y = property(get_y, set_y)
    z = property(get_z, set_z)

class Line:

    def __init__(self, p1, p2, color=None):
        # Accepts both Vertex and tuple.
        self.vertices = [p1, p2]
        if color == None:
            self.color = []
        else:
            self.color = color
        for i in range(0, 2):
            if isinstance(self.vertices[i], tuple): # Convert tuples to vertex.
                self.vertices[i] = Vector(*self.vertices[i])
            elif not isinstance(self.vertices[i], Vector): # Handles unsupported type.
                raise TypeError("type {} not supported as a vertex".format(self.vertices[i].__class__.__name__))

    def __str__(self):
        return '(' + str(self.vertices[0]) + ', ' + str(self.vertices[1]) + ')'

    def render(self):
        '''Render this object using OpenGL'''
        # Render line.
        glBegin(GL_LINES)
        if len(self.color) > 0:
            glColor(*self.color[0])
        glVertex(*self.vertices[0].vector)
        if len(self.color) > 1:
            glColor(*self.color[1])
        glVertex(*self.vertices[1].vector)
        glEnd()

    def applyTransformation(self, transformer):
        if isinstance(transformer, TransformationMatrix):
            new = []
            for p in self.vertices:
                new.append(transformer * p)
            self.vertices = new
        else:
            raise TypeError("trying to transform a {} with {}".format(self.__class__.__name__, transformer.__class__.__name__))

class Tri:

    def __init__(self, p1, p2, p3, color=None, twoface=False):
        # Accepts both Vertex and tuple.
        self.vertices = [p1, p2, p3]
        if color == None:
            self.color = []
        else:
            self.color = color
        self.two_face = twoface
        for i in range(0, 3):
            if isinstance(self.vertices[i], tuple): # Convert tuples to vertex.
                self.vertices[i] = Vector(*self.vertices[i])
            elif not isinstance(self.vertices[i], Vector): # Handles unsupported type.
                raise TypeError("type {} not supported as a vertex".format(self.vertices[i].__class__.__name__))

    def __str__(self):
        return '(' + str(self.vertices[0]) + ', ' + str(self.vertices[1]) + ', ' + str(self.vertices[2]) + ')'

    def render(self):
        '''Render this object using OpenGL'''
        # Render front face.
        glBegin(GL_TRIANGLES)
        if len(self.color) > 0:
            glColor(*self.color[0])
        glVertex(*self.vertices[0].vector)
        if len(self.color) > 1:
            glColor(*self.color[1])
        glVertex(*self.vertices[1].vector)
        if len(self.color) > 2:
            glColor(*self.color[2])
        glVertex(*self.vertices[2].vector)
        glEnd()
        if self.two_face:
            # Render back face.
            glBegin(GL_TRIANGLES)
            if len(self.color) > 3:
                glColor(*self.color[2])
            glVertex(*self.vertices[2].vector)
            if len(self.color) > 2:
                glColor(*self.color[1])
            glVertex(*self.vertices[1].vector)
            if len(self.color) > 1:
                glColor(*self.color[0])
            glVertex(*self.vertices[0].vector)
            glEnd()

    def applyTransformation(self, transformer):
        if isinstance(transformer, TransformationMatrix):
            new = []
            for p in self.vertices:
                new.append(transformer * p)
            self.vertices = new
        else:
            raise TypeError("trying to transform a {} with {}".format(self.__class__.__name__, transformer.__class__.__name__))

class Quad:

    def __init__(self, p1, p2, p3, p4, color=None, twoface=False):
        # Accepts both Vertex and tuple.
        self.vertices = [p1, p2, p3, p4]
        if color == None:
            self.color = []
        else:
            self.color = color
        self.two_face = twoface
        for i in range(0, 4):
            if isinstance(self.vertices[i], tuple): # Convert tuples to vertex.
                self.vertices[i] = Vector(*self.vertices[i])
            elif not isinstance(self.vertices[i], Vector): # Handles unsupported type.
                raise TypeError("type {} not supported as a vertex".format(self.vertices[i].__class__.__name__))

    def __str__(self):
        return '(' + str(self.vertices[0]) + ', ' + str(self.vertices[1]) + ', ' + str(self.vertices[2]) + ', ' + str(self.vertices[3]) + ')'

    def render(self):
        '''Render this object using OpenGL'''
        # Render front face.
        glBegin(GL_QUADS)
        if len(self.color) > 0:
            glColor(*self.color[0])
        glVertex(*self.vertices[0].vector)
        if len(self.color) > 1:
            glColor(*self.color[1])
        glVertex(*self.vertices[1].vector)
        if len(self.color) > 2:
            glColor(*self.color[2])
        glVertex(*self.vertices[2].vector)
        if len(self.color) > 3:
            glColor(*self.color[3])
        glVertex(*self.vertices[3].vector)
        glEnd()
        if self.two_face:
            # Render back face.
            glBegin(GL_QUADS)
            if len(self.color) > 3:
                glColor(*self.color[3])
            glVertex(*self.vertices[3].vector)
            if len(self.color) > 2:
                glColor(*self.color[2])
            glVertex(*self.vertices[2].vector)
            if len(self.color) > 1:
                glColor(*self.color[1])
            glVertex(*self.vertices[1].vector)
            if len(self.color) > 0:
                glColor(*self.color[0])
            glVertex(*self.vertices[0].vector)
            glEnd()

    def applyTransformation(self, transformer):
        if isinstance(transformer, TransformationMatrix):
            new = []
            for p in self.vertices:
                new.append(transformer * p)
            self.vertices = new
        else:
            raise TypeError("trying to transform a {} with {}".format(self.__class__.__name__, transformer.__class__.__name__))

class Renderable:

    def __init__(self, *childs):
        self.childs = []
        if childs:
            self.childs.extend(childs)
        self.transform = Transform()
        self.transformation = [self.transform.matrix]

    def render(self):
        '''Render this object using OpenGL'''
        glPushMatrix()
        # Apply transformation matrices.
        for matrix in self.transformation:
            if isinstance(matrix, TransformationMatrix):
                glMultMatrixf(matrix.c_values())
        # Render all objects attached to this object.
        for obj in self.childs:
            obj.render()
        glPopMatrix()
    
    def attach(self, child):
        if not hasattr(child, 'render'):
            raise TypeError("trying to attach '" + child.__repr__() + "' with no method 'render'")
        else:
            self.childs.append(child)

    def applyTransformation(self, transformer):
        if isinstance(transformer, TransformationMatrix):
            for c in self.childs:
                c.applyTransformation(transformer)
        else:
            raise TypeError("trying to transform a {} with {}".format(self.__class__.__name__, transformer.__class__.__name__))

class Transform:

    def __init__(self, position=(0, 0, 0), rotation=(0, 0, 0)):
        self.position = position
        self.rotation = rotation
        self.matrix = TransformationMatrix()
        self.reset()

    def reset(self):
        # Set positional matrix.
        self.positional_matrix = TransformationMatrix.translate(*self.position)
        # Set rotational matrix.
        self.rotational_matrix = TransformationMatrix.from_euler_angles(*self.rotation)
        # Set the actual matrix of the camera.
        self.matrix.set_identity()
        self.matrix.multiply(self.positional_matrix)
        self.matrix.multiply(self.rotational_matrix)

class TransformationMatrix:

    def __init__(self, *values):
        if values:
            self.reset(*values)
        else:
            self.set_identity()

    def c_values(self):
        if self._cached_c_values == None:
            # Split the list into a list of 4.
            segments = []
            c = 0
            holder = []
            # Uses values as a list for the pop functionality.
            values = list(self.values)
            while c < 4 and values:
                # If the value is an int, parse it into float before hand.
                if isinstance(values[0], int):
                    values[0] = float(values[0])
                if isinstance(values[0], float):
                    holder.append(values[0])
                    values.pop(0)
                    c += 1
                    if c == 4:
                        segments.append(holder)
                        holder = []
                        c = 0
                else: # Handles error for other types.
                    raise TypeError("float expected, got " + values[0].__class__.__name__)
            # Construct a C typed array of array.
            c_segments = []
            for seg in segments:
                c_segments.append((ctypes.c_float * len(seg))(*seg))
            # Save the constructed array for future use.
            self._cached_c_values = (ctypes.c_float * 4 * 4)(*c_segments)
        return self._cached_c_values

    def reset(self, *values):
        '''Accepts 16 float values'''
        if len(values) == 16:
            self.values = tuple(values)
            self._cached_c_values = None
        else:
            raise ValueError("expected 16 float values, got " + len(values))

    def set_identity(self):
        self.reset(
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        )

    def __str__(self):
        return '[' + reduce(lambda x, y: str(x) + ', ' + str(y), self.values) + ']'

    def multiply(self, other):
        if isinstance(other, TransformationMatrix):
            values = []
            for i in range(0, 4):
                for j in range(0, 4):
                    values.append(sum(self.values[i * 4 + k] * other.values[j + k * 4] for k in range(0, 4)))
            self.reset(*values)
        else:
            raise TypeError("unsupported multiplication between: '{}' and '{}'".format(self.__class__.__name__, other.__class__.__name__))

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            # Multiplication with scalar
            return TransformationMatrix(*[x * other for x in self.values])
        elif isinstance(other, tuple):
            # Multiplication with vector.
            count = len(other)
            if len(other) < 4:
                other = (*other, *[1 for _ in range(0, 4 - len(other))])
            result = (
                sum([self.values[i * 4] * other[i] for i in range(0, 4)]),
                sum([self.values[1 + i * 4] * other[i] for i in range(0, 4)]),
                sum([self.values[2 + i * 4] * other[i] for i in range(0, 4)]),
                sum([self.values[3 + i * 4] * other[i] for i in range(0, 4)]),
            )
            return result[:count]
        elif isinstance(other, list):
            # Multiplication with list.
            count = len(other)
            other = other[:]
            while len(other) < 4:
                other.append(1)
            result = [
                sum([self.values[i * 4] * other[i] for i in range(0, 4)]),
                sum([self.values[1 + i * 4] * other[i] for i in range(0, 4)]),
                sum([self.values[2 + i * 4] * other[i] for i in range(0, 4)]),
                sum([self.values[3 + i * 4] * other[i] for i in range(0, 4)]),
            ]
            return result[:count]
        elif isinstance(other, Vector):
            # Multiplication with Vector.
            point = (other.x, other.y, other.z, 1)
            result = self * point
            new = Vector(*result[:-1])
            return new
        elif isinstance(other, TransformationMatrix):
            # Multiplication with other matrix.
            values = []
            for i in range(0, 4):
                for j in range(0, 4):
                    values.append(sum(self.values[i * 4 + k] * other.values[j + k * 4] for k in range(0, 4)))
            return TransformationMatrix(*values)
        else:
            raise TypeError("unsupported operand type(s) for *: '{}' and '{}'".format(self.__class__.__name__, other.__class__.__name__))

    @staticmethod
    def translate(x, y, z):
        return TransformationMatrix(
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            x, y, z, 1.0
        )
    
    @staticmethod
    def dilate(k):
        return TransformationMatrix(
            k, 0.0, 0.0, 0.0,
            0.0, k, 0.0, 0.0,
            0.0, 0.0, k, 0.0,
            0.0, 0.0, 0.0, 1.0
        )

    @staticmethod
    def shear(src, dest, k):
        return TransformationMatrix(
            1 + (k * src[0] * dest[0]), (k * src[1] * dest[0]), (k * src[2] * dest[0]), 0.0,
            (k * src[0] * dest[1]), 1 + (k * src[1] * dest[1]), (k * src[2] * dest[1]), 0.0,
            (k * src[0] * dest[2]), (k * src[1] * dest[2]), 1 + (k * src[2] * dest[2]), 0.0,
            0.0, 0.0, 0.0, 1.0
        )

    @staticmethod
    def stretch(x, y, z):
        return TransformationMatrix(
            x, 0.0, 0.0, 0.0,
            0.0, y, 0.0, 0.0,
            0.0, 0.0, z, 0.0,
            0.0, 0.0, 0.0, 1.0
        )

    @staticmethod
    def from_euler_angles(x, y, z):
        matrix = TransformationMatrix()
        matrix.multiply(TransformationMatrix.rotate(-y, (0, 1, 0)))
        matrix.multiply(TransformationMatrix.rotate(-x, (1, 0, 0)))
        matrix.multiply(TransformationMatrix.rotate(-z, (0, 0, 1)))
        return matrix

    @staticmethod
    def reflect_point(x, y, z):
        retval = []
        point = (x, y, z)
        if point != (0, 0, 0):
            retval.append(TransformationMatrix.translate(-x, -y, -z))
        retval.append(TransformationMatrix(
            -1, 0, 0, 0,
            0, -1, 0, 0,
            0, 0, -1, 0,
            0, 0, 0, 1,
        ))
        if point != (0, 0, 0):
            retval.append(TransformationMatrix.translate(x, y, z))
        if len(retval) == 1:
            return retval[0]
        elif len(retval) > 1:
            # Multiply all the matrix and collapse them into a single matrix.
            collapsed = retval[0]
            for i in range(1, len(retval)):
                collapsed *= retval[i]
            return collapsed
        return retval

    @staticmethod
    def reflect_line(vector, point=(0, 0, 0)):
        if len(vector) != 3:
            raise ValueError("invalid vector: {}".format(vector))
        retval = []
        x, y, z = point
        if point != (0, 0, 0):
            retval.append(TransformationMatrix.translate(-x, -y, -z))
        retval.append(TransformationMatrix.rotate(180, vector))
        if point != (0, 0, 0):
            retval.append(TransformationMatrix.translate(x, y, z))
        if len(retval) == 1:
            return retval[0]
        elif len(retval) > 1:
            # Multiply all the matrix and collapse them into a single matrix.
            collapsed = retval[0]
            for i in range(1, len(retval)):
                collapsed *= retval[i]
            return collapsed
        return retval


    @staticmethod
    def rotate(angle, axis, point=None):
        if len(axis) != 3:
            raise ValueError("invalid axis: {}".format(axis))
        retval = []
        if point and point != (0, 0, 0):
            retval.append(TransformationMatrix.translate(*[-x for x in point]))
        if axis == (0, 0, 1) or axis == (0, 0, -1):
            _, _, z = axis
            if z == 1:
                angle = math.radians(angle)
            else:
                angle = math.radians(-angle)
            retval.append(TransformationMatrix(
                math.cos(angle), math.sin(angle), 0.0, 0.0,
                -math.sin(angle), math.cos(angle), 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0
            ))
        elif axis == (0, 1, 0) or axis == (0, -1, 0):
            _, y, _ = axis
            if y == 1:
                angle = math.radians(angle)
            else:
                angle = math.radians(-angle)
            retval.append(TransformationMatrix(
                math.cos(angle), 0.0, -math.sin(angle), 0.0,
                0.0, 1.0, 0.0, 0.0,
                math.sin(angle), 0.0, math.cos(angle), 0.0,
                0.0, 0.0, 0.0, 1.0
            ))
        elif axis == (1, 0, 0) or axis == (-1, 0, 0):
            x, _, _ = axis
            if x == 1:
                angle = math.radians(angle)
            else:
                angle = math.radians(-angle)
            retval.append(TransformationMatrix(
                1.0, 0.0, 0.0, 0.0,
                0.0, math.cos(angle), math.sin(angle), 0.0,
                0.0, -math.sin(angle), math.cos(angle), 0.0,
                0.0, 0.0, 0.0, 1.0
            ))
        else:
            x, y, z = axis
            # Align axis with xz plane.
            x_angle = math.degrees(math.atan2(y, z))
            level_xz = TransformationMatrix.rotate(x_angle, (1, 0, 0))
            # Align new axis with z axis.
            nx, ny, nz, _ = level_xz * (x, y, z, 1)
            y_angle = -math.degrees(math.atan2(nx, nz))
            level_z = TransformationMatrix.rotate(y_angle, (0, 1, 0))
            # Rotate around the z axis.
            rotation = TransformationMatrix.rotate(angle, (0, 0, 1))
            # Reverse alignment of z axis.
            i_level_z = TransformationMatrix.rotate(-y_angle, (0, 1, 0))
            # Reverse alignment of xz plane.
            i_level_xz = TransformationMatrix.rotate(-x_angle, (1, 0, 0))
            # Append individual transformation matrix to return value.
            retval.append(level_xz)
            retval.append(level_z)
            retval.append(rotation)
            retval.append(i_level_z)
            retval.append(i_level_xz)
        if point and point != (0, 0, 0):
            retval.append(TransformationMatrix.translate(*point))
        if len(retval) == 1:
            return retval[0]
        elif len(retval) > 1:
            # Multiply all the matrix and collapse them into a single matrix.
            collapsed = retval[0]
            for i in range(1, len(retval)):
                collapsed *= retval[i]
            return collapsed

class RotateOverTime(threading.Thread):

    def __init__(self, angle, axis, pivot, speed=360, callback=None):
        super().__init__()
        self.running = False
        self.current = TransformationMatrix()
        self.target = angle
        self.axis = axis
        self.pivot = pivot
        '''Duration is angle / speed.'''
        self.duration = abs(angle / speed)
        self.callback = callback

    def stop(self):
        self.running = False

    def run(self):
        self.running = True
        identity = [
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1,
        ]
        start_time = time.time()
        current_time = time.time()
        delay = 0.01
        while self.running and (current_time - start_time) < self.duration:
            current_angle = (current_time - start_time) / self.duration * self.target
            self.current.reset(*TransformationMatrix.rotate(current_angle, self.axis, self.pivot).values)
            current_time = time.time()
            time.sleep(delay)
        self.current.reset(*TransformationMatrix.rotate(self.target, self.axis, self.pivot).values)
        if self.callback:
            self.callback(self)

class TransformOverTime(threading.Thread):

    def __init__(self, target, duration=1, callback=None):
        super().__init__()
        self.running = False
        self.current = target
        self.target = target.values
        self.duration = duration
        self.callback = callback

    def stop(self):
        self.running = False

    def run(self):
        self.running = True
        identity = [
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1,
        ]
        start_time = time.time()
        current_time = time.time()
        delay = 0.01
        while self.running and (current_time - start_time) < self.duration:
            current = list(identity[i] + (self.target[i] - identity[i]) * (current_time - start_time) / self.duration for i in range(0, 16))
            self.current.reset(*current)
            current_time = time.time()
            time.sleep(delay)
        self.current.reset(*self.target)
        if self.callback:
            self.callback(self)
        
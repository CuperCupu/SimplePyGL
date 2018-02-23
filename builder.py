from GLHelper.glHelper import *
import math

def line(p1, p2, color):
    ''' Create a line object.
    Args:
        p1 (tuple): len(p1) == 3, represents x, y and z.
        p2 (tuple): len(p2) == 3, represents x, y and z.
    Returns:
        Renderable: a line object.
    '''
    ren_obj = Renderable()
    ren_obj.attach(Line(p1, p2, [color]))
    return ren_obj
    
def circle(radius, segments = 12, color = (0.4, 0.7, 1.0, 1.0)):
    '''Create a circle.
    Args:
        radius (float): the radius of the circle
    Returnss:
        Renderable: a 2D circle object.
    '''
    origin = Vector(0, 0, 0)
    vertices = []
    # Generate vertices.
    for i in range(0, segments):
        angle = math.pi * 2 * i / segments
        vertices.append(Vector(math.cos(angle) * radius, math.sin(angle) * radius, 0))
    ren_obj = Renderable()
    # Generate tris.
    for i in range(0, segments):
        n = i + 1
        if n >= segments:
            n -= segments
        ren_obj.attach(Tri(origin, vertices[i], vertices[n], [color], True))
    return ren_obj
    

def polygon(points):
    '''Create a polygonal shape based on several input points. Doesn't automatically create a concave shape.
    Args:
        points (list): list of Vector or tuple with len of 3 representing x, y and z.
    Returns:
        Renderable: a 2D polygonal object.
    '''
    # Check for input points count.
    count = len(points)
    if count < 3:
        raise ValueError("trying to build a polygon with {} {}.".format(count, "vertex" if count < 2 else "vertices"))
    # Process vertices
    vertices = []
    for p in points:
        if isinstance(p, Vector):
            vertices.append(p)
        elif (isinstance(p, tuple) or isinstance(p, list)) and len(p) == 3:
            vertices.append(Vector(p[0], p[1], p[2]))
        else:
            raise TypeError("unsupported type", p.__class__.__name__)
    # Create a simple polygon, doesn't support concave shape.
    ren_obj = Renderable()
    color = (0.4, 0.7, 1.0, 1.0)
    ren_obj.attach(Tri(vertices[0], vertices[1], vertices[2], [color], True))
    p = 2
    for i in range(3, count):
        c = i
        n = i + 1
        if n == count:
            n = 0
        ren_obj.attach(Tri(vertices[c], vertices[n], vertices[p], [color], True))
    return ren_obj

def block(p, width, height, length):
    '''Create a 3D block based on a position, width, height and length.
    Args:
        p (tuple): len(p) == 3, represents x, y and z of the position of the newly created block.
        width (float): width of the block.
        height (float): height of the block.
        length (float): length of the block.
    Returns:
        Renderable: a block object. 
    '''
    # Get position.
    x, y, z = p
    # Get offset in x, y, and z direction from the position.
    offset_x = width / 2
    offset_y = height / 2
    offset_z = length / 2
    # Start creating the renderable.
    ren_obj = Renderable()
    # Generate solid layer
    color = (0.4, 0.7, 1.0, 1.0)
    vertices = [
        Vector(x - offset_x, y - offset_y, z + offset_z),
        Vector(x + offset_x, y - offset_y, z + offset_z),
        Vector(x + offset_x, y - offset_y, z - offset_z),
        Vector(x - offset_x, y - offset_y, z - offset_z),
        Vector(x - offset_x, y + offset_y, z + offset_z),
        Vector(x + offset_x, y + offset_y, z + offset_z),
        Vector(x + offset_x, y + offset_y, z - offset_z),
        Vector(x - offset_x, y + offset_y, z - offset_z),
    ]
    # Bottom
    ren_obj.attach(Quad(vertices[3], vertices[2], vertices[1], vertices[0], [color], True))
    # Top
    ren_obj.attach(Quad(vertices[4], vertices[5], vertices[6], vertices[7], [color], True))
    # Front
    ren_obj.attach(Quad(vertices[0], vertices[1], vertices[5], vertices[4], [color], True))
    # Back
    ren_obj.attach(Quad(vertices[2], vertices[3], vertices[7], vertices[6], [color], True))
    # Left
    ren_obj.attach(Quad(vertices[3], vertices[0], vertices[4], vertices[7], [color], True))
    # Right
    ren_obj.attach(Quad(vertices[1], vertices[2], vertices[6], vertices[5], [color], True))
    # Generate outer lines
    color = (0.1, 0.4, 0.7, 1.0)
    offset_x += 0.005
    offset_y += 0.005
    offset_z += 0.005
    vertices = [
        Vector(x - offset_x, y - offset_y, z + offset_z),
        Vector(x + offset_x, y - offset_y, z + offset_z),
        Vector(x + offset_x, y - offset_y, z - offset_z),
        Vector(x - offset_x, y - offset_y, z - offset_z),
        Vector(x - offset_x, y + offset_y, z + offset_z),
        Vector(x + offset_x, y + offset_y, z + offset_z),
        Vector(x + offset_x, y + offset_y, z - offset_z),
        Vector(x - offset_x, y + offset_y, z - offset_z),
    ]
    # Bottom lines
    ren_obj.attach(Line(vertices[0], vertices[1], [color]))
    ren_obj.attach(Line(vertices[1], vertices[2], [color]))
    ren_obj.attach(Line(vertices[2], vertices[3], [color]))
    ren_obj.attach(Line(vertices[3], vertices[0], [color]))
    # Top lines
    ren_obj.attach(Line(vertices[4], vertices[5], [color]))
    ren_obj.attach(Line(vertices[5], vertices[6], [color]))
    ren_obj.attach(Line(vertices[6], vertices[7], [color]))
    ren_obj.attach(Line(vertices[7], vertices[4], [color]))
    # Corner lines
    ren_obj.attach(Line(vertices[0], vertices[4], [color]))
    ren_obj.attach(Line(vertices[1], vertices[5], [color]))
    ren_obj.attach(Line(vertices[2], vertices[6], [color]))
    ren_obj.attach(Line(vertices[3], vertices[7], [color]))
    return ren_obj

def cube(p, size):
    '''Create a 3D cube based on a point and a size.
    Args:
        p (tuple): len(p) == 3, represents x, y and z of the position of the newly created cube.
        size (float): size of the cube.
    Returns:
        Renderable: a cube object.
    '''
    return block(p, size, size, size) # Build a block with the same witdh, height and length.

def pyramid(p, height, radius, base_count=4):
    '''Create a 3D pyramid.
    Args:
        p (tuple): len(p) == 3, represents x, y and z of the position of the newly created pyramid.
        height (float): height of the pyramid.
        radius (float): radius of the base of the pyramid.
        base_count (int): the number of corner vertices of the pyramid.
    Returns:
        Renderable: a pyramid object.
    '''
    x, y, z = p
    top = Vector(x, y + height, z)
    vertices = []
    for i in range(0, base_count):
        angle = i / base_count * math.pi * 2
        vertices.append(Vector(radius * math.cos(angle), 0, radius * math.sin(angle)))
    ren_obj = polygon(vertices)
    color = (0.4, 0.7, 1.0, 1.0)
    color2 = (0.1, 0.4, 0.7, 1.0)
    for i in range(0, len(vertices)):
        n = i + 1
        if n == len(vertices):
            n = 0
        ren_obj.attach(Tri(vertices[i], vertices[n], top, [color], True))
        ren_obj.attach(Line(vertices[i], top, [color2]))
        ren_obj.attach(Line(vertices[i], vertices[n], [color2]))

    return ren_obj

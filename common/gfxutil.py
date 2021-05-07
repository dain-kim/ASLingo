#####################################################################
#
# gfxutil.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################


from kivy.clock import Clock as kivyClock
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Rectangle, Ellipse, Color, Fbo, ClearBuffers, ClearColor, Line
from kivy.graphics import PushMatrix, PopMatrix, Scale, Callback
from kivy.graphics.texture import Texture
from kivy.uix.label import Label
from kivy.core.window import Window

import numpy as np

def topleft_label(font_size='20sp', font_name="Arial"):
    """
    :returns: A Label object configured to be positioned at the top-left of the screen.
    """
    l = Label(text = "text", valign='top', font_size=font_size, font_name = font_name,
              pos=(Window.width * 0.5 - 40, Window.height * 0.5 - 55),
              text_size=(Window.width, Window.height))
    return l


def resize_topleft_label(label):
    """
    If the screen size has changed, repositions the label so that it remains
    in the top-left of the window.

    :param label: The Label object.
    """
    label.pos = (Window.width * 0.5 - 40, Window.height * 0.5 - 55)
    label.text_size = (Window.width, Window.height)

class CLabelRect(InstructionGroup):
    """
    Class for creating labels that can be added to Widget canvases like standard Kivy graphics
    objects, like Rectangle and Circle.
    """

    def __init__(self, cpos, text = "Hello World", font_size = 21, font_name = "Arial"):
        """
        :param cpos: The position of the label as a tuple (x, y).

        :param text: The text dispayed on the label.

        :param font_size: The size of the label text.

        :param font_name: The font of the label text.
        """
        super(CLabelRect, self).__init__()

        self.cpos = cpos
        self.font_size = font_size
        self.font_name = font_name

        self.label = Label(text=text, font_size=str(self.font_size)+"sp", font_name=self.font_name)
        self.label.texture_update()
        self.rect = Rectangle(size=self.label.texture_size, texture=self.label.texture)
        self.add(self.rect)
        self.set_cpos(self.cpos)

    def set_text(self, text):
        """
        Function that updates the label texture to change the label's text.

        :param text: The new text for the label to display.
        """

        self.label.text = text
        self.label.texture_update()
        
        self.rect.size = self.label.texture_size
        self.rect.texture = self.label.texture
        self.set_cpos(self.cpos)

    def set_cpos(self, cpos):
        """
        Set the center position of the text.

        :param cpos: The new (x,y) position for the text label.
        """

        self.cpos = cpos
        self.rect.pos = (self.cpos[0]-(self.label.texture_size[0]*0.5), self.cpos[1]-(self.label.texture_size[1]*0.5))



class CEllipse(Ellipse):
    """
    Override Ellipse class to add centered functionality.
    Use *cpos* and *csize* to set/get the ellipse based on a centered registration point
    instead of a bottom-left registration point.
    """

    def __init__(self, **kwargs):
        super(CEllipse, self).__init__(**kwargs)
        if 'cpos' in kwargs:
            self.cpos = kwargs['cpos']

        if 'csize' in kwargs:
            self.csize = kwargs['csize']

    def get_cpos(self):
        """
        The centered position of the ellipse as a tuple `(x, y)`.
        """

        return (self.pos[0] + self.size[0]/2, self.pos[1] + self.size[1]/2)

    def set_cpos(self, p):
        """
        Sets centered position of the ellipse.
        
        :param p: The new centered position as a tuple `(x, y)`.
        """

        self.pos = (p[0] - self.size[0]/2 , p[1] - self.size[1]/2)

    def get_csize(self):
        """
        The current size of the ellipse as a tuple `(width, height)`.
        """

        return self.size

    def set_csize(self, p):
        """
        Sets the size of the ellipse.
        
        :param p: The new size as a tuple `(width, height)`.
        """

        cpos = self.get_cpos()
        self.size = p
        self.set_cpos(cpos)

    cpos = property(get_cpos, set_cpos)
    csize = property(get_csize, set_csize)



class CRectangle(Rectangle):
    """
    Override Rectangle class to add centered functionality.
    Use *cpos* and *csize* to set/get the rectangle based on a centered registration point
    instead of a bottom-left registration point.
    """

    def __init__(self, **kwargs):
        super(CRectangle, self).__init__(**kwargs)
        if 'cpos' in kwargs:
            self.cpos = kwargs['cpos']

        if 'csize' in kwargs:
            self.csize = kwargs['csize']

    def get_cpos(self):
        """
        The centered position of the rectangle as a tuple `(x, y)`.
        """

        return (self.pos[0] + self.size[0]/2, self.pos[1] + self.size[1]/2)

    def set_cpos(self, p):
        """
        Sets centered position of the rectangle.
        
        :param p: The new centered position as a tuple `(x, y)`.
        """

        self.pos = (p[0] - self.size[0]/2 , p[1] - self.size[1]/2)

    def get_csize(self):
        """
        The current size of the rectangle as a tuple `(width, height)`.
        """

        return self.size

    def set_csize(self, p):
        """
        Sets the size of the rectangle.
        
        :param p: The new size as a tuple `(width, height)`.
        """

        cpos = self.get_cpos()
        self.size = p
        self.set_cpos(cpos)

    cpos = property(get_cpos, set_cpos)
    csize = property(get_csize, set_csize)



class KFAnim(object):
    """
    Keyframe animation class.  
    
    Initialize with an argument list where each argument is a keyframe.
    One keyframe = `(t, k1, k2, ...)`, where *t* is the time of the keyframe and
    *k1, k2, ..., kN* are the values.

    For example: ``KFAnim((time1, pos1_x, pos1_y), (time2, pos2_x, pos2_y))``
    """

    def __init__(self, *kwargs):
        super(KFAnim, self).__init__()
        frames = list(zip(*kwargs))
        self.time = frames[0]
        self.frames = frames[1:]

    def eval(self, t):
        """
        :param t: The time corresponding to the desired interpolated values.

        :returns: The linearly-interpolated value for the specified time from the set of initial keyframes.
            If more than one value, then returns each interpolated value in a list.
        """

        if len(self.frames) == 1:
            return np.interp(t, self.time, self.frames[0])
        else:
            return [np.interp(t, self.time, y) for y in self.frames]

    def is_active(self, t):
        """
        :param t: The time to check.

        :returns: True if the given time is within keyframe range. Otherwise, false.
        """

        return t < self.time[-1]


class AnimGroup(InstructionGroup):
    """
    AnimGroup is a simple manager of objects that get drawn, updated 
    on each frame, and removed when they are "done" (see :meth:`on_update`).
    """

    def __init__(self):
        super(AnimGroup, self).__init__()
        self.objects = []

    def add(self, obj):
        """
        Adds an object to the group.
        
        :param obj: The object to add. Must be an InstructionGroup (ie, can be added to canvas) and
            it must have an `on_update(self, dt)` method that returns *True* to keep going or *False* to be removed.
        """

        super(AnimGroup, self).add(obj)
        self.objects.append(obj)

    def remove_all(self):
        """
        Removes all objects from the group
        """
        for o in self.objects:
            self.remove(o)
        self.objects = []

    def on_update(self):
        """
        Update function for each frame.  Will automatically remove
        objects that return `False` in their `on_update()` functions.
        """

        dt = kivyClock.frametime
        kill_list = [o for o in self.objects if o.on_update(dt) == False]

        for o in kill_list:
            self.objects.remove(o)
            self.remove(o)

    def size(self):
        """
        :returns: The number of objects in the group.
        """
        return len(self.objects)


class Cursor3D(InstructionGroup):
    """
    A graphics object for displaying a point moving in a pre-defined 3D space
    the 3D point must be in the range `[0, 1]` for all 3 coordinates.
    Depth is rendered as the size of the circle.
    """

    def __init__(self, area_size, area_pos, rgb, size_range = (10, 50), border = True):
        """
        :param area_size: The size of the cursor boundary.
        :param area_pos: The position of the cursor boundary in the window.
        :param rgb: The color of the cursor.
        :param size_range: The range in size of the cursor `(min_size, max_size)`.
        :param border: If *True*, will display the border of the cursor boundary.
        """
        super(Cursor3D, self).__init__()
        self.area_size = area_size
        self.area_pos = area_pos
        self.min_sz = size_range[0]
        self.max_sz = size_range[1]

        self.border_line = Line(rectangle= area_pos + area_size)
        if border:
            self.add(Color(1, 0, 0))
            self.add(self.border_line)

        self.color = Color(*rgb)
        self.add(self.color)

        self.cursor = CEllipse(segments = 40)
        self.cursor.csize = (30,30)
        self.cursor.cpos = self.area_pos
        self.add(self.cursor)

    def to_screen_xy(self, pos):
        """
        Converts a normalized position to screen coordinates. `pos[2]`, the z-coordinate is ignored.

        :param pos: A position in a unit range.

        :returns: `(x, y)`, the normalized position scaled to the screen coordinates of this object's size and position.
        """

        return pos[0:2] * self.area_size + self.area_pos

    def set_pos(self, pos):
        """
        Sets the cursor position in screen coordinates.

        :param pos: A normalized 3D point (tuple) with all values from 0 to 1.
        """

        radius = self.min_sz + pos[2] * (self.max_sz - self.min_sz)
        self.cursor.csize = (radius*2, radius*2)
        self.cursor.cpos = pos[0:2] * self.area_size + self.area_pos

    def set_color(self, rgb):
        """
        Sets the color of the cursor.

        :param rgb: The new cursor color `(r, g, b)`.
        """

        self.color.rgb = rgb

    def set_boundary(self, area_size, area_pos):
        """
        Sets the size and position of the cursor boundary.

        :param size: The new size of the cursor boundary as a tuple `(width, height)`.

        :param pos: The new position of the cursor boundary as a tuple `(x, y)`.
        """

        self.area_size = area_size
        self.area_pos = area_pos
        self.border_line.rectangle = area_pos + area_size



def scale_point(pt, _range):
    """
    Converts the point `pt` to a unit range point spanning 0-1 in x, y, and z.

    :param pt: The input point as an array `[x, y, z]`.

    :param _range: The expected original bounds of the input point `pt` as an array 
        `((x_min, x_max), (y_min, y_max), (z_min, z_max))`.

    :returns: The point after conversion to unit range coordinates as an array `[x, y, z]`.
    """

    range_min = np.array((_range[0][0], _range[1][0], _range[2][0]))
    range_max = np.array((_range[0][1], _range[1][1], _range[2][1]))

    # pt == 0 is a special case meaning "no point". Return instead a point that is "furthest back" in Z
    if np.all(pt == 0):
        return np.array((0, 0, 1))

    pt = (pt - range_min) / (range_max - range_min)
    pt = np.clip(pt, 0, 1)
    return pt

import cv2
import numpy as np
from kivy import metrics
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.graphics.texture import Texture
from kivy.graphics.instructions import InstructionGroup
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from common.gfxutil import CLabelRect
from video_handler import VideoHandler

font_sz = metrics.dp(50)
font_name = "assets/AtlantisInternational"
w, h = Window.size

### BUTTONS

class ModeButton(Button):
    '''
    Extension of the Kivy Button class.
    '''
    def __init__(self, text, **kwargs):
        super(ModeButton, self).__init__(**kwargs)

        self.text = text
        self.font_size = font_sz
        self.font_name = font_name
        self.size = (0.45*w, 0.25*h)
        if self.text == 'Learning Mode':
            self.pos = (0.25*w, 0.3*h)
        else:
            self.pos = (0.25*w, 0.05*h)
        self.background_normal = 'assets/button.png'
        self.background_down = 'assets/button_down.png'
    
    def on_layout(self, win_size):
        w, h = win_size
        self.size = (0.45*w, 0.25*h)
        if self.text == 'Learning Mode':
            self.pos = (0.25*w, 0.3*h)
        else:
            self.pos = (0.25*w, 0.05*h)


class LevelButton(Button):
    '''
    Extension of the Kivy Button class.
    '''
    def __init__(self, text, r, c, **kwargs):
        super(LevelButton, self).__init__(**kwargs)

        self.text = text
        self.font_size = font_sz/2
        self.font_name = font_name
        self.r = r
        self.c = c
        self.size = (0.2*w, 0.15*h)
        self.pos = (0.2*self.c*w+0.1*w, 0.2*(3-self.r)*h+0.1*h)
        self.halign = 'center'
        self.background_normal = 'assets/button{}.png'.format(str(c))
        self.background_down = 'assets/button{}_down.png'.format(str(c))
        self.background_disabled_normal = 'assets/button{}_disabled.png'.format(str(c))
    
    def on_layout(self, win_size):
        w, h = win_size
        self.size = (0.2*w, 0.15*h)
        self.pos = (0.2*self.c*w+0.1*w, 0.2*(3-self.r)*h+0.1*h)

class ReturnToButton(Button):
    '''
    Extension of the Kivy Button class.
    '''
    def __init__(self, text, **kwargs):
        super(ReturnToButton, self).__init__(**kwargs)
        self.text = text
        self.font_size = font_sz/2
        self.font_name = font_name
        self.size = (0.35*w, 0.15*h)
        self.pos = (0.05*w, 0.05*h)
        self.background_normal = 'assets/button.png'
        self.background_down = 'assets/button_down.png'
    
    def on_layout(self, win_size):
        w, h = win_size
        self.size = (0.35*w, 0.15*h)
        self.pos = (0.05*w, 0.05*h)
        
class HelpButton(Button):
    '''
    Extension of the Kivy Button class.
    '''
    def __init__(self, mode, **kwargs):
        super(HelpButton, self).__init__(**kwargs)
        self.text = ""
        self.size = (metrics.dp(25), metrics.dp(25))
        self.pos = (0.9*w, 0.1*h)
        self.background_normal = "assets/help.png"
        self.background_down = "assets/help_down.png"
        self.mode = mode
        self.overlay = HelpDisplay(self.mode)
        self.active = False

    def on_layout(self, win_size):
        w, h = win_size
        self.size = (metrics.dp(25), metrics.dp(25))
        self.pos = (0.9*w, 0.1*h)

    def on_release(self):
        self.active = not self.active

### DISPLAYS

class VideoDisplay(Rectangle):
    def __init__(self, vid_src, position, **kwargs):
        super(VideoDisplay, self).__init__(**kwargs)
        self.position = position
        self.video = VideoHandler(vid_src)
        self.size = (0.5*w,0.375*h)
        self.move_to(position)
    
    def move_to(self, position):
        self.position = position
        # TODO scale display to preserve 16:9 ratio
        if position == 'right':
            # Right side
            self.pos = (0.5*w, 0.3*h)
        elif position == 'left':
            # Left side
            self.pos = (0, 0.3*h)
        else:
            # Center
            self.pos = (0.25*w, 0.3*h)

    def on_update(self):
        frame = self.video.get_frame()
        if frame is not None:
            buf = cv2.flip(frame, 0)
            buf = cv2.flip(buf, 1)
            buf = buf.tostring()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.texture = texture
            return True
    
    def on_layout(self, win_size):
        w, h = win_size
        self.size = (0.5*w,0.375*h)
        self.move_to(self.position)
    
    def load_source(self, vid_src):
        self.video.load_source(vid_src)
        


class HelpDisplay(InstructionGroup):
    '''
    Help Overlay.
    |---------------------|
    |mode                 |
    |   (O   O   O   O)   |
    |    O   O   O   O    |
    |    O   O   O   O    |
    |return           help|
    |---------------------|
    '''
    def __init__(self, mode):
        super(HelpDisplay, self).__init__()
        self.mode = mode
        
        # Start levels
        self.start_box_color = Color(0,1,0,0.2)
        self.start_box = Rectangle(
            pos = (0.1*w, 0.7*h),
            size = (0.8*w, 0.2*h)
        )
        self.start_text_color = Color(0,1,0,0.8)
        if mode == 'lmode':
            start_text = "Start off with these levels"
            cpos = (0.75*w, 0.88*h)
        elif mode == 'gmode':
            start_text = "Complete the learning mode to unlock the first level"
            cpos = (0.6*w, 0.88*h)
        self.start_text = CLabelRect(
            text=start_text,
            font_size=font_sz/4,
            font_name=font_name,
            cpos=cpos
        )
        self.add(self.start_box_color)
        self.add(self.start_box)
        self.add(self.start_text_color)
        self.add(self.start_text)
        
        # Locked levels
        self.locked_box_color = Color(1,1,0,0.2)
        self.locked_box = Rectangle(
            pos = (0.1*w, 0.2*h),
            size = (0.8*w, 0.5*h)
        )
        self.locked_text_color = Color(1,1,0,0.8)
        if mode == 'lmode':
            locked_text = "Complete the easier levels to unlock new ones"
        elif mode == 'gmode':
            locked_text = "Pass the easier level to unlock the next one"
        self.locked_text = CLabelRect(
            text = locked_text,
            font_size = font_sz/4,
            font_name = font_name,
            cpos = (0.65*w, 0.25*h)
        )
        self.add(self.locked_box_color)
        self.add(self.locked_box)
        self.add(self.locked_text_color)
        self.add(self.locked_text)
        
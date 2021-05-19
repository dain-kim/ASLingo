import numpy as np
from kivy import metrics
from kivy.core.window import Window
from kivy.uix.button import Button

font_sz = metrics.dp(50)
font_name = "AtlantisInternational"
w, h = Window.size


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
    def __init__(self, **kwargs):
        super(HelpButton, self).__init__(**kwargs)
        self.text = ""
        self.size = (metrics.dp(25), metrics.dp(25))
        self.pos = (0.9*w, 0.1*h)
        self.background_normal = "assets/help.png"
        self.background_down = "assets/help_down.png"
        
    def on_layout(self, win_size):
        w, h = win_size
        self.size = (metrics.dp(25), metrics.dp(25))
        self.pos = (0.9*w, 0.1*h)

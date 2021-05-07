import sys, os
sys.path.insert(0, os.path.abspath('..'))

from core import BaseWidget, run, lookup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label


class ParamSlider(GridLayout):
    """
    Creates a slider for adjusting a parameter.

    Slider layout has 3 columns. Ratio is 3:6:1
    
    | param label | slider | param value |

    """

    def __init__(self, parameter, default, callback=None):
        super(ParamSlider, self).__init__()

        self.cols = 3
        self.callback = callback

        self.name = parameter['name']
        self.label = parameter['label']
        self.min = parameter['min']
        self.max = parameter['max']
        self.step = parameter['step']

        # param label
        self.param_label = Label(text=self.label, font_size=20, size_hint_x=.3, on_texture=self.change_font_size)
        self.add_widget(self.param_label)

        # slider
        self.slider = Slider(min=self.min, max=self.max, value=self.clip_value(default), step=self.step, size_hint_x=.6, cursor_size=('20sp','20sp'), cursor_image='slider2.png')
        self.add_widget(self.slider)

        # param value
        self.param_value = Label(text=str(self.slider.value), font_size=20, size_hint_x=.1) 
        self.add_widget(self.param_value)

        self.slider.bind(value=self.on_value)

    def on_value(self, slider, value):
        value = self.clip_value(value)
        # update slider text
        self.param_value.text = str(value)
        return self.callback(self.name, value, self.label)

    def set_value(self, value):
        self.slider.value = self.clip_value(value)

    def clip_value(self, value):
        # temporary solution to prevent floating point error / trailing 0s
        if type(self.step) == int:
            return round(value)
        else:
            return round(value, 1)

    def change_font_size(self, size):
        self.param_label.font_size = size
        self.param_value.font_size = size


if __name__ == "__main__":
    run(ParamSlider)
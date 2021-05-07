#####################################################################
#
# core.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################


import os
os.environ["KIVY_NO_ARGS"] = "1"
import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.clock import Clock
import traceback


class BaseWidget(Widget):
    """A subclass of `kivy.uix.widget.Widget` that adds useful core functionality. To use, make your main app
    class a subclass of `BaseWidget`. You can define optional class methods (those beginning with `on_`) which 
    will get called based on particular events.    
    """

    def __init__(self, **kwargs):
        super(BaseWidget, self).__init__(**kwargs)

        # keyboard up / down messages
        self.down_keys = []
        kb = Window.request_keyboard(target=self, callback=None)
        kb.bind(on_key_down=self._key_down)
        kb.bind(on_key_up=self._key_up)

        # get called when app is about to shut down
        Window.bind(on_close=self._close)

        # create a clock to poll us every frame
        Clock.schedule_interval(self._update, 0)

        # window resizing variables
        self.window_size = (0, 0)
    
    def get_mouse_pos(self):
        """
        :returns: the current mouse position as ``[x, y]``.
        """

        return Window.mouse_pos

    def on_key_down(self, keycode, modifiers):
        """Override to receive keydown events.

        :param keycode: ``[ascii-code, key]`` ascii-code is an int, and key is a string. 
            Example: [49, '1'] when the 1 key is pressed.

        :param modifiers: a list of held-down modifier keys, like 'shift', 'ctrl', 'alt', 'meta'
        """
        pass

    def on_key_up(self, keycode):
        """Override to receive keyup events.

        :param keycode: ``[ascii-code, key]`` ascii-code is an int, and key is a string. 
            Example: [49, '1'] when the 1 key is released.

        """
        pass

    def on_close(self):
        """Override to get notified when window (and app) is about to close.
        """
        pass

    def on_update(self):
        """Override to get called every graphics frame update, typically around 60 times per second.
        """
        pass

    def on_layout(self, win_size):
        """Override to get notified when the main window just got resized.
        
        :param win_size: ``[width, height]`` - the new window size

        """
        pass

    def _key_down(self, keyboard, keycode, text, modifiers):
        if not keycode[1] in self.down_keys:
            self.down_keys.append(keycode[1])
            self.on_key_down(keycode, modifiers)

    def _key_up(self, keyboard, keycode):
        if keycode[1] in self.down_keys:
            self.down_keys.remove(keycode[1])
            self.on_key_up(keycode)

    def _close(self, *args):
        self.on_close()

    def _update(self, dt):
        self.on_update()

        # calls self.on_layout() if window size has changed
        if Window.size != self.window_size:
            self.window_size = Window.size
            self.on_layout(self.window_size)


# to guarantee a termination/shutdown function being called at the end of the
# app's lifetime, you can register the function by calling register_terminate_func.
# it will get called at the end, even if the app crashed.
g_terminate_funcs = []
def register_terminate_func(f):
    global g_terminate_funcs
    g_terminate_funcs.append(f)

def run(widget, pos=(0,0), fullscreen=False):
    """
    Used to create the main widget and run the application.

    :param widget: the `Widget`-derived instance for the top-level / main Window.

    :param pos: location of Window on the desktop (default = (0,0))

    :param fullscreen: if `True`, will run the app in full-screen mode. Check `Window.size` 
        to find the actual window size.
    """

    if fullscreen:
        Window.fullscreen = 'auto'

    Window.left = pos[0]
    Window.top = pos[1]

    class MainApp(App):
        def build(self):
            return widget

    try:
        MainApp().run()
    except:
        traceback.print_exc()

    global g_terminate_funcs
    for t in g_terminate_funcs:
        t()


def lookup(k, keys, values):
    """
    Look up a key in a list of keys, and returns the corresponding item from the values list.

    :param k: an item that should be found in the list **keys**

    :param keys: a list of items

    :param values: the list of return values that correspond to the list of **keys**. The length of 
        **values** and **keys** is expected to be the same.

    :returns: The *nth* item in **values** where *n* is the index of **k** in the list **keys**.
    
    Example: ``lookup('s', 'asdf', (4,5,6,7))`` will return ``5``.
    """

    if k in keys:
        idx = keys.index(k)
        return values[idx]
    else:
        return None

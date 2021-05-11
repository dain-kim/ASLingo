# screen.py

from .core import BaseWidget, run

from kivy.clock import Clock as kivyClock
from kivy.uix.widget import Widget


class Screen(Widget):
    def __init__(self, name, always_update = False, **kwargs):
        """A screen object, similar to BaseWidget, but intended to be used with ScreenManager
        for managing an app with multiple screens.

        :param name: the name of this screen. Must be unique across all screens.
        :param always_update: if True, on_update() is called all the time, even if this Screen is not active
        """

        super(Screen, self).__init__(**kwargs)
        self.name = name
        self.always_update = always_update
        self.manager = None

    def switch_to(self, screen_name):
        """Switches to from the current screen to a different screen.

        :param screen_name: the name of the screen 
        """
        self.manager.switch_to(screen_name)


    def on_key_down(self, keycode, modifiers):
        """Override to receive keydown events. Only called when active.

        :param keycode: ``[ascii-code, key]`` ascii-code is an int, and key is a string. 
            Example: [49, '1'] when the 1 key is pressed.

        :param modifiers: a list of held-down modifier keys, like 'shift', 'ctrl', 'alt', 'meta'
        """
        pass

    def on_key_up(self, keycode):
        """Override to receive keyup events. Only called when active.

        :param keycode: ``[ascii-code, key]`` ascii-code is an int, and key is a string. 
            Example: [49, '1'] when the 1 key is released.

        """
        pass

    def on_update(self):
        """Override to get called every graphics frame update, typically around 60 times per second.
        Called when active, or if self.always_update == True.
        """
        pass

    def on_layout(self, win_size):
        """Override to get notified when the main window just got resized. Called when active or inactive.
        
        :param win_size: ``[width, height]`` - the new window size

        """
        pass


    def on_enter(self):
        """Override to get called when this screen is about to become active."""
        pass

    def on_exit(self):
        """Override to get called when this screen is about to become inactive."""
        pass


class ScreenManager(BaseWidget):
    def __init__(self):
        """Derives from BaseWidget. Use this as the MainWidget to manage multiple Screens.
        Call :meth:`add_screen` with all Screen subclasses. Only one Screen can be active. 
        A Screen is made active by calling :meth:`switch_to`."""
        super(ScreenManager, self).__init__()

        self.screens = []
        self.cur_screen = None

    def add_screen(self, screen):
        """Register a screen with the ScreenManager. The first screen to be added 
        will become the current active screen.

        :param screen: an object inherited from ``Screen``.

        """
        set_current = len(self.screens) == 0

        screen.manager = self
        self.screens.append(screen)

        if set_current:
            self.switch_to(screen.name)

    def switch_to(self, screen_name):
        """Switches to from the current screen to a different screen.

        :param screen_name: the name of the screen 
        """
        kivyClock.schedule_once(lambda dt: self._switch_to(screen_name))

    def on_key_down(self, keycode, modifiers):
        ""
        if self.cur_screen:
            self.cur_screen.on_key_down(keycode, modifiers)

    def on_key_up(self, keycode):
        ""
        if self.cur_screen:
            self.cur_screen.on_key_up(keycode)

    def on_layout(self, win_size):
        ""
        for s in self.screens:
            s.on_layout(win_size)

    def on_update(self):
        ""
        for s in self.screens:
            if s == self.cur_screen or s.always_update:
                s.on_update()

    def _switch_to(self, screen_name):
        if self.cur_screen:
            self.cur_screen.on_exit()
            self.remove_widget(self.cur_screen)

        next_screen = [s for s in self.screens if s.name == screen_name]
        if next_screen:
            self.cur_screen = next_screen[0]
            self.cur_screen.on_enter()
            self.add_widget(self.cur_screen)
        else:
            raise Exception('Error: Screen name {} not found'.format(screen_name))

    def get_screen(self, screen_name):
        next_screen = [s for s in self.screens if s.name == screen_name]
        if next_screen:
            return next_screen[0]
        else:
            raise Exception('Error: Screen name {} not found'.format(screen_name))

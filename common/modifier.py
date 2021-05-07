#####################################################################
#
# modifier.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

from kivy.core.window import Window
import numpy as np
from collections import namedtuple

# Add a modifer with add_modifier():
   # key - keyboard key to activate (ie, 'a')
   # name - name of the property
   # values - list of values to choose from (ie, (1,2,3,4))
   # func - function to call with one of the values given.
class Modifier(object):
    """
    Lets the client modify a value and apply that value to a function by holding
    down a particular keyboard key and moving the mouse up/down.

    Requires that :meth:`on_key_down`, :meth:`on_key_up`, and :meth:`on_update` be called.
    """
    def __init__(self):
        super(Modifier, self).__init__()
        self.mods = {}
        self.cur_key = None
        self.pos = None

    def add(self, key, name, values, func):
        """
        Adds a modifier.

        :param key: Keyboard key (eg, 'a') that will activate the modifier.
        :param name: Name of the property.
        :param values: List of values to choose from (eg, (1,2,3,4))
        :param func: Function to call with the appropriate given value.
        """
        self.mods[key] = _Mod(name, values, func)
        self.cur_key = None
        self.pos = None

    def on_key_down(self, key):
        """
        Should be called when a key is pressed. Checks if key is a modifier.

        :param key: The key that was pressed.
        """
        if key in list(self.mods.keys()):
            self.cur_key = key
            self.pos = Window.mouse_pos[1]

    def on_key_up(self, key):
        """
        Should be called when a key is lifted. Deactivates modifier if necessary.

        :param key: The key that was lifted.
        """
        if key == self.cur_key:
            self.cur_key = None
            self.pos = None

    def on_update(self):
        """
        Should be called on every update. Detects changes in mouse position
        if a modifier is active.
        """
        if self.cur_key:
            p = Window.mouse_pos[1]
            delta = p - self.pos
            if delta > 10:
                self._change_idx(1)
                self.pos = p
            elif delta < -10:
                self._change_idx(-1)
                self.pos = p

    def get_txt(self):
        """
        :returns: A text list of the modifiers, their names, and their current values.
            An active modifier will be displayed with a '>' at the beginning of its row.
        """
        txt = ''
        for k in list(self.mods.keys()):
            active = '> ' if k == self.cur_key else '   '
            mod = self.mods[k]
            txt += '%s[%s] %s: %s\n' % (active, k, mod.name, str(mod.values[mod.idx]))
        return txt

    def _change_idx(self, d):
        mod = self.mods[self.cur_key]
        old_idx = mod.idx
        mod.idx = int(np.clip(mod.idx + d, 0, len(mod.values) - 1))
        if old_idx != mod.idx:
            mod.func(mod.values[mod.idx])

class _Mod(object):
    def __init__(self, name, values, func):
        super(_Mod, self).__init__()
        self.name = name
        self.values = values
        self.func = func
        self.idx = 0

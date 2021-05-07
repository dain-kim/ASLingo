#####################################################################
#
# keydisplay.py
#
# Copyright (c) 2020, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

from types import SimpleNamespace

from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Rectangle, Line
from kivy.graphics.instructions import InstructionGroup
from kivy import metrics

from .gfxutil import CLabelRect


kSpecialKeys = {
    'tab': 'TAB',
    'capslock': 'CAPS',
    'shift': 'SHIFT',
    'lctrl': 'CTRL',
    'alt': 'ALT',
    'super': 'CMD',
    'alt-gr': 'ALT',
    'rctrl': 'CTRL',
    'spacebar': 'SPACE',
    'rshift': 'SHIFT',
    'enter': 'ENTER',
    'backspace': 'BKSP',
    'delete': 'DEL',
    'end': 'END',
    'home': 'HOME',
    'pagedown': 'PG-DN',
    'pageup': 'PG-UP',
    'left': '<=',
    'down': 'DOWN',
    'right': '=>',
    'up': 'UP',
    'numpadenter': 'NP-ENT',
    'numpadadd': 'NP+',
    'numpadsubstract': 'NP-',
    'numpadmul': 'NP*',
    'numpaddivide': 'NP/',
    'numlock': 'N-LCK',
    'numpad0': 'NP0',
    'numpad1': 'NP1',
    'numpad2': 'NP2',
    'numpad3': 'NP3',
    'numpad4': 'NP4',
    'numpad5': 'NP5',
    'numpad6': 'NP6',
    'numpad7': 'NP7',
    'numpad8': 'NP8',
    'numpad9': 'NP9',
    'numpaddecimal': 'NP.',
}

class KeyDisplay(Widget):
    def __init__(self, **kwargs):
        super(KeyDisplay, self).__init__(**kwargs)

        print(self.pos)
        x = self.pos[0]
        y = self.pos[1]
        sz = metrics.pt(21)
        sz2 = metrics.pt(21) * 2.5
        gap = metrics.mm(2)  # 2 millimeters

        # print(metrics.pt(21), metrics.sp(21), metrics.dp(21), metrics.mm(10))

        # keyboard up / down messages
        self.active_keys = {}
        self.slots = []
        for i in range(5):
            self.slots.append(SimpleNamespace(icon=None, pos=(x + (gap+sz)*i, y + gap+sz), size=(sz,sz)))
        self.meta_slots = []
        for i in range(5):
            self.meta_slots.append(SimpleNamespace(icon=None, pos=(x + (gap+sz2)*i, y), size=(sz2,sz)))

        kb = Window.request_keyboard(target=self, callback=None)
        kb.bind(on_key_down=self._key_down)
        kb.bind(on_key_up=self._key_up)

    def _key_down(self, keyboard, keycode, text, modifiers):
        k = keycode[1]
        if k in self.active_keys:
            return

        if k in kSpecialKeys:
            slots = self.meta_slots
            txt = kSpecialKeys[k]
        else:
            slots = self.slots
            txt = k.upper()

        # find a free slot:
        free_slots = [x for x in slots if x.icon is None]
        if not free_slots:
            print('ran out of slots to display Key')
            return

        slot = free_slots[0]
        icon = KeyIcon(txt, slot.pos, slot.size)
        self.canvas.add(icon)
        slot.icon = icon
        self.active_keys[k] = slot

    def _key_up(self, keyboard, keycode):
        k = keycode[1]
        if k not in self.active_keys:
            return

        slot = self.active_keys[k]
        self.canvas.remove(slot.icon)
        slot.icon = None
        del self.active_keys[k]


class KeyIcon(InstructionGroup):
    def __init__(self, txt, pos, size):
        super(KeyIcon, self).__init__()

        label = CLabelRect(cpos = pos, text=txt)
        self.add(label)
        x,y = pos
        hw = size[0] // 2
        hh = size[1] // 2
        box = Line(points=[x-hw,y-hh, x-hw,y+hh, x+hw,y+hh, x+hw,y-hh, x-hw,y-hh], 
                   width=metrics.mm(.25))
        self.add(box)






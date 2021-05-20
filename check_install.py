import sys, os
# sys.path.insert(0, os.path.abspath('..'))

import importlib
from importlib.metadata import version
import platform
import os.path

PY_TGT_VERSION = (3,8)


gErrors = []
def error(e):
    print(e)
    global gErrors
    gErrors.append(e)

def print_errors():
    if not gErrors:
        print('\nEverything looks good.')
    else:
        print('\nErrors found:')
        for e in gErrors:
            print(e)

def check(cond, txt):
    if cond:
        print(txt, '[OK]')
    else:
        error(txt + '[FAILURE]')

def check_module(mod, version_check=None):
    print('\nChecking', mod)
    try:
        m = importlib.import_module(mod)
        if version_check:
            if mod == 'sklearn':
                mod = 'scikit-learn'
            assert version(mod) == version_check, f"{mod} version mismatch (should be {version_check}, but is {version(mod)})"
        print(m, '[OK]')
    except Exception as e:
        error(str(e) + ' [FAILURE]')


def check_kivy_window():
    try:
        import kivy
        from kivy.app import App
        from kivy.uix.widget import Widget
        from kivy.uix.label import Label
        from kivy.core.window import Window

        class TestWidget(Widget):
            def __init__(self, **kwargs):
                super(TestWidget, self).__init__(**kwargs)
            
                # label with text message
                label = Label(text="Kivy Window Test.\npress escape to exit", 
                    pos=(Window.width / 2. , Window.height / 2), font_size='20sp')
                self.add_widget(label)

                # keyboard key binding
                kb = Window.request_keyboard(target=self, callback=None)
                kb.bind(on_key_down=self._key_down)
                
                if platform.system() in ('Linux', 'Windows'):
                    error("You seem to be on Linux or Windows. This app has only been tested on a Mac, so the display may not render as intended. [WARNING]")
                elif Window.size != (1600,1200):
                    print('Window size', Window.size)
                    error("You seem to be on an older Mac OS version. This app has only been tested on Catalina 10.15, so the display may not render as intended. [WARNING]")
    

            def _key_down(self, keyboard, keycode, text, modifiers):
                if keycode[1] == 'escape':
                    print(keycode[1])
                    App.get_running_app().stop()

        class MainApp(App):
            def build(self):
                return TestWidget()

        MainApp().run()
    except Exception as e:
        error(str(e) + '[FAILURE]')


# Check python version
check(sys.version_info[:2] == PY_TGT_VERSION, "Python Version == %d.%d" % PY_TGT_VERSION)

check_module('numpy')
check_module('cv2')
check_module('mediapipe', "0.8.3.1")
check_module('pandas')
check_module('jupyter')
check_module('matplotlib')
check_module('sklearn', "0.24.1")
check_module('kivy', "2.0.0")
check_kivy_window()

print_errors()

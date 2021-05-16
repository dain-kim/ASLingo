from common.core import run
from common.screen import ScreenManager
from screens import IntroScreen, LearningScreen, GameScreen, LmodeMainScreen
from webcam_handler import WebcamHandler


if __name__ == "__main__":
    # Create the Kivy screen manager
    sm = ScreenManager()
    webcam = WebcamHandler()

    def level_switch_handler(mode, level, difficulty):
        callback_screen = sm.get_screen(mode)
        callback_screen.set_level(level, difficulty)

    def get_level(mode):
        return 'todo'

    # Add all screens to the manager. The first screen added is the current screen.
    sm.add_screen(IntroScreen(name='intro'))
    sm.add_screen(LmodeMainScreen(level_switch_callback=level_switch_handler, name='lmode_main'))
    sm.add_screen(LearningScreen(webcam, name='lmode'))
    sm.add_screen(GameScreen(webcam, name='gmode'))

    run(sm)


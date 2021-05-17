from common.core import run
from common.screen import ScreenManager
from screens import IntroScreen, LmodeMainScreen, GmodeMainScreen, LearningScreen, GameScreen
from webcam_handler import WebcamHandler
from levels import Level


if __name__ == "__main__":
    # Create the Kivy screen manager
    sm = ScreenManager()
    webcam = WebcamHandler()
    # global var that changes
    # app_level = Level(mode='lmode',letter_set=0,difficulty=0)

    def enter_level(level):
        # global app_level
        # app_level = level
        sm.get_screen(level.mode).set_level(level)
        sm.switch_to(level.mode)

    # def get_level():
    #     global app_level
    #     return app_level

    # Add all screens to the manager. The first screen added is the current screen.
    sm.add_screen(IntroScreen(name='intro'))
    sm.add_screen(LmodeMainScreen(enter_level=enter_level, name='lmode_main'))
    sm.add_screen(GmodeMainScreen(enter_level=enter_level, name='gmode_main'))
    sm.add_screen(LearningScreen(webcam, name='lmode'))
    sm.add_screen(GameScreen(webcam, name='gmode'))
    
    run(sm)


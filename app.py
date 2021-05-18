from common.core import run
from common.screen import ScreenManager
from screens import IntroScreen, LmodeMainScreen, GmodeMainScreen, LearningScreen, GameScreen, TransitionScreen
from webcam_handler import WebcamHandler
from levels import Level
from kivy.core.window import Window


# Create the Kivy screen manager
sm = ScreenManager()
webcam = WebcamHandler()

def enter_level(level):
    sm.get_screen(level.mode).set_level(level)
    sm.switch_to(level.mode)

# Add all screens to the manager. The first screen added is the current screen.
sm.add_screen(IntroScreen(name='intro'))
sm.add_screen(LmodeMainScreen(enter_level=enter_level, name='lmode_main'))
sm.add_screen(GmodeMainScreen(enter_level=enter_level, name='gmode_main'))
sm.add_screen(LearningScreen(webcam, name='lmode'))
sm.add_screen(GameScreen(webcam, name='gmode'))
sm.add_screen(TransitionScreen(name='transition'))

# Window.fullscreen = 'auto'

run(sm)


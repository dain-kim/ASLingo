import sys
from common.core import run
from common.screen import ScreenManager
from screens import IntroScreen, LmodeMainScreen, GmodeMainScreen, LearningScreen, GameScreen, TransitionScreen
from webcam_handler import WebcamHandler
from levels import Level
from kivy.core.window import Window

if __name__ == "__main__":
    # if len(sys.argv) > 1 and sys.argv[1] == 'godmode':
    #     UNLOCK_ALL = True
    # todo rename
    godmode = (len(sys.argv) > 1 and 'godmode' in sys.argv[1])
    # print('master key', godmode)
    # Create the Kivy screen manager
    sm = ScreenManager()
    webcam = WebcamHandler()

    def enter_level(level):
        sm.get_screen(level.mode).set_level(level)
        sm.switch_to(level.mode)
    
    def send_summary(game_summary):
        sm.get_screen('transition').get_summary(game_summary)
    
    def unlock_next():
        sm.get_screen('gmode').unlock_next_levels()

    # Add all screens to the manager. The first screen added is the current screen.
    sm.add_screen(IntroScreen(name='intro'))
    sm.add_screen(LmodeMainScreen(enter_level=enter_level, name='lmode_main', channel=godmode))
    sm.add_screen(GmodeMainScreen(enter_level=enter_level, name='gmode_main', channel=godmode))
    sm.add_screen(LearningScreen(webcam, name='lmode'))
    sm.add_screen(GameScreen(webcam, send_summary=send_summary, name='gmode'))
    sm.add_screen(TransitionScreen(unlock_next=unlock_next, name='transition'))

    # Window.fullscreen = 'auto'

    run(sm)


from common.core import run
from common.screen import ScreenManager
from screens import IntroScreen, LearningScreen, GameScreen
from evaluate_sign import WebcamHandler


if __name__ == "__main__":
    # Create the Kivy screen manager
    sm = ScreenManager()
    webcam = WebcamHandler()

    # Add all screens to the manager. The first screen added is the current screen.
    sm.add_screen(IntroScreen(name='intro'))
    sm.add_screen(LearningScreen(webcam, name='learning'))
    sm.add_screen(GameScreen(webcam, name='game'))

    run(sm)


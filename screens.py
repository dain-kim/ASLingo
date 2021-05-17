from common.screen import Screen
from common.gfxutil import topleft_label, resize_topleft_label, CLabelRect
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy import metrics
import cv2
import string
import numpy as np
from levels import Level

font_sz = metrics.dp(50)
button_sz = metrics.dp(100)
set_idx_to_letters = {0: 'ABCDEFG', 1: 'HIJKLMN', 2: 'OPQRST', 3: 'UVWXYZ'}
ALL_LEVELS = {}

def gen_button_text(mode, letter_set, difficulty):
    '''helper function for the LModeMainScreen to get the correct button text'''
    if mode == 'lmode':
        letters = set_idx_to_letters[letter_set]
        if difficulty == 0:
            return 'letters {}-{}'.format(letters[0],letters[-1])
        elif difficulty == 1:
            return 'review {}-{}'.format(letters[0],letters[-1])
        elif difficulty == 2:
            return 'review {}-{}: shuffle'.format(letters[0],letters[-1])
    elif mode == 'gmode':
        return 'TEMP'


class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super(IntroScreen, self).__init__(**kwargs)

        w, h = Window.size

        self.title = CLabelRect(cpos=(w/2, 2*h/3),
                                text="ASLingo",
                                font_size=font_sz*1.8,
                                font_name="AtlantisInternational")
        self.canvas.add(self.title)

        # Buttons for entering learning/game main screen
        self.lmode_button = Button(text='Learning Mode', font_name="AtlantisInternational", font_size=font_sz, size=(0.5*w, 0.15*h), pos=(0.25*w, 0.35*h))
        self.lmode_button.bind(on_release= lambda x: self.switch_to('lmode_main'))
        self.add_widget(self.lmode_button)

        self.gmode_button = Button(text='Game Mode', font_name="AtlantisInternational", font_size=font_sz, size=(0.5*w, 0.15*h), pos=(0.25*w, 0.15*h))
        self.gmode_button.bind(on_release= lambda x: self.switch_to('gmode_main'))
        self.add_widget(self.gmode_button)

    def on_layout(self, win_size):
        w, h = win_size
        self.title.set_cpos((w/2, 2*h/3))
        self.lmode_button.size = (0.5*w, 0.15*h)
        self.lmode_button.pos = (0.25*w, 0.35*h)
        self.gmode_button.size = (0.5*w, 0.15*h)
        self.gmode_button.pos = (0.25*w, 0.15*h)

class LmodeMainScreen(Screen):
    def __init__(self, enter_level, **kwargs):
        super(LmodeMainScreen, self).__init__(**kwargs)
        
        # # Add background image
        # self.background_image = Image(source='level_select.png', pos_hint={'center_x': .5, 'center_y': .5}, size_hint_y=1, allow_stretch=False)
        # self.add_widget(self.background_image)
        # # Add background sound
        # self.audio = Audio(2)
        # self.mixer = Mixer()
        # self.audio.set_generator(self.mixer)
        # self.background_audio = WaveGenerator(WaveFile("./data/howto.wav"), loop=True)
        # self.mixer.add(self.background_audio)
        # self.bg.pause()
        # # Add graphic text
        # self.explain1 = CLabelRect(cpos=(w/2, 0.8*h),
        #                            text="Choose a level",
        #                         font_size=36,
        #                            font_name="AtlantisInternational")
        # self.canvas.add(self.explain1)

        self.info = topleft_label(font_size=font_sz, font_name="AtlantisInternational")
        self.info.text = "Learning Mode\n"
        self.add_widget(self.info)

        w, h = Window.size
        # level transition function
        self.enter_level = enter_level

        # buttons - one to switch back to the intro screen, and one to switch to the end screen.
        self.intro_button = Button(text='Return to Main Screen', font_size=font_sz, font_name="AtlantisInternational", size=(0.5*w, 0.15*h), pos=(0.25*w, 0.05*h))
        self.intro_button.bind(on_release= lambda x: self.switch_to('intro'))
        self.add_widget(self.intro_button)
        
        # self.grid = GridLayout(cols=4, spacing=0, padding=0, size_hint_y = None)
        # self.grid.bind(minimum_height=self.grid.setter('height'))
        
        # Add button for each level
        self.level_buttons = {}  # button_to_level
        # self.levels = {}
        
        # Four sets of letters, three difficulties
        for letter_set in range(4):
            for difficulty in range(3):
                lvl_button = Button(
                    text=gen_button_text('lmode', letter_set, difficulty), 
                    font_size=font_sz/2., 
                    font_name="AtlantisInternational", 
                    size=(0.2*w, 0.15*h), 
                    pos=(0.2*letter_set*w+0.1*w, 0.2*(3-difficulty)*h+0.1*h),
                    # background_normal='bt.png',
                    # background_down = 'bt_down.png',
                    # background_locked_normal='bt.png',
                    # background_locked_down = 'bt_down.png',
                    )
                
                    
                lvl_button.bind(on_release=self.to_level)
                # self.grid.add_widget(lvl_button)
                self.add_widget(lvl_button)
                
                # only first difficulty is unlocked in the beginning
                level = Level(mode='lmode', letter_set=letter_set, difficulty=difficulty, unlocked=(difficulty == 0))
                self.level_buttons[lvl_button] = level
                ALL_LEVELS[('lmode', letter_set, difficulty)] = {'level':level, 'button':lvl_button}
                if not level.unlocked:
                    lvl_button.disabled = True

    def to_level(self, button):
        level = self.level_buttons[button]
        self.enter_level(level)

    def on_key_down(self, keycode, modifiers):
        print(keycode[1])

    def on_update(self):
        # Update screen text
        self.info.text = "Learning Mode\n"

    def on_layout(self, win_size):
        resize_topleft_label(self.info)
        w, h = win_size
        self.intro_button.size = (0.5*w, 0.15*h)
        self.intro_button.pos = (0.25*w, 0.05*h)


class LearningScreen(Screen):
    def __init__(self, webcam, **kwargs):
        super(LearningScreen, self).__init__(**kwargs)
        self.webcam = webcam
        # self.get_level = get_level
        # self.level = self.get_level()
        self.level = Level(mode='lmode',letter_set=0,difficulty=0)
        self.guide_video = cv2.VideoCapture(self.level.vid_src)

        self.info = topleft_label(font_size=font_sz, font_name="AtlantisInternational")
        self.info.text = "Learning Mode\n"
        self.info.text += "Use the keyboard to see a different letter\n"
        self.info.text += "Letter: {}\n".format(self.level.target)

        self.add_widget(self.info)

        w, h = Window.size

        # buttons - one to switch back to the intro screen, and one to switch to the end screen.
        self.intro_button = Button(text='Return to Main Screen', font_size=font_sz, font_name="AtlantisInternational", size=(0.5*w, 0.15*h), pos=(0.25*w, 0.05*h))
        self.intro_button.bind(on_release= lambda x: self.switch_to('intro'))
        self.add_widget(self.intro_button)

        # TODO smarter way of scaling webcam display to preserve 16:9 ratio
        self.webcam_display = Rectangle(pos=(0.5*w, 0.3*h), size=(0.5*w,0.375*h))
        self.canvas.add(self.webcam_display)
        self.guide_video_display = Rectangle(pos=(0, 0.3*h), size=(0.5*w,0.375*h))
        self.canvas.add(self.guide_video_display)
    
    def on_exit(self):
        print('EXITING LEARNING SCREEN')


    def on_key_down(self, keycode, modifiers):
        print(keycode[1])
        if keycode[1] in string.ascii_lowercase:
            # TODO decide whether to keep the keyboard functionality
            # If H+ is pressed in set A-G, what happens?
            if keycode[1].upper() in set_idx_to_letters[self.level.letter_set]:
                if self.level.set_target(keycode[1].upper()):
                    self.guide_video = cv2.VideoCapture(self.level.vid_src)

    def on_update(self):
        # Update guide video display
        if self.guide_video:
            success, frame = self.guide_video.read()
            if success:
                buf1 = cv2.flip(frame, 0)
                buf1 = cv2.flip(buf1, 1)
                buf = buf1.tostring()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.guide_video_display.texture = texture

        # Update webcam display
        frame_info = self.webcam.get_next_frame()
        if frame_info:
            frame, pred, score = frame_info
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.webcam_display.texture = texture
                
            # Update level
            level_update = self.level.on_update(frame_info)
            #TODO better way of doing this
            if level_update == "level complete":
                self.unlock_next_levels()
                self.switch_to('lmode_main')
            elif level_update:
                self.guide_video = cv2.VideoCapture(self.level.vid_src)
        
        # Update screen text
        self.info.text = "Learning Mode\n"
        self.info.text += "Use the keyboard to see a different letter\n"
        self.info.text += "Letter: {}\n".format(self.level.target)
        self.info.text += self.level.feedback

    def on_layout(self, win_size):
        resize_topleft_label(self.info)
        w, h = win_size
        if self.level.difficulty == 0:
            if self.guide_video_display not in self.canvas.children:
                self.canvas.add(self.guide_video_display)
            self.uncenter_webcam()
        else:
            if self.guide_video_display in self.canvas.children:
                print('removing guide video display')
                self.canvas.remove(self.guide_video_display)
            self.center_webcam()
        self.webcam_display.size = (0.5*w,0.375*h)
        self.guide_video_display.pos = (0, 0.3*h)
        self.guide_video_display.size = (0.5*w,0.375*h)
        self.intro_button.size = (0.5*w, 0.15*h)
        self.intro_button.pos = (0.25*w, 0.05*h)

    # def on_enter(self):
    #     app_level = self.get_level()
    #     self.set_level(app_level)

    def set_level(self, level):
        self.level = level
        if self.level.difficulty == 0:
            if self.guide_video_display not in self.canvas.children:
                self.canvas.add(self.guide_video_display)
            self.uncenter_webcam()
            self.guide_video = cv2.VideoCapture(self.level.vid_src)
        else:
            if self.guide_video:
                self.guide_video.release()
            self.guide_video = None
            if self.guide_video_display in self.canvas.children:
                self.canvas.remove(self.guide_video_display)
            self.center_webcam()
    
    def unlock_next_levels(self):
        # if not the final difficulty, unlock the next difficulty
        if self.level.difficulty != 2:
            level_to_unlock = ALL_LEVELS[(self.level.mode, self.level.letter_set, self.level.difficulty+1)]
            level_to_unlock['level'].unlocked = True
            level_to_unlock['button'].disabled = False
        # if final difficulty, unlock corresponding game level
        else:
            level_to_unlock = ALL_LEVELS[('gmode', self.level.letter_set, 0)]
            level_to_unlock['level'].unlocked = True
            level_to_unlock['button'].disabled = False
            # also unlock next set of letters (if any)
            if self.level.letter_set != 3:
                level_to_unlock = ALL_LEVELS[(self.level.mode, self.level.letter_set+1, 0)]
                level_to_unlock['level'].unlocked = True
                level_to_unlock['button'].disabled = False
        
        # print('moving onto the next level...')
        # self.set_level(level_to_unlock['level'])

    def center_webcam(self):
        w,h = Window.size
        self.webcam_display.pos = (0.25*w, 0.3*h)

    def uncenter_webcam(self):
        w,h = Window.size
        self.webcam_display.pos = (0.5*w, 0.3*h)

class GmodeMainScreen(Screen):
    def __init__(self, enter_level, **kwargs):
        super(GmodeMainScreen, self).__init__(**kwargs)
        
        '''
        # Add background image
        self.background_image = Image(source='level_select.png', pos_hint={'center_x': .5, 'center_y': .5}, size_hint_y=1, allow_stretch=False)
        self.add_widget(self.background_image)
        # Add background sound
        self.audio = Audio(2)
        self.mixer = Mixer()
        self.audio.set_generator(self.mixer)
        self.background_audio = WaveGenerator(WaveFile("./data/howto.wav"), loop=True)
        self.mixer.add(self.background_audio)
        self.bg.pause()
        # Add graphic text
        self.explain1 = CLabelRect(cpos=(w/2, 0.8*h),
                                   text="Choose a level",
                                font_size=36,
                                   font_name="AtlantisInternational")
        self.canvas.add(self.explain1)
        '''

        self.info = topleft_label(font_size=font_sz, font_name="AtlantisInternational")
        self.info.text = "Game Mode\n"

        self.add_widget(self.info)

        w, h = Window.size
        # level transition function
        self.enter_level = enter_level

        # buttons - one to switch back to the intro screen, and one to switch to the end screen.
        self.intro_button = Button(text='Return to Main Screen', font_size=font_sz, font_name="AtlantisInternational", size=(0.5*w, 0.15*h), pos=(0.25*w, 0.05*h))
        self.intro_button.bind(on_release= lambda x: self.switch_to('intro'))
        self.add_widget(self.intro_button)
        
        # self.grid = GridLayout(cols=4, spacing=0, padding=0, size_hint_y = None)
        # self.grid.bind(minimum_height=self.grid.setter('height'))
        
        # Add button for each level
        self.level_buttons = {}  # button_to_level
        # self.unlocked = []
        
        # Four rows of three consecutive levels
        for letter_set in range(4):
            for difficulty in range(3):
                lvl_button = Button(
                    text=gen_button_text('gmode',letter_set,difficulty), 
                    font_size=font_sz/2., 
                    font_name="AtlantisInternational", 
                    size=(0.2*w, 0.15*h), 
                    pos=(0.2*letter_set*w+0.1*w, 0.2*(3-difficulty)*h+0.1*h),
                    # background_normal='bt.png',
                    # background_down = 'bt_down.png',
                    # background_locked_normal='bt.png',
                    # background_locked_down = 'bt_down.png',
                    )
                    
                lvl_button.bind(on_release=self.to_level)
                # self.grid.add_widget(lvl_button)
                self.add_widget(lvl_button)
                
                level = Level(mode='gmode', letter_set=letter_set, difficulty=difficulty, unlocked=False)
                self.level_buttons[lvl_button] = level
                ALL_LEVELS[('gmode', letter_set, difficulty)] = {'level':level, 'button':lvl_button}
                if not level.unlocked:
                    lvl_button.disabled = True

    def unlock_next_levels(self):
        # if not the final difficulty, unlock the next difficulty
        if self.level.difficulty != 2:
            level_to_unlock = ALL_LEVELS[(self.level.mode, self.level.letter_set, self.level.difficulty+1)]
            level_to_unlock['level'].unlocked = True
            level_to_unlock['button'].disabled = False

    def to_level(self, button):
        level = self.level_buttons[button]
        self.enter_level(level)

    def on_key_down(self, keycode, modifiers):
        print(keycode[1])

    def on_update(self):
        # Update screen text
        self.info.text = "Game Mode\n"

    def on_layout(self, win_size):
        resize_topleft_label(self.info)
        w, h = win_size
        self.intro_button.size = (0.5*w, 0.15*h)
        self.intro_button.pos = (0.25*w, 0.05*h)


class GameScreen(Screen):
    def __init__(self, webcam, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.webcam = webcam
        # self.get_level = get_level
        # self.level = self.get_level()
        self.level = Level(mode='gmode',letter_set=0,difficulty=0)
        # self.guide_video = cv2.VideoCapture(self.level.vid_src)

        self.info = topleft_label(font_size=font_sz, font_name="AtlantisInternational")
        self.info.text = "Game Mode\n"
        self.info.text += "Spell out the following word\n"
        self.info.text += "Press w to choose another word\n"
        self.info.text += "Word: {}\n".format(self.level.target)
        self.info.text += "Spelled so far: {}\n".format(self.level.target[:self.level._cur_letter_idx])

        self.add_widget(self.info)

        w, h = Window.size

        # buttons - one to switch back to the intro screen, and one to switch to the end screen.
        self.intro_button = Button(text='Return to Main Screen', font_size=font_sz, font_name="AtlantisInternational", size=(0.5*w, 0.15*h), pos=(0.25*w, 0.05*h))
        self.intro_button.bind(on_release= lambda x: self.switch_to('intro'))
        self.add_widget(self.intro_button)

        # TODO smarter way of scaling webcam display to preserve 16:9 ratio
        self.webcam_display = Rectangle(pos=(0.3*w, 0.3*h), size=(0.4*w,0.3*h))
        self.canvas.add(self.webcam_display)
        # self.guide_video_display = Rectangle(pos=(0, 0.3*h), size=(0.5*w,0.375*h))
        # self.canvas.add(self.guide_video_display)

    def on_exit(self):
        print('EXITING GAME SCREEN')

    def on_key_down(self, keycode, modifiers):
        print(keycode[1])
        if keycode[1] == 'w':
            # get new target word
            self.level.set_target(self.level.get_next_target())

    def on_update(self):
        # # Update guide video display
        # if self.guide_video:
        #     success, frame = self.guide_video.read()
        #     if success:
        #         buf1 = cv2.flip(frame, 0)
        #         buf1 = cv2.flip(buf1, 1)
        #         buf = buf1.tostring()
        #         texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        #         texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        #         self.guide_video_display.texture = texture

        # Update webcam display
        frame_info = self.webcam.get_next_frame()
        if frame_info:
            frame, pred, score = frame_info
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.webcam_display.texture = texture
                
            # Update level
            # if self.level.on_update(frame_info):
            #     self.guide_video = cv2.VideoCapture(self.level.vid_src)
            level_update = self.level.on_update(frame_info)
            #TODO better way of doing this
            if level_update == "level complete":
                self.unlock_next_levels()
                self.switch_to('gmode_main')
        
        # Update screen text
        self.info.text = "Game Mode\n"
        self.info.text += "Spell out the following word\n"
        self.info.text += "Press w to choose another word\n"
        self.info.text += "Word: {}\n".format(self.level.target)
        self.info.text += "Spelled so far: {}\n".format(self.level.target[:self.level._cur_letter_idx])
        self.info.text += self.level.feedback

    def on_layout(self, win_size):
        resize_topleft_label(self.info)
        w, h = win_size
        # if self.level.difficulty == 0:
        #     if self.guide_video_display not in self.canvas.children:
        #         self.canvas.add(self.guide_video_display)
        #     self.uncenter_webcam()
        # else:
        #     if self.guide_video_display in self.canvas.children:
        #         print('removing guide video display')
        #         self.canvas.remove(self.guide_video_display)
        #     self.center_webcam()
        self.webcam_display.pos = (0.3*w, 0.3*h)
        self.webcam_display.size = (0.4*w,0.3*h)
        self.intro_button.size = (0.5*w, 0.15*h)
        self.intro_button.pos = (0.25*w, 0.05*h)

    # def on_enter(self):
    #     app_level = self.get_level()
    #     self.set_level(app_level)

    def set_level(self, level):
        self.level = level
        # if self.level.difficulty == 0:
        #     if self.guide_video_display not in self.canvas.children:
        #         self.canvas.add(self.guide_video_display)
        #     self.uncenter_webcam()
        #     self.guide_video = cv2.VideoCapture(self.level.vid_src)
        # else:
        #     if self.guide_video:
        #         self.guide_video.release()
        #     self.guide_video = None
        #     if self.guide_video_display in self.canvas.children:
        #         self.canvas.remove(self.guide_video_display)
        #     self.center_webcam()

    # def center_webcam(self):
    #     w,h = Window.size
    #     self.webcam_display.pos = (0.25*w, 0.3*h)

    # def uncenter_webcam(self):
    #     w,h = Window.size
    #     self.webcam_display.pos = (0.5*w, 0.3*h)




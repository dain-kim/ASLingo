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

def next_alpha(s, alpha_range=None):
    if alpha_range:
        return chr((ord(s.upper())+1 - ord(alpha_range[0])) % len(alpha_range) + ord(alpha_range[0]))
    return chr((ord(s.upper())+1 - 65) % 26 + 65)

def choose_word(word):
    word_bank = ['ANDY','FRIEND','SUNDAY','GUAVA','BANANA','CAT','DOG','HAND']
    word_bank.remove(word)
    return np.random.choice(word_bank)

def gen_button_text(letter_set, difficulty):
    '''helper function for the LModeMainScreen to get the correct button text'''
    letters = set_idx_to_letters[letter_set]
    if difficulty == 0:
        return 'letters {}-{}'.format(letters[0],letters[-1])
    elif difficulty == 1:
        return 'review {}-{}'.format(letters[0],letters[-1])
    elif difficulty == 2:
        return 'review {}-{}: shuffle'.format(letters[0],letters[-1])


# IntroScreen is just like a MainWidget, but it derives from Screen instead of BaseWidget.
# This allows it to work with the ScreenManager system.
class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super(IntroScreen, self).__init__(**kwargs)

        w, h = Window.size

        self.title = CLabelRect(cpos=(w/2, 2*h/3),
                                text="ASLingo",
                                font_size=font_sz*1.8,
                                font_name="AtlantisInternational")
        self.canvas.add(self.title)

        # A button is a widget. It must be added with add_widget()
        # button.bind allows you to set up a reaction to when the button is pressed (or released).
        # It takes a function as argument. You can define one, or just use lambda as an inline function.
        # In this case, the button will cause a screen switch
        self.lmode_button = Button(text='Learning Mode', font_name="AtlantisInternational", font_size=font_sz, size=(0.5*w, 0.15*h), pos=(0.25*w, 0.35*h))
        self.lmode_button.bind(on_release= lambda x: self.switch_to('lmode_main'))
        self.add_widget(self.lmode_button)

        self.gmode_button = Button(text='Game Mode', font_name="AtlantisInternational", font_size=font_sz, size=(0.5*w, 0.15*h), pos=(0.25*w, 0.15*h))
        self.gmode_button.bind(on_release= lambda x: self.switch_to('gmode'))
        self.add_widget(self.gmode_button)

    # on_layout always gets called - even when a screen is not active.
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
        self.unlocked = []
        
        # Four rows of three consecutive levels
        for letter_set in range(4):
            for difficulty in range(3):
                lvl_button = Button(
                    text=gen_button_text(letter_set,difficulty), 
                    font_size=font_sz/2., 
                    font_name="AtlantisInternational", 
                    size=(0.2*w, 0.15*h), 
                    pos=(0.2*letter_set*w+0.1*w, 0.2*(3-difficulty)*h+0.1*h),
                    # background_normal='bt.png',
                    # background_down = 'bt_down.png',
                    # background_locked_normal='bt.png',
                    # background_locked_down = 'bt_down.png',
                    )
                # if (difficulty,letter_set) not in self.unlocked:
                #     lvl_button.disabled = True
                    
                lvl_button.bind(on_release=self.to_level)
                # self.grid.add_widget(lvl_button)
                self.add_widget(lvl_button)
                
                level = Level(mode='lmode', letter_set=letter_set, difficulty=difficulty)
                self.level_buttons[lvl_button] = level
                # lvl_button.bind(on_release= lambda x: self.switch_to('lmode'))

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
    def __init__(self, webcam, get_level, **kwargs):
        super(LearningScreen, self).__init__(**kwargs)
        self.webcam = webcam
        self.get_level = get_level
        self.level = self.get_level()
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


    def on_key_down(self, keycode, modifiers):
        print(keycode[1])
        if keycode[1] in string.ascii_lowercase:
            # TODO decide whether to keep the keyboard functionality
            # If H+ is pressed in set A-G, what happens?
            
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
            if self.level.on_update(frame_info):
                self.guide_video = cv2.VideoCapture(self.level.vid_src)
        
        # Update screen text
        self.info.text = self.info.text = "Learning Mode\n"
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

    def center_webcam(self):
        w,h = Window.size
        self.webcam_display.pos = (0.25*w, 0.3*h)

    def uncenter_webcam(self):
        w,h = Window.size
        self.webcam_display.pos = (0.5*w, 0.3*h)


class GameScreen(Screen):
    def __init__(self, webcam, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.target = 'ANDY'
        self._cur_letter_idx = 0
        self._score_counter = 0
        self._feedback_counter = 0

        self.info = topleft_label(font_size=font_sz, font_name="AtlantisInternational")
        self.info.text = "Game Mode\n"
        self.info.text += "Spell out the following word\n"
        self.info.text += "Press w to choose another word\n"
        self.info.text += "Word: {}\n".format(self.target)
        self.info.text += "Spelled so far: {}\n".format(self.target[:self._cur_letter_idx])

        self.add_widget(self.info)
        self.webcam = webcam
        w, h = Window.size

        # more buttons - one to switch back to the intro screen, and one to switch to the end screen.
        self.intro_button = Button(text='Return to Main Screen', font_name="AtlantisInternational", font_size=font_sz, size=(0.5*w, 0.15*h), pos=(0.25*w, 0.05*h))
        self.intro_button.bind(on_release= lambda x: self.switch_to('intro'))
        self.add_widget(self.intro_button)
        
        # TODO smarter way of scaling webcam display
        self.webcam_display = Rectangle(pos=(0.3*w, 0.3*h), size=(0.4*w,0.3*h))
        self.canvas.add(self.webcam_display)


    def on_key_down(self, keycode, modifiers):
        if keycode[1] == 'w':
            self._score_counter = 0
            self._cur_letter_idx = 0
            self.target = choose_word(self.target)


    def on_layout(self, win_size):
        resize_topleft_label(self.info)
        w, h = win_size
        self.webcam_display.pos = (0.3*w, 0.3*h)
        self.webcam_display.size = (0.4*w,0.3*h)
        self.intro_button.size = (0.5*w, 0.15*h)
        self.intro_button.pos = (0.25*w, 0.05*h)

    def on_update(self):
        # Update screen text
        self.info.text = "Game Mode\n"
        self.info.text += "Spell out the following word\n"
        self.info.text += "Press w to choose another word\n"
        self.info.text += "Word: {}\n".format(self.target)
        self.info.text += "Spelled so far: {}\n".format(self.target[:self._cur_letter_idx])
        if self._feedback_counter > 10:
            self._feedback_counter = 0
        if 0 < self._feedback_counter:
            self.info.text += 'Nice job!'
            self._feedback_counter += 1

        if len(self.target) == self._cur_letter_idx:
            print('Nice job!')
            self._score_counter = 0
            self._feedback_counter = 1
            self._cur_letter_idx = 0
            self.target = choose_word(self.target)

        # Update webcam display
        frame_info = self.webcam.get_next_frame()
        if frame_info:
            frame, pred, score = frame_info
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.webcam_display.texture = texture

            # Check if prediction is correct
            # TODO: more robust way of parsing prediction
            cur_letter = self.target[self._cur_letter_idx]
            if pred.replace('LETTER-','') == cur_letter:
                self._score_counter += 1
            if self._score_counter > 10:
                # move onto next letter
                self._score_counter = 0
                self._cur_letter_idx += 1







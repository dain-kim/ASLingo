from common.screen import Screen
from common.gfxutil import topleft_label, resize_topleft_label, CRectangle, CLabelRect
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Line, Rectangle
from kivy.graphics.instructions import InstructionGroup
from kivy.core.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy import metrics
import cv2
import string
import numpy as np
from levels import Level
import time
from config import ModeButton, LevelButton, ReturnToButton, HelpButton

font_sz = metrics.dp(50)
button_sz = metrics.dp(100)
set_idx_to_letters = {0: 'ABCDEFG', 1: 'HIJKLMN', 2: 'OPQRST', 3: 'UVWXYZ'}
ALL_LEVELS = {}

def gen_button_text(mode, letter_set, difficulty):
    '''helper function for the LModeMainScreen to get the correct button text'''
    letters = set_idx_to_letters[letter_set]
    if mode == 'lmode':
        if difficulty == 0:
            return 'letters {}-{}'.format(letters[0],letters[-1])
        elif difficulty == 1:
            return 'review {}-{}'.format(letters[0],letters[-1])
        elif difficulty == 2:
            return 'shuffle {}-{}'.format(letters[0],letters[-1])
    elif mode == 'gmode':
        if difficulty == 0:
            return '{}-{}\nshort words'.format('A',letters[-1])
        elif difficulty == 1:
            return '{}-{}\nmedium words'.format('A',letters[-1])
        elif difficulty == 2:
            return '{}-{}\nlong words'.format('A',letters[-1])

class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super(IntroScreen, self).__init__(**kwargs)

        w, h = Window.size

        self.title = CLabelRect(cpos=(w/2, 3*h/4),
                                text="ASLingo",
                                font_size=font_sz*1.8,
                                font_name="AtlantisInternational")
        self.canvas.add(self.title)

        # Buttons for entering learning/game main screen
        self.lmode_button = ModeButton('Learning Mode')
        self.lmode_button.bind(on_release=lambda x: self.switch_to('lmode_main'))
        self.add_widget(self.lmode_button)

        self.gmode_button = ModeButton('Game Mode')
        self.gmode_button.bind(on_release=lambda x: self.switch_to('gmode_main'))
        self.add_widget(self.gmode_button)

    def on_layout(self, win_size):
        w, h = win_size
        self.title.set_cpos((w/2, 3*h/4))
        self.lmode_button.on_layout(win_size)
        self.gmode_button.on_layout(win_size)


class LmodeMainScreen(Screen):
    def __init__(self, enter_level, channel, **kwargs):
        super(LmodeMainScreen, self).__init__(**kwargs)
        # level transition function
        self.enter_level = enter_level
        self.godmode = channel
        
        # Main screen text
        self.info = topleft_label(font_size=font_sz, font_name="AtlantisInternational")
        self.info.text = "Learning Mode\n"
        self.add_widget(self.info)

        # Return button
        self.intro_button = ReturnToButton('Return to Main Screen')
        self.intro_button.bind(on_release=lambda x: self.switch_to('intro'))
        self.add_widget(self.intro_button)
        
        # Help button
        self.help_button = HelpButton()
        self.help_button.bind(on_release=self.call_help)
        self.add_widget(self.help_button)
        
        
        # Level button for each level
        self.level_buttons = {}
        
        # Four sets of letters, three difficulties
        for letter_set in range(4):
            for difficulty in range(3):
                level_button = LevelButton(
                    gen_button_text('lmode', letter_set, difficulty), 
                    difficulty, 
                    letter_set)
                level_button.bind(on_release=self.to_level)
                self.add_widget(level_button)
                # self.grid.add_widget(level_button)
                
                # only first difficulty is unlocked in the beginning
                saved_mode = False  # TODO load saved game
                level = Level(
                    mode='lmode', 
                    letter_set=letter_set, 
                    difficulty=difficulty, 
                    unlocked=(difficulty == 0 or saved_mode or self.godmode))
                self.level_buttons[level_button] = level
                ALL_LEVELS[('lmode', letter_set, difficulty)] = {'level':level, 'button':level_button}
                if not level.unlocked:
                    level_button.disabled = True
        
        # self.add_widget(self.grid)

    def to_level(self, button):
        level = self.level_buttons[button]
        self.enter_level(level)
    
    def call_help(self, button):
        print('help!')

    def on_key_down(self, keycode, modifiers):
        print(keycode[1])

    def on_update(self):
        # Update screen text
        self.info.text = "Learning Mode\n"

    def on_layout(self, win_size):
        resize_topleft_label(self.info)
        self.intro_button.on_layout(win_size)
        self.help_button.on_layout(win_size)
        for level_button in self.level_buttons.keys():
            level_button.on_layout(win_size)


class LearningScreen(Screen):
    def __init__(self, webcam, **kwargs):
        super(LearningScreen, self).__init__(**kwargs)
        self.webcam = webcam
        
        self.level = Level(mode='lmode',letter_set=0,difficulty=0)
        self.guide_video = cv2.VideoCapture(self.level.vid_src)

        self.info = topleft_label(font_size=font_sz, font_name="AtlantisInternational")
        self.info.text = set_idx_to_letters[self.level.letter_set] + '\n'
        self.info.text += "Use the keyboard to see a different letter\n"
        self.info.text += "Letter: {}\n".format(self.level.target)

        self.add_widget(self.info)

        self.intro_button = ReturnToButton('Return to Learning Mode')
        self.intro_button.bind(on_release=lambda x: self.switch_to('lmode_main'))
        self.add_widget(self.intro_button)

        w, h = Window.size
        # TODO smarter way of scaling webcam display to preserve 16:9 ratio
        self.webcam_display = Rectangle(pos=(0.5*w, 0.3*h), size=(0.5*w,0.375*h))
        self.canvas.add(self.webcam_display)
        self.guide_video_display = Rectangle(pos=(0, 0.3*h), size=(0.5*w,0.375*h))
        self.canvas.add(self.guide_video_display)
    
    def on_exit(self):
        print('EXITING LEARNING SCREEN')

    def on_key_down(self, keycode, modifiers):
        print(keycode[1])
        if keycode[1] == '1': #TODO temp
            print('manual unlock')
            ALL_LEVELS[(self.level.mode, self.level.letter_set, self.level.difficulty)]['button'].background_normal = 'assets/button{}_down.png'.format(str(self.level.letter_set))
            self.unlock_next_levels()
            self.switch_to('lmode_main')
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
                ALL_LEVELS[(self.level.mode, self.level.letter_set, self.level.difficulty)]['button'].background_normal = 'assets/button{}_down.png'.format(str(self.level.letter_set))
                self.unlock_next_levels()
                self.switch_to('lmode_main')
            elif level_update:
                if self.guide_video:
                    self.guide_video.release()
                self.guide_video = cv2.VideoCapture(self.level.vid_src)
        
        # Update screen text
        self.info.text = set_idx_to_letters[self.level.letter_set] + '\n'
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
        self.intro_button.on_layout(win_size)

    def set_level(self, level):
        self.level = level
        if self.level.difficulty == 0:
            if self.guide_video_display not in self.canvas.children:
                self.canvas.add(self.guide_video_display)
            self.uncenter_webcam()
            if self.guide_video:
                self.guide_video.release()
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
    def __init__(self, enter_level, channel, **kwargs):
        super(GmodeMainScreen, self).__init__(**kwargs)

        # level transition function
        self.enter_level = enter_level
        self.godmode = channel
        
        self.info = topleft_label(font_size=font_sz, font_name="AtlantisInternational")
        self.info.text = "Game Mode\n"
        self.add_widget(self.info)

        self.intro_button = ReturnToButton('Return to Main Screen')
        self.intro_button.bind(on_release=lambda x: self.switch_to('intro'))
        self.add_widget(self.intro_button)
        
        self.help_button = HelpButton()
        self.help_button.bind(on_release=self.call_help)
        self.add_widget(self.help_button)
        
        # Add button for each level
        self.level_buttons = {}  # button_to_level
        
        # Four rows of three consecutive levels
        for letter_set in range(4):
            for difficulty in range(3):
                level_button = LevelButton(
                    gen_button_text('gmode',letter_set,difficulty), 
                    difficulty, 
                    letter_set)
                level_button.bind(on_release=self.to_level)
                self.add_widget(level_button)
                
                saved_mode = False  # TODO load saved game
                level = Level(
                    mode='gmode', 
                    letter_set=letter_set, 
                    difficulty=difficulty, 
                    unlocked=(saved_mode or self.godmode)
                    )
                self.level_buttons[level_button] = level
                ALL_LEVELS[('gmode', letter_set, difficulty)] = {'level':level, 'button':level_button}
                if not level.unlocked:
                    level_button.disabled = True

    def to_level(self, button):
        level = self.level_buttons[button]
        self.enter_level(level)
    
    def call_help(self, button):
        print('help!')

    def on_key_down(self, keycode, modifiers):
        print(keycode[1])

    def on_update(self):
        # Update screen text
        self.info.text = "Game Mode\n"

    def on_layout(self, win_size):
        resize_topleft_label(self.info)
        self.intro_button.on_layout(win_size)
        self.help_button.on_layout(win_size)
        for level_button in self.level_buttons.keys():
            level_button.on_layout(win_size)


class GameScreen(Screen):
    def __init__(self, webcam, send_summary, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.webcam = webcam
        # transition function for sending game summary
        self.send_summary = send_summary
        self.level = Level(mode='gmode',letter_set=0,difficulty=0)
        self.guide_video = None

        self.info = topleft_label(font_size=font_sz, font_name="AtlantisInternational")
        self.info.text = set_idx_to_letters[self.level.letter_set] + '\n'
        self.info.text += "Spell out the following word\n"
        self.info.text += "Press spacebar to skip, h to see hint\n"
        self.info.text += "Word: {}\n".format(self.level.target)
        self.info.text += "Spelled so far: {}\n".format(self.level.target[:self.level._cur_letter_idx])

        self.add_widget(self.info)
        self.start_time = time.time() + 3
        self.bartimer = TimerDisplay()
        self.canvas.add(self.bartimer)
        
        # # Hint popup
        # self.popup = HelpPopup()
        # self.add_widget(self.popup)

        self.gmode_button = ReturnToButton('Return to Game Mode')
        self.gmode_button.bind(on_release=lambda x: self.switch_to('gmode_main'))
        self.add_widget(self.gmode_button)

        w, h = Window.size
        # TODO smarter way of scaling webcam display to preserve 16:9 ratio
        self.webcam_display = Rectangle(pos=(0.3*w, 0.3*h), size=(0.4*w,0.3*h))
        self.canvas.add(self.webcam_display)
        self.guide_video_display = Rectangle(pos=(0.3*w, 0.3*h), size=(0.4*w, 0.3*h))
        # self.canvas.add(self.guide_video_display)

    def on_enter(self):
        # reset timer
        self.start_time = time.time() + 3
        duration = 30. + 15 * (self.level.difficulty)
        self.bartimer.reset(duration)
        if self.guide_video:
            self.guide_video.release()
            self.guide_video = None
        if self.guide_video_display in self.canvas.children:
            self.canvas.remove(self.guide_video_display)
    
    def on_exit(self):
        print('EXITING GAME SCREEN')

    def on_key_down(self, keycode, modifiers):
        print(keycode[1])
        if keycode[1] == 'spacebar':
            # get new target word
            self.level.set_target(self.level.get_next_target())
        if keycode[1] == 'h':
            if self.guide_video:
                self.guide_video.release()
            let = self.level.target[self.level._cur_letter_idx]
            self.guide_video = cv2.VideoCapture('guide_videos/{}.mp4'.format(let))
            self.canvas.add(self.guide_video_display)
            # self.popup.open(self.level.target[self.level._cur_letter_idx])
            # TODO use self.level.vid_src
    
    # def on_key_up(self, keycode):
    #     if keycode[1] == 'h':
    #         self.popup.dismiss()

    def on_update(self):
        # Update time
        time_elapsed = time.time() - self.start_time
        if self.bartimer.on_update(time_elapsed) == 'end of game':
            print('game ended')
            # count how many words were guessed correctly
            level_total = len(self.level.attempted)
            # TODO if hint used, score is docked
            # TODO if word skipped, score is docked
            # TODO calculate and save level score
            # ALL_LEVELS[(self.level.mode, self.level.letter_set, self.letter.difficulty)]['']
            self.send_summary({'correct': level_total})
            if level_total > 0:
                print('UNLOCKING')
                ALL_LEVELS[(self.level.mode, self.level.letter_set, self.level.difficulty)]['button'].background_normal = 'assets/button{}_down.png'.format(str(self.level.letter_set))
                self.unlock_next_levels()
            self.switch_to('transition')
            return
        
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
            else:
                self.guide_video.release()
                self.guide_video = None
                self.canvas.remove(self.guide_video_display)

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
            
        
        # Update screen text
        self.info.text = set_idx_to_letters[self.level.letter_set] + '\n'
        self.info.text += "Spell out the following word\n"
        self.info.text += "Press spacebar to skip, h to see hint\n"
        self.info.text += "Word: {}\n".format(self.level.target)
        self.info.text += "Spelled so far: {}\n".format(self.level.target[:self.level._cur_letter_idx])
        self.info.text += self.level.feedback

    def on_layout(self, win_size):
        resize_topleft_label(self.info)
        self.gmode_button.on_layout(win_size)
        
        w, h = win_size
        self.webcam_display.pos = (0.3*w, 0.3*h)
        self.webcam_display.size = (0.4*w,0.3*h)
        self.guide_video_display.pos = (0.3*w, 0.3*h)
        self.guide_video_display.size = (0.4*w,0.3*h)
        self.bartimer.on_layout(win_size)
        # self.popup.redraw()

    def set_level(self, level):
        self.level = level
    
    def unlock_next_levels(self):
        # if not the final difficulty, unlock the next difficulty
        if self.level.difficulty != 2:
            level_to_unlock = ALL_LEVELS[(self.level.mode, self.level.letter_set, self.level.difficulty+1)]
            level_to_unlock['level'].unlocked = True
            level_to_unlock['button'].disabled = False

class TransitionScreen(Screen):
    def __init__(self, unlock_next, **kwargs):
        super(TransitionScreen, self).__init__(**kwargs)
        self.unlock_next = unlock_next

        w, h = Window.size

        self.title = CLabelRect(cpos=(w/2, 3*h/4),
                                text="Game Summary",
                                font_size=font_sz,
                                font_name="AtlantisInternational")
        self.canvas.add(self.title)
        self.stats = CLabelRect(cpos=(w/2, h/2),
                                text="default",
                                font_size=font_sz/2,
                                font_name="AtlantisInternational")
        self.canvas.add(self.stats)
        
        self.game_summary = ""
        
        self.stars = [
            CRectangle(
                cpos=(0.4*w, 0.3*h),
                csize=((metrics.dp(70), metrics.dp(70))),
                source='assets/star.png'
            ),
            CRectangle(
                cpos=(0.5*w, 0.3*h),
                csize=((metrics.dp(70), metrics.dp(70))),
                source='assets/star.png'
            ),
            CRectangle(
                cpos=(0.6*w, 0.3*h),
                csize=((metrics.dp(70), metrics.dp(70))),
                source='assets/star.png'
            )
        ]
        for star in self.stars:
            self.canvas.add(star)

        self.gmode_button = ReturnToButton('Return to Game Mode')
        self.gmode_button.bind(on_release=lambda x: self.switch_to('gmode_main'))
        self.add_widget(self.gmode_button)

    def on_layout(self, win_size):
        self.gmode_button.on_layout(win_size)
        w, h = win_size
        self.title.set_cpos((w/2, 3*h/4))
        self.stats.set_cpos((w/2, h/2))
        for i,star in enumerate(self.stars):
            star.pos = ((0.4+0.1*i)*w, 0.3*h)
    
    def on_enter(self):
        print('transition')
    
    def get_summary(self, game_summary):
        for i,star in enumerate(self.stars):
            if star in self.canvas.children:
                self.canvas.remove(star)
        count = game_summary['correct']
        # hint = game_summary['hint']
        # skip = game_summary['skip']
        summary_text = f"Correctly spelled: {count} words"
        self.stats.set_text(summary_text)
        for i in range(min(count,3)):
            self.canvas.add(self.stars[i])


class TimerDisplay(InstructionGroup):
    def __init__(self):
        super(TimerDisplay, self).__init__()
        self.duration = 30.
        self.start_x = Window.width*0.2
        self.end_x = Window.width*.85
        self.start_y = Window.height*.2
        self.end_y = Window.height*.25
        
        # Initialize moving timer
        self.color = Color(0,1,0) # start off green
        self.bar = Rectangle(pos=(self.start_x, self.start_y), size=(self.end_x-self.start_x, self.end_y-self.start_y))
        self.add(self.color)
        self.add(self.bar)
        
        self.remaining_time = CLabelRect(cpos=(self.end_x + 50, self.start_y),
                                text=str(int(self.duration)),
                                font_size=(self.end_y-self.start_y)/2,
                                font_name="AtlantisInternational")
        self.add(self.remaining_time)
        
        # Vertical borders
        self.border_left = Line(width=2)
        self.border_mid = Line(width=2)
        self.border_right = Line(width=2)
        self.add(self.border_left)
        self.add(self.border_right)
        self.add(self.border_mid)
        
        # Horizontal borders
        self.border_bot = Line(width=2)
        self.border_top = Line(width=2)
        self.add(self.border_bot)
        self.add(self.border_top)
        
        self.on_layout(Window.size)
    
    def reset(self, duration=30.):
        self.duration = duration
        self.color.rgb = (0,1,0)
        self.bar.size = (self.end_x-self.start_x, self.end_y-self.start_y)
        self.remaining_time.set_text(str(int(self.duration)))

    def get_width(self, time):
        t = (self.end_x - self.start_x) * (1 - time / self.duration)
        return t

    def on_update(self, time_elapsed):
        if time_elapsed > self.duration:
            return 'end of game'

        if time_elapsed >=0:
            # self.nowbar.points = [(self.getXPos(time_elapsed), self.start_y), (self.getXPos(time_elapsed), self.end_y),]
            # self.bar.pos = (self.getXPos(time_elapsed), self.start_y)
            self.bar.size = (self.get_width(time_elapsed), self.end_y-self.start_y)
            # update remaining time
            self.remaining_time.set_text(str(int(self.duration - time_elapsed)))
        
            # update bar timer color
            self.color.rgb = (min(time_elapsed/self.duration*2,1),min(1,(1-time_elapsed/self.duration)*2),0)
        
        
        

    def on_layout(self, win_size):
        self.start_x = win_size[0]*0.2
        self.end_x = win_size[0]*.85
        self.start_y = win_size[1]*.2
        self.end_y = win_size[1]*.25
        # width, height = win_size
        # self.border_left.points = [(width*0.2, height*.9,) ,(width*.2, height*.95)]
        # self.border_right.points=[(width*0.85, height*.9,), (width*.85, height*.95)]
        # self.border_mid.points=[(width*0.525, height*.9,), (width*.525, height*.95)]
        # # self.border_h4.points = [(width*0.2, height*.925,), (width*.85, height*.925)]
        # self.border_bot.points = [(width*0.2, height*.9,), (width*.85, height*.9)]
        # self.border_top.points = [(width*0.2, height*.95,), (width*.85, height*.95)]
        # for gem in self.gems:
        #     gem.on_layout(win_size)
        self.bar.pos=(self.start_x, self.start_y)
        self.border_left.points = [(self.start_x, self.start_y) ,(self.start_x, self.end_y)]
        self.border_mid.points=[((self.start_x + self.end_x)/2, self.start_y), ((self.start_x + self.end_x)/2, self.end_y)]
        self.border_right.points=[(self.end_x, self.start_y), (self.end_x, self.end_y)]
        self.border_bot.points = [(self.start_x, self.start_y), (self.end_x, self.start_y)]
        self.border_top.points = [(self.start_x, self.end_y,), (self.end_x, self.end_y)]
        self.remaining_time.set_cpos((self.end_x + 50, self.start_y))
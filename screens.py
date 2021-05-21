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
import string
import numpy as np
from levels import Level
import time
from config import ModeButton, LevelButton, ReturnToButton, HelpButton, VideoDisplay, TimerDisplay

font_sz = metrics.dp(50)
button_sz = metrics.dp(100)
set_idx_to_letters = {0: 'ABCDEFG', 1: 'HIJKLMN', 2: 'OPQRST', 3: 'UVWXYZ'}
ALL_LEVELS = {}

def get_level(level_id):
    return ALL_LEVELS[level_id]['level']

def get_button(level_id):
    return ALL_LEVELS[level_id]['button']

def gen_button_text(mode, letter_set, difficulty):
    '''helper function for the MainScreen to get the correct level button text'''
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
    '''
    Intro Screen.
    |---------------------|
    |        title        |
    |                     |
    |        lmode        |
    |        gmode        |
    |---------------------|
    '''
    def __init__(self, **kwargs):
        super(IntroScreen, self).__init__(**kwargs)

        w, h = Window.size

        self.title = CLabelRect(cpos=(w/2, 3*h/4),
                                text="ASLingo",
                                font_size=font_sz*1.8,
                                font_name="assets/AtlantisInternational")
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


class MainScreen(Screen):
    '''
    Main Screen.
    |---------------------|
    |mode                 |
    |    O   O   O   O    |
    |    O   O   O   O    |
    |    O   O   O   O    |
    |return           help|
    |---------------------|
    '''
    def __init__(self, enter_level, channel, mode, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        
        # level transition function
        self.enter_level = enter_level
        self.godmode = channel
        self.mode = mode
        
        # Mode text
        self.info = topleft_label(font_size=font_sz, font_name="assets/AtlantisInternational")
        if self.mode == 'lmode':
            self.info.text = "Learning Mode\n"
        elif self.mode == 'gmode':
            self.info.text = "Game Mode\n"
        self.add_widget(self.info)

        # Return button
        self.intro_button = ReturnToButton('Return to Main Screen')
        self.intro_button.bind(on_release=lambda x: self.switch_to('intro'))
        self.add_widget(self.intro_button)
        
        # Help button
        self.help_button = HelpButton(self.mode)
        self.help_button.bind(on_release=self.call_help)
        self.add_widget(self.help_button)
        
        # Level button for each level
        self.level_buttons = {}
        
        # Four sets of letters, three difficulties
        for letter_set in range(4):
            for difficulty in range(3):
                level_button = LevelButton(
                    gen_button_text(self.mode, letter_set, difficulty), 
                    difficulty, 
                    letter_set)
                level_button.bind(on_release=self.to_level)
                self.add_widget(level_button)
                
                saved_mode = False  # TODO load saved game
                # in learning mode, only first difficulty is unlocked in the beginning
                level = Level(
                    mode=self.mode, 
                    letter_set=letter_set, 
                    difficulty=difficulty, 
                    unlocked=(saved_mode or self.godmode or (self.mode,difficulty) == ('lmode',0)))
                self.level_buttons[level_button] = level
                ALL_LEVELS[(self.mode, letter_set, difficulty)] = {'level':level, 'button':level_button}
                if not level.unlocked:
                    level_button.disabled = True

    def to_level(self, button):
        level = self.level_buttons[button]
        self.enter_level(level)
    
    def call_help(self, button):
        if button.active:
            self.canvas.remove(button.overlay)
        else:
            self.canvas.add(button.overlay)

    def on_update(self):
        # Update screen text
        if self.mode == 'lmode':
            self.info.text = "Learning Mode\n"
        elif self.mode == 'gmode':
            self.info.text = "Game Mode\n"

    def on_layout(self, win_size):
        resize_topleft_label(self.info)
        self.intro_button.on_layout(win_size)
        self.help_button.on_layout(win_size)
        for level_button in self.level_buttons.keys():
            level_button.on_layout(win_size)


class LearningScreen(Screen):
    '''
    Learning Screen.
    |---------------------|
    |text                 |
    |----------|----------|
    |guidevideo|  webcam  |
    |----------|----------|
    |return               |
    |---------------------|
    '''
    def __init__(self, webcam, **kwargs):
        super(LearningScreen, self).__init__(**kwargs)
        self.level = Level(mode='lmode',letter_set=0,difficulty=0)

        # Level text
        self.info = topleft_label(font_size=font_sz, font_name="assets/AtlantisInternational")
        self.info.text = set_idx_to_letters[self.level.letter_set] + '\n'
        self.info.text += "Use the keyboard to see a different letter\n"
        self.info.text += "Letter: "
        self.add_widget(self.info)
        
        # Return button
        self.intro_button = ReturnToButton('Return to Learning Mode')
        self.intro_button.bind(on_release=lambda x: self.switch_to('lmode_main'))
        self.add_widget(self.intro_button)

        # Guide video and webcam displays
        w, h = Window.size
        # TODO smarter way of scaling webcam display to preserve 16:9 ratio
        self.webcam = VideoDisplay(0, 'right')
        self.canvas.add(self.webcam)
        self.guide_video = VideoDisplay(self.level.vid_src, 'left')
        self.canvas.add(self.guide_video)
    
    def on_key_down(self, keycode, modifiers):
        if keycode[1] == '1': #TODO temp
            print('manual unlock')
            self.unlock_next_levels()
            self.switch_to('lmode_main')
        # If pressed key is in the letter set and is not the current letter, show video
        if keycode[1] in string.ascii_lowercase:
            if keycode[1].upper() in set_idx_to_letters[self.level.letter_set]:
                if self.level.set_target(keycode[1].upper()):
                    self.guide_video.load_source(self.level.vid_src)
                    # TODO display hint video for review levels

    def on_update(self):
        # Update guide video display
        self.guide_video.on_update()

        # Update webcam display
        frame_info = self.webcam.on_update()
        if frame_info:
            pred, score = frame_info
            
            # Update level
            level_update = self.level.on_update(pred, score)
            #TODO better way of doing this
            if level_update == "level complete":
                self.unlock_next_levels()
                self.switch_to('lmode_main')
            elif level_update:
                self.guide_video.load_source(self.level.vid_src) # TODO maybe not necessary?
        
        # Update screen text
        self.info.text = set_idx_to_letters[self.level.letter_set] + '\n'
        self.info.text += "Use the keyboard to see a different letter\n"
        self.info.text += "Letter: {}\n".format(self.level.target)
        self.info.text += self.level.feedback

    def on_layout(self, win_size):
        resize_topleft_label(self.info)
        self.webcam.on_layout(win_size)
        self.guide_video.on_layout(win_size)
        self.intro_button.on_layout(win_size)
    
    def display_video(self, position):
        self.guide_video.move_to(position)
        if self.guide_video not in self.canvas.children:
            self.canvas.add(self.guide_video)
    
    def hide_video(self):
        if self.guide_video in self.canvas.children:
            self.canvas.remove(self.guide_video)

    def set_level(self, level):
        self.level = level
        self.guide_video.load_source(self.level.vid_src)
        
        if self.level.difficulty == 0:
            self.display_video('left')
            self.webcam.move_to('right')
        else:
            self.hide_video()
            self.webcam.move_to('center')
    
    def unlock_next_levels(self):
        # Fill in the button icon to show completion
        level_button = get_button(self.level.get_id())
        level_button.background_normal = 'assets/button{}_down.png'.format(str(self.level.letter_set))

        # if not the final difficulty, unlock the next difficulty
        if self.level.difficulty != 2:
            next_id = (self.level.mode, self.level.letter_set, self.level.difficulty+1)
        # if final difficulty, unlock corresponding game level
        else:
            next_id = ('gmode', self.level.letter_set, 0)
        get_level(next_id).unlocked = True
        get_button(next_id).disabled = False


class GameScreen(Screen):
    def __init__(self, webcam, send_summary, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        # transition function for sending game summary
        self.send_summary = send_summary
        self.level = Level(mode='gmode',letter_set=0,difficulty=0)

        self.info = topleft_label(font_size=font_sz, font_name="assets/AtlantisInternational")
        self.info.text = set_idx_to_letters[self.level.letter_set] + '\n'
        self.info.text += "Spell out the following word: {}\n".format(self.level.target)
        self.info.text += "Press spacebar to skip, h to see hint\n"
        self.info.text += "Spelled so far: {}\n".format(self.level.target[:self.level._cur_letter_idx])

        self.add_widget(self.info)
        self.start_time = time.time() + 3
        self.bartimer = TimerDisplay()
        self.canvas.add(self.bartimer)
        
        self.gmode_button = ReturnToButton('Return to Game Mode')
        self.gmode_button.bind(on_release=lambda x: self.switch_to('gmode_main'))
        self.add_widget(self.gmode_button)

        w, h = Window.size
        # TODO smarter way of scaling webcam display to preserve 16:9 ratio
        self.webcam = VideoDisplay(0, 'center')
        self.canvas.add(self.webcam)
        self.guide_video = VideoDisplay(self.level.vid_src, 'left')
    
    def display_video(self, position):
        self.guide_video.move_to(position)
        if self.guide_video not in self.canvas.children:
            self.canvas.add(self.guide_video)
    
    def hide_video(self):
        if self.guide_video in self.canvas.children:
            self.canvas.remove(self.guide_video)

    def on_enter(self):
        # reset timer
        self.start_time = time.time() + 3
        duration = 30. + 15 * (self.level.difficulty)
        self.bartimer.reset(duration)
        
        self.level.reset()
        self.guide_video.load_source(self.level.vid_src)
        self.hide_video()

    def on_key_down(self, keycode, modifiers):
        if keycode[1] == 'spacebar':
            # get new target word
            new_target = self.level.set_target(self.level.get_next_target())
            if new_target == 'level complete':
                print('game ended')
                # count how many words were guessed correctly
                level_total = len(self.level.attempted)
                # TODO if hint used, score is docked
                # TODO if word skipped, score is docked
                # TODO calculate and save level score
                self.send_summary({'correct': level_total})
                if level_total > 0:
                    self.unlock_next_levels()
                self.switch_to('transition')
                return
            self.guide_video.load_source(self.level.vid_src)
        if keycode[1] == 'h':
            self.display_video('center')

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
            self.send_summary({'correct': level_total})
            if level_total > 0:
                self.unlock_next_levels()
            self.switch_to('transition')
            return
        
        # Update guide video display
        if self.guide_video in self.canvas.children:
            video_update = self.guide_video.on_update()
            if not video_update:
                self.hide_video()

        # Update webcam display
        frame_info = self.webcam.on_update()
        if frame_info:
            pred, score = frame_info
                
            # Update level
            level_update = self.level.on_update(pred, score)
            if level_update == 'level complete':
                print('game ended')
                # count how many words were guessed correctly
                level_total = len(self.level.attempted)
                # TODO if hint used, score is docked
                # TODO if word skipped, score is docked
                # TODO calculate and save level score
                self.send_summary({'correct': level_total})
                if level_total > 0:
                    self.unlock_next_levels()
                self.switch_to('transition')
                return
            if level_update:
                self.hide_video()
                self.guide_video.load_source(self.level.vid_src)
            
        
        # Update screen text
        self.info.text = set_idx_to_letters[self.level.letter_set] + '\n'
        self.info.text += "Spell out the following word: {}\n".format(self.level.target)
        self.info.text += "Press spacebar to skip, h to see hint\n"
        self.info.text += "Spelled so far: {}\n".format(self.level.target[:self.level._cur_letter_idx])
        self.info.text += self.level.feedback

    def on_layout(self, win_size):
        resize_topleft_label(self.info)
        self.gmode_button.on_layout(win_size)
        self.webcam.on_layout(win_size)
        self.guide_video.on_layout(win_size)
        self.bartimer.on_layout(win_size)

    def set_level(self, level):
        self.level = level
    
    def unlock_next_levels(self):
        # Fill in the button icon to show completion
        level_button = get_button(self.level.get_id())
        level_button.background_normal = 'assets/button{}_down.png'.format(str(self.level.letter_set))
        
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
                                font_name="assets/AtlantisInternational")
        self.canvas.add(self.title)
        self.stats = CLabelRect(cpos=(w/2, 0.6*h),
                                text="",
                                font_size=font_sz/2,
                                font_name="assets/AtlantisInternational")
        self.canvas.add(self.stats)
        
        self.game_summary = ""
        
        self.stars = [
            CRectangle(
                cpos=(0.4*w, 0.4*h),
                csize=((metrics.dp(70), metrics.dp(70))),
                source='assets/rainbow_star.png'
            ),
            CRectangle(
                cpos=(0.5*w, 0.4*h),
                csize=((metrics.dp(70), metrics.dp(70))),
                source='assets/rainbow_star.png'
            ),
            CRectangle(
                cpos=(0.6*w, 0.4*h),
                csize=((metrics.dp(70), metrics.dp(70))),
                source='assets/rainbow_star.png'
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
        self.stats.set_cpos((w/2, 0.6*h))
        for i,star in enumerate(self.stars):
            star.pos = ((0.4+0.1*i)*w, 0.4*h)
    
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

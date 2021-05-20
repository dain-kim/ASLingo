import numpy as np
import random
from game_words import GAME_WORDS
set_idx_to_letters = {0: 'ABCDEFG', 1: 'HIJKLMN', 2: 'OPQRST', 3: 'UVWXYZ'}

class Level():
    '''
    This is a functional class that serves as a dictionary for each level's information.
    '''
    def __init__(self, mode, letter_set, difficulty, unlocked=True):
        self.mode = mode
        self.letter_set = letter_set
        self.difficulty = difficulty
        self.unlocked = unlocked
        self.completed = False
        self.reset()

    def reset(self):
        self._cur_letter_idx = 0
        self.attempted = set()
        self.feedback = ""
        self._frame_counter = 0
        self._feedback_counter = 0
        
        if self.mode == 'lmode':
            if self.difficulty == 2:
                self._cur_letter_idx = np.random.choice(range(len(set_idx_to_letters[self.letter_set])))
                self.target = set_idx_to_letters[self.letter_set][self._cur_letter_idx]
            else:
                self.target = set_idx_to_letters[self.letter_set][0]
            self.vid_src = 'guide_videos/{}.mp4'.format(self.target)
            
        elif self.mode == 'gmode':
            self.target = np.random.choice(GAME_WORDS[self.letter_set][self.difficulty])
            self.vid_src = 'guide_videos/{}.mp4'.format(self.target[self._cur_letter_idx])
    
    def get_id(self):
        return (self.mode, self.letter_set, self.difficulty)
    
    def set_target(self, target):
        if target == 'level complete':
            return target
        if self.target != target:
            self.target = target
            self._frame_counter = 0
            if self.mode == 'lmode':
                self.vid_src = 'guide_videos/{}.mp4'.format(self.target)
            elif self.mode == 'gmode':
                self._cur_letter_idx = 0
                self.vid_src = 'guide_videos/{}.mp4'.format(self.target[self._cur_letter_idx])
            return self.target
    
    def get_next_target(self):
        if self.mode == 'lmode':
            if self.difficulty in [0,1]:
                letters = set_idx_to_letters[self.letter_set]
                return letters[self._cur_letter_idx%len(letters)]
            else:
                letters = list(set(set_idx_to_letters[self.letter_set]) - self.attempted)
                return np.random.choice(letters)
        elif self.mode == 'gmode':
            word_bank = GAME_WORDS[self.letter_set][self.difficulty]
            if len(self.attempted) == len(word_bank):
                return "level complete"
            # TODO know words that are already guessed
            draw_from = list(set(word_bank)-self.attempted)
            if len(draw_from) == 0:
                return "level complete"
            return np.random.choice(draw_from)
            
    
    def on_update(self, pred, score):
        # Update feedback
        if 0 < self._feedback_counter:
            self.feedback = 'Nice job!'
            self._feedback_counter += 1
        if self._feedback_counter > 10:
            self._feedback_counter = 0
            self.feedback = ""

        # Update score
        if self.mode == 'lmode':
            if pred.replace('LETTER-','') == self.target:
                self._frame_counter += 1
            if self._frame_counter > 10:
                # Passed letter
                self.attempted.add(self.target)
                self._frame_counter = 0
                self._feedback_counter = 1
                self._cur_letter_idx += 1
                if len(self.attempted) == len(set_idx_to_letters[self.letter_set]):
                    print('congrats! You learned all the letters in this set')
                    self.completed = True
                    self._cur_letter_idx = 0
                    self.target = set_idx_to_letters[self.letter_set][self._cur_letter_idx]
                    self.attempted = set()
                    return "level complete"
                return self.set_target(self.get_next_target())
        elif self.mode == 'gmode':
            if pred.replace('LETTER-','') == self.target[self._cur_letter_idx]:
                self._frame_counter += 1
            if self._frame_counter > 10:
                # Passed letter
                self._frame_counter = 0
                self._feedback_counter = 1
                self._cur_letter_idx += 1
                if len(self.target) == self._cur_letter_idx:
                    self.attempted.add(self.target)
                    print('FINISHED WORD')
                    self._cur_letter_idx = 0
                    return self.set_target(self.get_next_target())
                else:
                    self.vid_src = 'guide_videos/{}.mp4'.format(self.target[self._cur_letter_idx])
                    return self.target[self._cur_letter_idx]


import numpy as np
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
        self._cur_letter_idx = 0
        self.attempted = set()
        
        if self.mode == 'lmode':
            self.target = set_idx_to_letters[self.letter_set][0]
            if self.difficulty == 2:
                self.target = self.get_next_target()
        elif self.mode == 'gmode':
            self.target = np.random.choice(GAME_WORDS[self.letter_set][self.difficulty])
        self.feedback = ""
        self._frame_counter = 0
        self._feedback_counter = 0
        if self.mode == 'lmode':
            self.vid_src = 'guide_videos/{}.mp4'.format(self.target)
        else:
            self.vid_src = 'guide_videos/{}.mp4'.format(self.target[self._cur_letter_idx])
    
    def get_id(self):
        return (self.mode, self.letter_set, self.difficulty)
    
    def set_target(self, target):
        if self.target != target:
            self.target = target
            self._frame_counter = 0
            if self.mode == 'lmode':
                self.vid_src = 'guide_videos/{}.mp4'.format(self.target)
            elif self.mode == 'gmode':
                self._cur_letter_idx = 0
                print('updated vid src to', self.target[self._cur_letter_idx])
                self.vid_src = 'guide_videos/{}.mp4'.format(self.target[self._cur_letter_idx])
            return self.target
    
    def get_next_target(self):
        if self.mode == 'lmode':
            if self.difficulty in [0,1]:
                letters = set_idx_to_letters[self.letter_set]
                # return chr((ord(self.target)+1 - ord(letters[0])) % len(letters) + ord(letters[0]))
                return letters[self._cur_letter_idx%len(letters)]
            # TODO fix shuffle mode behavior to keep track of guessed letters
            else:
                # letters = [l for l in set_idx_to_letters[self.letter_set] if l != self.target]
                letters = [l for l in set_idx_to_letters[self.letter_set] if l not in self.attempted]
                return np.random.choice(letters)
        elif self.mode == 'gmode':
            word_bank = GAME_WORDS[self.letter_set][self.difficulty]
            # TODO know words that are already guessed
            word_bank.remove(self.target)
            return np.random.choice(word_bank)
            
    
    def on_update(self, frame_info):
        frame, pred, score = frame_info

        # Update feedback
        if 0 < self._feedback_counter:
            self.feedback = 'Nice job!'
            self._feedback_counter += 1
        if self._feedback_counter > 10:
            self._feedback_counter = 0
            self.feedback = ""

        # Update score
        # TODO: more robust way of parsing prediction
        if self.mode == 'lmode':
            if pred.replace('LETTER-','') == self.target:
                self._frame_counter += 1
            if self._frame_counter > 10:
                # Passed letter
                self.attempted.add(self.target)
                self._frame_counter = 0
                self._feedback_counter = 1
                self._cur_letter_idx += 1
                # if len(set_idx_to_letters[self.letter_set]) == self._cur_letter_idx:
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
                    print('updated vid src to', self.target[self._cur_letter_idx])
                    self.vid_src = 'guide_videos/{}.mp4'.format(self.target[self._cur_letter_idx])
                    return self.target[self._cur_letter_idx]
                # TODO game finish condition


import numpy as np
set_idx_to_letters = {0: 'ABCDEFG', 1: 'HIJKLMN', 2: 'OPQRST', 3: 'UVWXYZ'}

class Level():
    '''
    This is a functional class that serves as a dictionary for each level's information.
    '''
    def __init__(self, mode, letter_set, difficulty):
        self.mode = mode
        self.letter_set = letter_set
        self.difficulty = difficulty
        self._cur_letter_idx = 0
        
        if self.mode == 'lmode':
            self.target = set_idx_to_letters[self.letter_set][0]
            if self.difficulty == 2:
                self.target = self.get_next_target()
        elif self.mode == 'gmode':
            self.target = 'ANDY' # TODO
        self.feedback = ""
        self._score_counter = 0
        self._feedback_counter = 0
        if self.mode == 'lmode':
            self.vid_src = 'guide_videos/{}.mp4'.format(self.target)
    
    def set_target(self, target):
        if self.target != target:
            self.target = target
            self._score_counter = 0
            if self.mode == 'lmode':
                self.vid_src = 'guide_videos/{}.mp4'.format(self.target)
            if self.mode == 'gmode':
                self._cur_letter_idx = 0
            return True
        return False
    
    def get_next_target(self):
        if self.mode == 'lmode':
            if self.difficulty in [0,1]:
                letters = set_idx_to_letters[self.letter_set]
                return chr((ord(self.target)+1 - ord(letters[0])) % len(letters) + ord(letters[0]))
            # TODO fix shuffle mode behavior to keep track of guessed letters
            else:
                letters = [l for l in set_idx_to_letters[self.letter_set] if l != self.target]
                return np.random.choice(letters)
        elif self.mode == 'gmode':
            word_bank = ['ANDY','FRIEND','SUNDAY','GUAVA','BANANA','CAT','DOG','HAND']
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
                self._score_counter += 1
            if self._score_counter > 10:
                self._score_counter = 0
                self._feedback_counter = 1
                return self.set_target(self.get_next_target())
        elif self.mode == 'gmode':
            if pred.replace('LETTER-','') == self.target[self._cur_letter_idx]:
                self._score_counter += 1
            if self._score_counter > 10:
                self._score_counter = 0
                self._feedback_counter = 1
                self._cur_letter_idx += 1
                if len(self.target) == self._cur_letter_idx:
                    print('FINISHED WORD')
                    return self.set_target(self.get_next_target())


# Define levels here as a mapping from (letter_set, difficulty) --> list of words in the word bank
GAME_WORDS = {
    # A-G
    0: {
        # length 3
        0: ['ACE', 'AGE', 'BAD', 'BAG', 'BED', 'BEG', 'CAB', 'FAD'],
        # length 4
        1: ['BEAD', 'CAFE', 'CAGE', 'DEAF', 'FACE', 'FADE'],
        # length 5-6
        2: ['BADGE', 'DECAF', 'DEFACE', 'DECADE', 'FACADE']
    },
    # H-N
    1: {
        0: ['ELF', 'DIG', 'MAN', 'JAB', 'INK', 'HAM', 'CAN', 'END'],
        1: ['ACHE', 'FAKE', 'LAND', 'JAIL', 'EDGE', 'FILM'],
        2: ['AGILE', 'CABIN', 'CAMEL', 'DENIM', 'MAGIC', 'KEBAB', 'JADED', 'HEDGE', 'CHALK', 'CHILD']
    },
    # O-T
    2: {
        0: ['ANT', 'ART', 'ASK', 'DOT', 'FOG', 'OAT', 'PAN', 'QI', 'MAP'],
        1: ['KELP', 'MELT', 'JOIN', 'FORT', 'DROP', 'TRIP', 'STOP', 'SONG', 'HOME'], # Q
        2: ['BISON', 'RIGHT', 'SPACE', 'FJORD', 'TEMPO', 'MANGO', 'STORM', 'TIGER', 'STICK', 'MIDST'] # Q
    },
    # U-Z
    3: {
        0: ['AXE', 'BOX', 'JOY', 'COW', 'WHY', 'ZEN', 'DOT', 'PUG', 'FLY', 'VOW', 'SPY', 'ZIP', 'WAR', 'MUD', 'KEY'], # q
        1: ['AQUA', 'YEAR', 'SWIM', 'APEX', 'COZY', 'DUCK', 'FAUX', 'JUDO', 'MYTH', 'YAWN'],
        2: ['VINYL', 'WALTZ', 'ZEBRA', 'LAUGH', 'UNCLE', 'BROWN', 'WAVES', 'WATER', 'MIXER', 'HELIX', 'CHEWY', 'WHISK', 'BOXER']
    }
}
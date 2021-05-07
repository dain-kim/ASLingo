#####################################################################
#
# noteseq.py
#
# Copyright (c) 2017, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

from common.clock import kTicksPerQuarter, quantize_tick_up

class NoteSequencer(object):
    """
    Plays a single Sequence of notes. The sequence is a python list containing
    notes. Each note is ``(dur, pitch)``.
    """

    def __init__(self, sched, synth, channel, program, notes, loop=True):
        """
        :param sched: The Scheduler object. Should keep track of ticks and
            allow commands to be scheduled.
        :param synth: The Synthesizer object that will generate audio.
        :param channel: The channel to use for playing audio.
        :param program: A tuple (bank, preset). Allows an instrument to be specified.
        :param notes: The sequence of notes to play, a list containing ``(dur, pitch)``.
        :param loop: When True, restarts playback from the first note.
        """
        super(NoteSequencer, self).__init__()
        self.sched = sched
        self.synth = synth
        self.channel = channel
        self.program = program

        self.notes = notes
        self.loop = loop
        self.playing = False

        self.on_cmd = None
        self.off_cmd = None
        self.idx = 0

    def start(self):
        """
        Starts playback.
        """

        if self.playing:
            return

        self.playing = True
        self.synth.program(self.channel, self.program[0], self.program[1])

        # start from the beginning
        self.idx = 0

        # post the first note on the next quarter-note:
        now = self.sched.get_tick()
        next_beat = quantize_tick_up(now, kTicksPerQuarter)
        self.on_cmd = self.sched.post_at_tick(self._note_on, next_beat)

    def stop(self):
        """
        Stops playback.
        """

        if not self.playing:
            return

        self.playing = False
        if self.on_cmd:
            self.sched.cancel(self.on_cmd)
        if self.off_cmd:
            self.sched.cancel(self.off_cmd)
            self.off_cmd.execute() # cause note off to happen right now
        self.on_cmd = None
        self.off_cmd = None

    def toggle(self):
        """
        Toggles playback.
        """

        if self.playing:
            self.stop()
        else:
            self.start()

    def _note_on(self, tick):
        # if looping, go back to beginning
        if self.loop and self.idx >= len(self.notes):
            self.idx = 0

        # play new note if available
        if self.idx < len(self.notes):
            length, pitch = self.notes[self.idx]
            if pitch != 0: # pitch 0 is a rest
                # play note and post note off
                self.synth.noteon(self.channel, pitch, 60)
                off_tick = tick + length * .95 # slightly detached 
                self.off_cmd = self.sched.post_at_tick(self._note_off, off_tick, pitch) 

            # schedule the next note:
            self.idx += 1
            self.on_cmd = self.sched.post_at_tick(self._note_on, tick + length)
        else:
            self.playing = False


    def _note_off(self, tick, pitch):
        # terminate current note:
        self.synth.noteoff(self.channel, pitch)



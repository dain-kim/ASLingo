#####################################################################
#
# note.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

import numpy as np
from .audio import Audio

# Twelevth root of 2
kTRT = pow(2.0, 1.0/12.0)

def midi_to_frequency(n):
    """
    Converts MIDI pitch (parameter `n`) to frequency in Hz.
    Example: *A440* = MIDI note *69*.

    :param n: The MIDI pitch of the note.
    :returns: The frequency in Hz correspnding to the MIDI pitch.
    """

    return 440.0 * pow(kTRT, (n - 69))

class NoteGenerator(object):
    """
    Generates repeating waveforms to create constant tones/notes.
    """

    def __init__(self, pitch, gain, timbre="sine"):
        """
        :param pitch: The MIDI pitch of the note to be generated.
        :param gain: The gain/volume of the note.
        :param timbre: Specifies the geometric waveform used to generate the note,
            and allows the production of different timbres, or sound qualities.
            Can be set to one of the following: ``sine``, ``square``, ``sawtooth``, or ``triangle``.
            Defaults to ``sine``.
        """

        super(NoteGenerator, self).__init__()

        self.freq = midi_to_frequency(pitch)
        self.gain = float(gain)
        self.frame = 0
        self.playing = True

        harmonics = {
            "sine": (np.sin, (1., )),
            "square": (np.sin, (1., 0, 1/3., 0, 1/5., 0, 1/7., 0, 1/9.)),
            "sawtooth": (np.sin, (1., -1/2., 1/3., -1/4., 1/5., -1/6., 1/7., -1/8., 1/9.)),
            "triangle": (np.cos, (1., 0, 1/9., 0, 1/25., 0, 1/49.)),
        }

        self.func = harmonics[timbre][0]
        self.harmonics = harmonics[timbre][1]

    def note_off(self):
        """
        Halts tone generation.
        """

        self.playing = False

    def generate(self, num_frames, num_channels):
        """
        Should be called on every update. Generates Note output.

        :param num_frames: An integer number of frames to generate.
        :param num_channels: Number of channels. Can be 1 (mono) or 2 (stereo)

        :returns: A tuple ``(output, continue_flag)``. The output is the waveform
            that has the pitch, gain, and waveform specified during initialization.
            The continue_flag is ``True`` if the note is still playing, and ``False``
            if :meth:`note_off` has been called.
        """

        # create time series from frame range
        time = np.arange(self.frame, self.frame + num_frames) / Audio.sample_rate 

        # frequency
        omega = (2.0 * np.pi) * self.freq

        # final output, gain
        output = self.gain * self._make_waveform(omega * time)

        # advance frame counter
        self.frame += num_frames

        # convert from mono to stereo
        if num_channels == 2:
            stereo = np.empty(num_frames * 2)
            stereo[0::2] = output
            stereo[1::2] = output
            output = stereo

        return (output, self.playing)

    # Constructs waveform defined by specified timbre during initialization.
    def _make_waveform(self, time):
        # create fundamental frequency
        signal = self.harmonics[0] * self.func( time )

        # add additional harmonics
        for (h, w) in enumerate( self.harmonics[1:] ):
            if w != 0: # optimization for amplitude weight = 0
                signal += w * self.func( time * (h+2))

        return signal


class Envelope(object):
    """
    Modifies frames from another generator to fade in and out nicely.
    Total duration is *attack_time + decay_time*.
    """

    def __init__(self, generator, attack_time, n1, decay_time, n2):
        """
        :param generator: A generator object. Generator must define the method
            ``generate(num_frames, num_channels)``, which returns a tuple
            ``(signal, continue_flag)``. The signal must be a numpy array of
            length *(num_frames * num_channels)*. 

        :param attack_time: The duration of attack time, in seconds.

        :param n1: The time constant of the attack function. Values farther from 1.0 are more sharply curved.

        :param decay_time: The duration of decay time, in seconds.

        :param n2: The time constant of the decay function. Values farther from 1.0 are more sharply curved.
        """
        super(Envelope, self).__init__()

        self.generator = generator

        # attack / decay time parameters (converted from seconds to frames)
        self.attack_frames = round(attack_time * Audio.sample_rate)
        self.decay_frames =  round(decay_time * Audio.sample_rate)

        # attack / decay envelope shapes
        self.n1 = n1
        self.n2 = n2

        self.frame = 0

    def generate(self, num_frames, num_channels):
        """
        Should be called on every update. Shapes the amplitude of generated audio with
        a gain envelope.

        :param num_frames: An integer number of frames to generate.
        :param num_channels: Number of channels. Can be 1 (mono) or 2 (stereo)

        :returns: A tuple ``(output, continue_flag)``. The output is the result of combining
            the envelope and the waveform from the generator specified on initialization.
            The continue_flag is ``False`` if the envelope has ended, and ``True`` otherwise.
        """

        # get data from predecessor:
        data, continue_flag = self.generator.generate(num_frames, num_channels)

        # set up correct frame ranges:
        end_frame = self.frame + num_frames
        frames = np.arange(self.frame, end_frame)

        # boundary is the transition location between attack and decay functions
        boundary = int(np.clip(self.attack_frames - self.frame, 0, num_frames))

        # attack part:
        env1 = (frames[:boundary] / self.attack_frames) ** (1.0/self.n1)

        # decay part:
        env2 = 1.0 - ((frames[boundary:] - self.attack_frames) / self.decay_frames) ** (1.0/self.n2)

        # combine:
        env = np.append(env1, env2)

        # deal with end of envelope:
        # clamp curve to 0, so we don't get any negative values and don't continue
        if end_frame > self.attack_frames + self.decay_frames:
            env[env < 0] = 0
            continue_flag = False

        # advance frame counter
        self.frame = end_frame

        # make envelope work for stereo if needed
        if num_channels == 2:
            stereo = np.empty(num_frames * 2)
            stereo[0::2] = env
            stereo[1::2] = env
            env = stereo
            
        output = env * data
        return output, continue_flag


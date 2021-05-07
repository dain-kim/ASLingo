#####################################################################
#
# wavegen.py
#
# Copyright (c) 2018, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################


import numpy as np

# generates audio data by asking an audio-source (ie, WaveFile) for that data.
class WaveGenerator(object):
    """
    Generates audio data by asking an audio-source (eg, WaveFile) for that data.
    """
    def __init__(self, wave_source, loop=False):
        """
        :param wave_source: The source of data. Must define ``get_frames(start_frame, end_frame)``,
            which returns a numpy array.
        :param loop: When *True*, continuously restarts playback from beginning of wave source.
        """
        super(WaveGenerator, self).__init__()
        self.source = wave_source
        self.loop = loop
        self.frame = 0
        self.paused = False
        self._release = False
        self.gain = 1.0

    def reset(self):
        """
        Restarts playback from frame 0.
        """
        self.paused = True
        self.frame = 0

    def play_toggle(self):
        """
        Toggles play and pause.
        """
        self.paused = not self.paused

    def play(self):
        """
        Starts audio generation from the last frame it played.
        """
        self.paused = False

    def pause(self):
        """
        Pauses audio generation.
        """
        self.paused = True

    def release(self):
        """
        Stops any further audio generation.
        """
        self._release = True

    def set_gain(self, g):
        """
        Sets volume/gain value for audio output.

        :param g: A float specifying gain. Will be clipped between 0 and 1,
            where 1 is full volume.
        """
        self.gain = g

    def get_gain(self):
        """
        :returns: The volume/gain of the generator, a float between 0 and 1.
        """
        return self.gain

    def generate(self, num_frames, num_channels):
        """
        Generates output from the wave source. When paused, only zeros are
        generated. When looping, if the end of the buffer is reached, more
        data will be read from the beginning.

        :param num_frames: An integer number of frames to generate.
        :param num_channels: Number of channels. Can be 1 (mono) or 2 (stereo)

        :returns: A tuple ``(output, True)``. The output is the audio data from
            wave source, a numpy array of size num_frames * num_channels. 
        """
        if self.paused:
            output = np.zeros(num_frames * num_channels)
            return (output, True)

        else:
            # get data based on our position and requested # of frames
            output = self.source.get_frames(self.frame, self.frame + num_frames)
            src_channels = self.source.get_num_channels()
            if num_channels != src_channels:
                output = convert_channels(output, src_channels, num_channels)

            # check for end-of-buffer condition:
            actual_num_frames = len(output) // num_channels
            continue_flag = actual_num_frames == num_frames

            # advance current-frame
            self.frame += actual_num_frames

            # looping. If we got to the end of the buffer, don't actually end.
            # Instead, read some more from the beginning
            if self.loop and not continue_flag:
                continue_flag = True
                remainder = num_frames - actual_num_frames
                output = np.append(output, self.source.get_frames(0, remainder))
                self.frame = remainder

            if self._release:
                continue_flag = False

            # zero-pad if output is too short (may happen if not looping / end of buffer)
            shortfall = num_frames * num_channels - len(output)
            if shortfall > 0:
                output = np.append(output, np.zeros(shortfall))

            # return
            return (output * self.gain, continue_flag)


def convert_channels(data, in_channels, out_channels):
    """
    Convert an audio data buffer of a given number of channels to a different number of channels.
    Currently only handles going from mono to multi-channel, or from multi-channel to mono.
    """
    if in_channels == out_channels:
        return data

    # copy mono input into all output channels, interleaved
    if in_channels == 1:
        frames = len(data)
        output = np.empty(frames * out_channels)
        for c in range(out_channels):
            output[c::out_channels] = data
        return output

    # reduce all input interleaved input channels into one mono output, averaging data
    if out_channels == 1:
        frames = len(data) // in_channels
        in_data = np.empty((in_channels, frames))
        for c in range(in_channels):
            in_data[c] = data[c::in_channels]
        return in_data.mean(axis=0)

    else:
        assert("can't convert unless input or output is mono")


class SpeedModulator(object):
    """
    Modulates the speed of generated data from a source.
    """
    def __init__(self, generator, speed = 1.0):
        """
        :param generator: The generator object. Must define the method 
            ``generate(num_frames, num_channels)``, which returns a tuple
            ``(signal, continue_flag)``.
        """
        super(SpeedModulator, self).__init__()
        self.generator = generator
        self.speed = speed

    def set_speed(self, speed):
        """
        Sets the factor by which the speed should be modulated. For example, a speed
        of 1.0 is the original speed, 2.0 is twice as fast, 0.5 is twice as slow.

        :param speed: The desired speed, a float.
        """
        self.speed = speed

    def generate(self, num_frames, num_channels):
        """
        Generates output of modulated speed by resampling audio data according
        to the specified speed.

        :param num_frames: An integer number of frames to generate.
        :param num_channels: Number of channels. Can be 1 (mono) or 2 (stereo)

        :returns: A tuple ``(output, True)``. The output is the audio data from
            wave source, a numpy array of size num_frames * num_channels. 
        """
        # optimization if speed is 1.0
        if self.speed == 1.0:
            return self.generator.generate(num_frames, num_channels)

        # otherwise, we need to ask self.generator for a number of frames that is
        # larger or smaller than num_frames, depending on self.speed
        adj_frames = int(round(num_frames * self.speed))

        # get data from generator
        data, continue_flag = self.generator.generate(adj_frames, num_channels)

        # split into multi-channels:
        data_chans = [ data[n::num_channels] for n in range(num_channels) ]

        # stretch or squash data to fit exactly into num_frames
        from_range = np.arange(adj_frames)
        to_range = np.arange(num_frames) * (float(adj_frames) / num_frames)
        resampled = [ np.interp(to_range, from_range, data_chans[n]) for n in range(num_channels) ]

        # convert back by interleaving into a single buffer
        output = np.empty(num_channels * num_frames, dtype=float)
        for n in range(num_channels):
            output[n::num_channels] = resampled[n]

        return (output, continue_flag)

#####################################################################
#
# writer.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

import numpy as np
import os.path
import wave
from .audio import Audio

class AudioWriter(object):
    """Class for recording audio data. To use, create an AudioWriter, and pass its method
        :meth:`add_audio` into Audio's `listen_func`. See :class:`common.audio.Audio`.
    """

    def __init__(self, filebase, num_channels = 1):
        """
        :param filebase: The name of the file to output (without the extension). File extension
            is added automatically.

        :param num_channels: When writing the wave file, write with this many channels
        """
        super(AudioWriter, self).__init__()
        self.active = False
        self.buffers = []
        self.filebase = filebase
        self.num_channels = num_channels

    def add_audio(self, data, num_channels):
        """Function to add more audio into AudioWriter's internal buffer.
        
        :param data: the frames of audio data.
        :param num_channels: number of channels of interleaved audio data in `data`.
        
        """
        if self.active:
            # convert audio from num_channels to the # channels selected for writing
            data = convert_channels(data, num_channels, self.num_channels)
            self.buffers.append(data)

    def toggle(self):
        """
        Toggles between calling `start()` and `stop()`
        """

        if self.active:
            self.stop()
        else:
            self.start()

    def start(self):
        """
        Starts recording audio frames, by accepting data from :meth:`add_audio`.
        """

        if not self.active:
            print('AudioWriter: start capture')
            self.active = True
            self.buffers = []

    def stop(self):
        """
        Stops recording audio frames by ignoring any calls to :meth:`add_audio`.
        """

        if self.active:
            print('AudioWriter: stop capture')
            self.active = False

            output = combine_buffers(self.buffers)
            if len(output) == 0:
                print('AudioWriter: empty buffers. Nothing to write')
                return

            filename = self._get_filename('wav')
            print('AudioWriter: saving', len(output), 'samples in', filename)
            write_wave_file(output, self.num_channels, filename)

    # look for a filename that does not exist yet.
    def _get_filename(self, ext):
        suffix = 1
        while(True):
            filename = '%s%d.%s' % (self.filebase, suffix, ext)
            if not os.path.exists(filename):
                return filename
            else:
                suffix += 1


def write_wave_file(buf, num_channels, filename):
    """Write a Wave File

    :param buf: Buffer of audio data as an interleaved numpy float array, assuming a range of [-1, 1]

    :param num_channels: Number of channels in `buf`

    :param filename: Name of output file to write
    """
    f = wave.open(filename, 'w')
    f.setnchannels(num_channels)
    f.setsampwidth(2)
    f.setframerate(Audio.sample_rate)
    buf = buf * (2**15)
    buf = buf.astype(np.int16)
    f.writeframes(buf.tostring())


# TODO move to some common folder
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


# create single buffer from an array of buffers:
def combine_buffers(buffers):
    """Concatenates a list of numpy arrays into a single numpy array

    :param buffers: A list of numpy arrays

    :returns: A concatenated numpy float array with length being the sum of lengths of 
        arrays in input buffers.

    """
    size = 0
    for b in buffers:
        size += len(b)

    # create a single output buffer of the right size
    output = np.empty( size, dtype=float)
    f = 0
    for b in buffers:
        output[f:f+len(b)] = b
        f += len(b)
    return output

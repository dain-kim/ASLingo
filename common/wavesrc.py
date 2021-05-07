#####################################################################
#
# wavesrc.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

import numpy as np
import wave
from .audio import Audio

class WaveFile(object):
    """

    Interface for reading data from a wave file. Does not store this data locally.
    Simply call `get_frames()` to get data in format we like *(numpy array, float32)*.

    """

    def __init__(self, filepath):
        """
        :param filepath: The path to the wave file. Should be a 16 bit file with a sample rate of 44100Hz.
        """
        super(WaveFile, self).__init__()

        self.wave = wave.open(filepath)
        self.num_channels, self.sampwidth, self.sr, self.end, \
           comptype, compname = self.wave.getparams()

        # for now, we will only accept 16 bit files and the sample rate must match
        assert(self.sampwidth == 2)
        assert(self.sr == Audio.sample_rate)

    # read an arbitrary chunk of data from the file
    def get_frames(self, start_frame, end_frame):
        """
        Gets a range of frames of audio data from the provided wavefile.

        :param start_frame: The frame of the wave file to start on.
        :param end_frame: The frame of the wave file to end on.

        :returns: A numpy array of audio data from *start_frame* to *end_frame* of the wave file.
            If more frames are asked for than are available, then returns what it can.
        """

        # get the raw data from wave file as a byte string. If asking for more than is available, it just
        # returns what it can
        self.wave.setpos(start_frame)
        raw_bytes = self.wave.readframes(end_frame - start_frame)

        # convert raw data to numpy array, assuming int16 arrangement
        samples = np.fromstring(raw_bytes, dtype = np.int16)

        # convert from integer type to floating point, and scale to [-1, 1]
        samples = samples.astype(float)
        samples *= (1 / 32768.0)

        return samples

    def get_num_channels(self):
        """
        :returns: The number of channels of the loaded wave file.
        """

        return self.num_channels

# We can generalize the thing that WaveFile does - it provides arbitrary wave
# data. We can define a "wave data providing interface" (called WaveSource)
# if it can support the function:
#
# get_frames(self, start_frame, end_frame)
#
# Now create WaveBuffer. Same WaveSource interface, but can take a subset of
# audio data from a wave file and holds all that data in memory.
class WaveBuffer(object):
    """
    Reads certain data from a wave file and stores it in memory.

    This is a WaveSource -- a wave data providing interface. Call :meth:`get_frames()`
    to get audio data in the format we like *(numpy array, float32)*.
    """
    def __init__(self, filepath, start_frame, num_frames):
        """
        :param filepath: The path to the wave file. Should be a 16 bit file with a sample rate of 44100Hz.
        :param start_frame: The frame of the wave file that this buffer should start on.
        :param end_frame: The frame of the wave file that this buffer should end on.
        """
        super(WaveBuffer, self).__init__()

        # get a local copy of the audio data from WaveFile
        wr = WaveFile(filepath)
        self.data = wr.get_frames(start_frame, start_frame + num_frames)
        self.num_channels = wr.get_num_channels()

    # start and end args are in units of frames,
    # so take into account num_channels when accessing sample data
    def get_frames(self, start_frame, end_frame):
        """
        Gets a range of frames of audio data from the wave buffer.

        :param start_frame: The frame of the wave buffer to start on.
        :param end_frame: The frame of the wave buffer to end on.

        :returns: A numpy array of audio data from *start_frame* to *end_frame* of the wave buffer.
            If more frames are asked for than are available, then returns what it can.
        """
        start_sample = start_frame * self.num_channels
        end_sample = end_frame * self.num_channels
        return self.data[start_sample : end_sample]

    def get_num_channels(self):
        """
        :returns: The number of channels of the loaded wave file.
        """
        return self.num_channels



# simple class to hold a region: name, start frame, length (in frames)
from collections import namedtuple
AudioRegion = namedtuple('AudioRegion', ['name', 'start', 'len'])

# a collection of regions read from a file
class SongRegions(object):
    def __init__(self, filepath):
        super(SongRegions, self).__init__()

        self.regions = []
        self._read_regions(filepath)

    def __repr__(self):
        out = ''
        for r in self.regions:
            out = out + str(r) + '\n'
        return out

    def _read_regions(self, filepath):
        lines = open(filepath).readlines()

        for line in lines:
            # each region is: start_time val len name, separated by tabs.
            # we don't care about val
            # time values are in seconds
            (start_sec, x, len_sec, name) = line.strip().split('\t')

            # convert time (in seconds) to frames. Assumes Audio.sample_rate
            start_f = int( float(start_sec) * Audio.sample_rate )
            len_f = int( float(len_sec) * Audio.sample_rate )

            self.regions.append(AudioRegion(name, start_f, len_f))

# Reads from a regions file and a wave file to create a bunch of WaveBuffers,
# one per region.
def make_wave_buffers(wave_path, regions_path):
    """
    Reads from a regions file and a wave file to create one WaveBuffer per region.

    :param wave_path: The path to the wave file.
    :param regions_path: The path to the text file containing one region per line.
        Each line should contain the following, separated by tabs:
        start time (in seconds), index, length (in seconds), region name.
    
    :returns: A dictionary of WaveBuffers, keyed by region name.
    """
    sr = SongRegions(regions_path)
    buffers = {}
    for r in sr.regions:
        buffers[r.name] = WaveBuffer(wave_path, r.start, r.len)
    return buffers

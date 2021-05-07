#####################################################################
#
# mixer.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

import numpy as np


class Mixer(object):
    """
    Merges audio frames from multiple sources.
    """

    def __init__(self):
        super(Mixer, self).__init__()
        self.generators = []
        self.gain = 0.25

    def add(self, gen):
        """
        Adds a generator to Mixer. Generator must define the method 
        ``generate(num_frames, num_channels)``, which returns a tuple
        ``(signal, continue_flag)``. The signal must be a numpy array of 
        length *(num_frames * num_channels)*. The continue_flag should
        be a boolean indicating whether the generator has more audio to generate.

        :param gen: The generator object.
        """

        if gen not in self.generators:
            self.generators.append(gen)

    def remove(self, gen):
        """
        Removes generator from Mixer.

        :param gen: The generator object to remove.
        """

        self.generators.remove(gen)

    def set_gain(self, gain):
        """
        Sets volume/gain value for Mixer output.

        :param gain: A float specifying gain. Will be clipped between 0 and 1,
            where 1 is full volume.
        """

        self.gain = np.clip(gain, 0, 1)

    def get_gain(self):
        """
        :returns: The volume/gain of the Mixer, a float betwen 0 and 1.
        """

        return self.gain

    def get_num_generators(self):
        """
        :returns: The number of generators that have been added to the Mixer.
        """

        return len(self.generators)

    def generate(self, num_frames, num_channels):
        """
        Generates Mixer output by summing frames from all added generators.

        :param num_frames: An integer number of frames to generate.
        :param num_channels: Number of channels. Can be 1 (mono) or 2 (stereo)

        :returns: A tuple ``(output, True)``. The output is the sum of the outputs of
            all added generators.
        """

        output = np.zeros(num_frames * num_channels)

        # this calls generate() for each generator. generator must return:
        # (signal, keep_going). If keep_going is True, it means the generator
        # has more to generate. False means generator is done and will be
        # removed from the list. signal must be a numpay array of length
        # num_frames * num_channels
        kill_list = []
        for g in self.generators:
            (signal, keep_going) = g.generate(num_frames, num_channels)
            output += signal
            if not keep_going:
                kill_list.append(g)

        # remove generators that are done
        for g in kill_list:
            self.generators.remove(g)

        output *= self.gain
        return (output, True)

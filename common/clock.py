#####################################################################
#
# clock.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

import time
import numpy as np
from .audio import Audio


# Simple time keeper object. It starts at 0 and knows how to pause
class Clock(object):
    """
    Time keeper object. Time starts at 0.
    """
    def __init__(self):
        super(Clock, self).__init__()
        self.paused = True
        self.offset = 0
        self.start()

    def is_paused(self):
        """
        :returns: True if paused, else False
        """
        return self.paused

    def get_time(self):
        """
        :returns: The current time, a float.
        """
        if self.paused:
            return self.offset
        else:
            return self.offset + time.time()

    def set_time(self, t):
        """
        Sets the clock to a specific time.

        :param t: The time to which the clock should be set, a float.
        """
        if self.paused:
            self.offset = t
        else:
            self.offset = t - time.time()

    def start(self):
        """
        Resumes advancing time from the point when it was paused.
        """
        if self.paused:
            self.paused = False
            self.offset -= time.time()

    def stop(self):
        """
        Pauses the clock.
        """
        if not self.paused:
            self.paused = True
            self.offset += time.time()

    def toggle(self):
        """
        Toggles between paused and unpaused.
        """
        if self.paused:
            self.start()
        else:
            self.stop()


# For tempo maps - converting bpm to ticks
kTicksPerQuarter = 480

class SimpleTempoMap(object):
    """
    A simple tempo map to keep track of the relationship between time, ticks, and bpm.
    """

    def __init__(self, bpm = 120):
        """
        :param bpm: The desired tempo, as beats per minute, of the tempo map.
        """
        super(SimpleTempoMap, self).__init__()
        self.bpm = bpm
        self.tick_offset = 0

    def time_to_tick(self, time):
        """
        Converts time into tick number.

        :param time: The time elapsed, in seconds.
        :returns: The integer number of ticks corresponding to the given amount of time.
        """
        slope = (kTicksPerQuarter * self.bpm) / 60.
        tick = slope * time + self.tick_offset
        return int(tick)

    def tick_to_time(self, tick):
        """
        Converts tick number into time.

        :param tick: The number of ticks.
        :returns: The time in seconds corresponding to the given number of ticks.
        """
        slope = (kTicksPerQuarter * self.bpm) / 60.
        time = (tick - self.tick_offset) / slope
        return time

    def set_tempo(self, bpm, cur_time):
        """
        Sets the tempo to a new bpm.

        :param bpm: The new desired tempo, as beats per minute.
        :param cur_time: The current time, in seconds.
        """
        cur_tick = self.time_to_tick(cur_time)
        self.bpm = bpm
        slope = (kTicksPerQuarter * self.bpm) / 60.
        self.tick_offset = cur_tick - cur_time * slope

    def get_tempo(self):
        """
        :returns: The current bpm.
        """
        return self.bpm

# prints the tick and beat (assuming kTicksPerQuarter is ticks per beat)
def tick_str(tick):
    """
    Prints the tick and the beat.
    :param tick: The tick number, an integer.
    """
    beat = float(tick) / kTicksPerQuarter
    return "tick:{}\nbeat:{:.2f}".format(tick, beat)


# data passed into tempo map is a list of points
# where each point is (time, tick)
# optionally pass in filepath instead which will
# read the file to create the list of (time, tick) points
# TempoMap will linearly interpolate this graph
class TempoMap(object):
    """
    A tempo map that reads points of timestamped ticks and linearly
    interpolates between points to determine tempo.
    """
    def __init__(self, data = None, filepath = None):
        """
        :param data: A list of points, where each point is (time, tick).
        :param filepath: The path to a file containing a list of markers, each 
            on a separate line. A marker is a tab-delimited pair of values: ``time`` and ``delta_beats``.
            ``delta_beats`` is the number of elapsed beats (quarter notes) since the last marker
            Will read from file only if ``data`` is not provided.
        """
        super(TempoMap, self).__init__()

        if data == None:
            data = self._read_tempo_data(filepath)

        assert(data[0] == (0,0))
        assert(len(data) > 1)

        self.times, self.ticks = list(zip(*data))

    def time_to_tick(self, time):
        """
        Converts time into tick number.

        :param time: The time elapsed, in seconds.
        :returns: The number of ticks corresponding to the given amount of time,
            linearly interpolated from the given data.
        """
        tick = np.interp(time, self.times, self.ticks)
        return tick

    def tick_to_time(self, tick):
        """
        Converts tick number into time.

        :param tick: The number of ticks.
        :returns: The time in seconds corresponding to the given number of ticks, ,
            linearly interpolated from the given data.
        """
        time = np.interp(tick, self.ticks, self.times)
        return time

    def _read_tempo_data(self, filepath):
        data = [(0,0)]

        for line in open(filepath).readlines():
            (time, beats) = line.strip().split('\t')
            time = float(time)

            delta_tick = float(beats) * kTicksPerQuarter
            last_tick = data[-1][1]
            data.append( (time, last_tick + delta_tick))

        return data


class Scheduler(object):
    """
    Allows commands to be posted and executed at certain tick values.
    """
    def __init__(self, clock, tempo_map):
        """
        :param clock: The Clock object that keeps time.
        :param tempo_map: The TempoMap object that keeps track of tempo.
        """
        super(Scheduler, self).__init__()
        self.clock = clock
        self.tempo_map = tempo_map
        self.commands = []

    def get_time(self):
        """
        :returns: The time elapsed in seconds.
        """
        return self.clock.get_time()

    def get_tick(self):
        """
        :returns: The tick corresponding to the current time.
        """
        sec = self.get_time()
        return self.tempo_map.time_to_tick(sec)

    # add a record for the function to call at the particular tick
    # keep the list of commands sorted from lowest to hightest tick
    # make sure tick is the first argument so sorting will work out
    # properly
    def post_at_tick(self, func, tick, arg = None):
        """
        Adds a record for the function to execute at the specified tick value.

        :param func: The function to call.
        :param tick: The tick at which ``func`` should be called.
        :param arg: An additional argument to pass into ``func`` when it is called.

        :returns: The command object created by this record.
        """
        now_tick = self.get_tick()

        cmd = Command(tick, func, arg)
        self.commands.append(cmd)
        self.commands.sort(key = lambda x: x.tick)
        return cmd

    # attempt a removal. Does nothing if cmd is not found
    def cancel(self, cmd):
        """
        Attempts to remove the command object from the list of commands to be
        executed. Does nothing if ``cmd`` is not found.

        :param cmd: The command object to remove.
        """
        if cmd in self.commands:
            idx = self.commands.index(cmd)
            del self.commands[idx]

    # on_update should be called as often as possible.
    # the only trick here is to make sure we remove the command BEFORE
    # calling the command's function so we handle re-entry properly.
    def on_update(self):
        """
        Executes commands at the correct tick. Should be called as often as possible.
        """
        now_tick = self.get_tick()
        while self.commands:
            if self.commands[0].tick <= now_tick:
                command = self.commands.pop(0)
                command.execute()
            else:
                break

    def now_str(self):
        """
        :returns: A string containing newline-separated indicators for time, tick,
            and beat at the current time.
        """
        time = self.get_time()
        tick = self.get_tick()
        beat = float(tick) / kTicksPerQuarter
        txt = "time:%.2f\ntick:%d\nbeat:%.2f" % (time, tick, beat)
        return txt


# AudioScheduler is a Scheduler and Clock built into one class.
# It is ALSO a Generator. For it to work, it must be inserted into
# and Audio generator chain.
class AudioScheduler(object):
    """
    Generates scheduled audio with a built-in Clock and Scheduler. As a generator,
    for it to work, it must be inserted into an Audio generator chain.
    """
    def __init__(self, tempo_map):
        """
        :param tempo_map: The TempoMap object that keeps track of tempo.
        """
        super(AudioScheduler, self).__init__()
        self.tempo_map = tempo_map
        self.commands = []

        self.generator = None
        self.cur_frame = 0

    def set_generator(self, gen):
        """
        Sets a Generator object that supplies audio data. Generator must define the 
        method ``generate(num_frames, num_channels)``, which returns a numpy array of 
        length **(num_frames * num_channels)**.

        :param gen: The generator object.
        """
        self.generator = gen

    def generate(self, num_frames, num_channels):
        """
        Executes audio-generating commands at the correct tick.

        :param num_frames: An integer number of frames to generate.
        :param num_channels: Number of channels. Can be 1 (mono) or 2 (stereo)

        :returns: A tuple ``(output, True)``. The output is a numpy array of length
            **(num_frames * num_channels)**
        """
        output = np.empty(num_channels * num_frames, dtype = float)
        o_idx = 0

        # the current period of time goes from self.cur_frame to end_frame
        end_frame = self.cur_frame + num_frames

        # advance time and fire off commands for this time frame
        while self.commands:
            # find the exact frame at which the next command should happen
            cmd_tick = self.commands[0].tick
            cmd_time = self.tempo_map.tick_to_time(cmd_tick)
            cmd_frame = int(cmd_time * Audio.sample_rate)

            if cmd_frame < end_frame:
                o_idx = self._generate_until(cmd_frame, num_channels, output, o_idx)
                command = self.commands.pop(0)
                command.execute()
            else:
                break

        self._generate_until(end_frame, num_channels, output, o_idx)

        return output, True

    # generate audio from self.cur_frame to to_frame
    def _generate_until(self, to_frame, num_channels, output, o_idx):
        num_frames = to_frame - self.cur_frame
        if num_frames > 0:
            if self.generator:
                data, cont = self.generator.generate(num_frames, num_channels)
            else:
                data = np.zeros(num_channels * num_frames, dtype=float)

            next_o_idx = o_idx+(num_channels * num_frames)
            output[o_idx : next_o_idx] = data
            self.cur_frame += num_frames
            return next_o_idx
        else:
            return o_idx


    def get_time(self):
        """
        :returns: The time elapsed in seconds.
        """
        return self.cur_frame / float(Audio.sample_rate)

    def get_tick(self):
        """
        :returns: The tick corresponding to the current time.
        """
        return self.tempo_map.time_to_tick(self.get_time())

    # add a record for the function to call at the particular tick
    def post_at_tick(self, func, tick, arg = None):
        """
        Adds a record for the function to execute at the specified tick value.

        :param func: The function to call.
        :param tick: The tick at which ``func`` should be called.
        :param arg: An additional argument to pass into ``func`` it is called.

        :returns: The command object created by this record.
        """
        now_time  = self.get_time()
        post_time = self.tempo_map.tick_to_time(tick)

        # create a command to hold the function/arg and sort by tick
        cmd = Command(tick, func, arg)
        self.commands.append(cmd)
        self.commands.sort(key = lambda x: x.tick)
        return cmd

    # attempt a removal. Does nothing if cmd is not found
    def cancel(self, cmd):
        """
        Attempts to remove the command object from the list of commands to be
        executed. Does nothing if ``cmd`` is not found.

        :param cmd: The command object to remove.
        """
        if cmd in self.commands:
            idx = self.commands.index(cmd)
            del self.commands[idx]

    def now_str(self):
        """
        :returns: A string containing newline-separated indicators for time, tick,
            and beat at the current time.
        """
        time = self.get_time()
        tick = self.tempo_map.time_to_tick(time)
        beat = float(tick) / kTicksPerQuarter
        txt = "time:%.2f\ntick:%d\nbeat:%.2f" % (time, tick, beat)
        return txt


class Command(object):
    """
    An object that will execute a function exactly once with the given arguments.
    """
    def __init__(self, tick, func, arg):
        """
        :param tick: The tick value at which this command will be executed.
        :param func: The function that should be called.
        :param arg: An additional argument to pass into ``func``.
        """
        super(Command, self).__init__()
        self.tick = int(tick)
        self.func = func
        self.arg = arg
        self.did_it = False

    def execute(self):
        """
        Calls the given function with the arguments (tick, arg).
        """
        # ensure that execute only gets called once.
        if not self.did_it:
            self.did_it = True
            if self.arg == None:
                self.func( self.tick )
            else:
                self.func( self.tick, self.arg )


    def __repr__(self):
        return 'cmd:%d' % self.tick

# helper function for quantization:
def quantize_tick_up(tick, grid):
    """
    Quantizes a given tick number to the closest higher tick on the grid.
    For example, for ``tick=900`` and ``grid=480``, this returns ``960``.

    :param tick: The tick number.
    :param grid: The grid to be quanitzed to.

    :returns: The closest higher tick on the grid.
    """
    return tick - (tick % grid) + grid


#####################################################################
#
# audio.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

import sys

try:
    from common.core import register_terminate_func
except:
    # if import failed, we are most likely running from command line (python audio.py)
    # to print out audio devices. In that case, we don't need anything from common.core anyway
    pass

import pyaudio
import numpy as np
import time

class Audio(object):
    """
    Audio input and output stream manager. Only one `Audio` object should be created. Audio output
    (sent to speakers) is supplied by setting an audio Generator class. Audio input (from microphone) is 
    provided via a callback function. You can also "tap into" the output audio using a callback.

    :param num_channels: Number of output channels. Can be 1 (mono) or 2 (stereo)

    :param listen_func: if provided, call with audio buffer about to be sent out to speaker with
        parameters ``(audio, num_channels)``

    :param input_func: if provided, input streaming is enabled, and function will be called when 
        input data is available with parameters ``(audio, num_channels)``

    :param num_input_channels: stream 1 (mono) or 2 (stereo) input channels. Note that some devices
        may not support stereo input.

    The following parameters are class-parameters and can be set before creating the Audio class:

    :param Audio.sample_rate: Audio sample rate to use. Defaults to 44100.

    :param Audio.buffer_size: Internal buffer size. A smaller buffer will lower latency, at the risk of buffer underrun.
        Default is 512.

    :param Audio.out_dev: Can specify a non-default audio output device (via integer index). 
        See :meth:`print_audio_devices`. Default is None, which chooses the default output device.

    :param Audio.in_dev: Can specify a non-default audio input device (via integer index). 
        See :meth:`print_audio_devices`. Default is None, which chooses the default input device.



    .. note::
        On Windows, if ASIO drivers are installed, you can run the whole python app with
        command-line-args `-asio`. That will cause ASIO drivers to be used instead of the default in/out
        devices. ASIO typically has much lower latency than the built-in Windows drivers.

        Example: ``python myapp.py -asio``

    """

    # audio configuration parameters:
    sample_rate = 44100
    buffer_size = 512
    out_dev = None
    in_dev = None

    def __init__(self, num_channels, listen_func = None, input_func = None, num_input_channels = 1):
        super(Audio, self).__init__()

        assert(num_channels == 1 or num_channels == 2)
        self.num_channels = num_channels
        self.listen_func = listen_func
        self.input_func = input_func
        self.audio = pyaudio.PyAudio()

        self.num_input_channels = num_input_channels

        # on windows, if '-asio' found in command-line-args, use ASIO drivers
        if '-asio' in sys.argv:
            Audio.out_dev, Audio.in_dev = self._find_asio_devices()

        print('using audio params:')
        print('  samplerate: {}\n  buffersize: {}\n  outputdevice: {}\n  inputdevice: {}'.format(
            Audio.sample_rate, Audio.buffer_size, Audio.out_dev, Audio.in_dev))

        # create output stream
        self.stream = self.audio.open(format = pyaudio.paFloat32,
                                      channels = num_channels,
                                      frames_per_buffer = Audio.buffer_size,
                                      rate = Audio.sample_rate,
                                      output = True,
                                      input = False,
                                      output_device_index = Audio.out_dev)

        # create input stream
        self.input_stream = None
        if input_func:
            self.input_stream = self.audio.open(format = pyaudio.paFloat32,
                                                channels = self.num_input_channels,
                                                frames_per_buffer = Audio.buffer_size,
                                                rate = Audio.sample_rate,
                                                output = False,
                                                input = True,
                                                input_device_index = Audio.in_dev)

        self.generator = None
        self.cpu_time = 0
        register_terminate_func(self._close)

    def set_generator(self, gen):
        """
        Sets a Generator object that must supply audio data to Audio. Generator must define the 
        method ``generate(num_frames, num_channels)``, which returns a numpy array of 
        length *(num_frames * num_channels)*.

        :param gen: The generator object. May be `None`.

        """
        self.generator = gen

    def get_cpu_load(self):
        """
        :returns: Time spent (in milliseconds) processing audio input and output.
            Returned value is smoothed out somewhat. If value is too high (above 16ms), then too much time
            is being spent calculating audio.
        """
        return 1000 * self.cpu_time

    def on_update(self):
        """
        Must be called by the app (`MainWidget`) very often - usually 60 times per second. Typically,
        Audio.on_update() should be called from MainWidget.on_update().
        """

        t_start = time.time()

        # get input audio if desired
        if self.input_stream:
            try:
                num_frames = self.input_stream.get_read_available() # number of frames to ask for
                if num_frames:
                    data_str = self.input_stream.read(num_frames, False)
                    data_np = np.fromstring(data_str, dtype=np.float32)
                    self.input_func(data_np, self.num_input_channels)
            except IOError as e:
                print('got error', e)

        # Ask the generator to generate some audio samples.
        num_frames = self.stream.get_write_available() # number of frames to supply
        if self.generator and num_frames != 0:
            (data, continue_flag) = self.generator.generate(num_frames, self.num_channels)

            # make sure we got the correct number of frames that we requested
            assert len(data) == num_frames * self.num_channels, \
                "asked for (%d * %d) frames but got %d" % (num_frames, self.num_channels, len(data))

            # convert type if needed and write to stream
            if data.dtype != np.float32:
                data = data.astype(np.float32)
            self.stream.write(data.tostring())

            # send data to listener as well
            if self.listen_func:
                self.listen_func(data, self.num_channels)

            # continue flag
            if not continue_flag:
                self.generator = None

        # how long this all took
        dt = time.time() - t_start
        a = 0.9
        self.cpu_time = a * self.cpu_time + (1-a) * dt

    def _close(self):
        self.stream.stop_stream()
        self.stream.close()
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()

        self.audio.terminate()

    # look for the ASIO devices and return them (output, input)
    def _find_asio_devices(self):
        out_dev = in_dev = None

        cnt = self.audio.get_host_api_count()
        for i in range(cnt):
            api = self.audio.get_host_api_info_by_index(i)
            if api['type'] == pyaudio.paASIO:
                out_dev = api['defaultOutputDevice']
                in_dev = api['defaultInputDevice']
                print('Found ASIO device at index', i)

        return out_dev, in_dev



def get_audio_devices():
    """
    :returns: Available input and output devices as `{ 'input': <list>, 'output': <list> }`.
        `<list>` is a list of device descriptors, each being a dictionary:
        `{'index': <integer>, 'name': <string>, 'latency': (low, high), 'channels': <max # of channels>`.
    """

    def add_device(arr, io_type, dev):
        info = {}
        info['index'] = dev['index']
        info['name'] = dev['name']
        info['latency'] = (dev['defaultLow' + io_type + 'Latency'], 
                           dev['defaultHigh' + io_type + 'Latency'])
        info['channels'] = dev['max' + io_type + 'Channels']
        arr.append(info)

    audio = pyaudio.PyAudio()

    out_devs = [{'index':'None', 'name':'Default', 'channels':0, 'latency':(0,0)}]
    in_devs  = [{'index':'None', 'name':'Default', 'channels':0, 'latency':(0,0)}]

    cnt = audio.get_device_count()
    for i in range(cnt):
        dev = audio.get_device_info_by_index(i)

        if dev['maxOutputChannels'] > 0:
            add_device(out_devs, 'Output', dev)

        if dev['maxInputChannels'] > 0:
            add_device(in_devs, 'Input', dev)

    audio.terminate()
    return {'output': out_devs, 'input': in_devs}


def print_audio_devices():
    """
    Prints the list of accessible input and output audio devices. This easiest way to see
    these results is to run ``python audio.py``, which just calls this function.
    """

    devs = get_audio_devices()

    print("\nOutput Devices")
    print('{:>5}: {:<40} {:<6} {}'.format('idx', 'name', 'chans', 'latency'))
    for d in devs['output']:
        print('{index:>5}: {name:<40} {channels:<6} {latency[0]:.3f} - {latency[1]:.3f}'.format(**d))

    print("\nInput Devices")
    print('{:>5}: {:<40} {:<6} {}'.format('idx', 'name', 'chans', 'latency'))
    for d in devs['input']:
        print('{index:>5}: {name:<40} {channels:<6} {latency[0]:.3f} - {latency[1]:.3f}'.format(**d))


if __name__ == "__main__":
    print_audio_devices()

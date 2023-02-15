import os
MODULE_PATH = os.path.dirname(__file__)

try:
    import simpleaudio
    bell = simpleaudio.WaveObject.from_wave_file(MODULE_PATH+"/bell.wav")

    def play_bell():
        bell.play()

    running = simpleaudio.WaveObject.from_wave_file(MODULE_PATH+"/running.wav")
    running.audio_data *= 200 # repeat sample

    playing = None
    
    def play_running():
        global playing
        if playing is None:
            # playing = running.play()
            pass

    def stop_running():
        global playing
        if playing is not None:
            # playing.stop()
            pass
            playing = None

except ImportError:
    print("Audio disabled. Install python package 'simpleaudio' for a fully immersive experience :)")

    def play_bell():
        pass
    def play_running():
        pass
    def stop_running():
        pass

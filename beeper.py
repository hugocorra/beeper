import argparse
import time
from playsound import playsound

default_sound = 'Airplane-ding-sound.mp3'

def play_default():
    playsound(default_sound)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Beep each N seconds.')
    parser.add_argument('seconds', metavar='N', type=int, nargs='?', default=15,
                       help='interval (in seconds) between each beep')

    args = parser.parse_args()
    seconds = args.seconds

    play_default()
    while (True):
        time.sleep(seconds)
        play_default()

import os
import signal
import sys

import yaml

from robot import ASR, TTS, Player, config, constants, logging, statistic
from robot.Conversation import Conversation
from server import server
from snowboy import snowboydecoder
logger = logging.getLogger(__name__)

interrupted = False
conversation = None


def audioRecorderCallback(fname):

    conversation.converse(fname)


def detectedCallback():
    if conversation:
        conversation.stop()
    Player.play('static/beep_hi.wav', wait=False)
    statistic.set(0)


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted


conversation = Conversation()
server.run(conversation)
model = config.get('/snowboy/hotwork', 'snowboy/resources/snowboy.umdl')

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(
    model, sensitivity=config.get('/snowboy/sensitivity', 0.38))
logger.info('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=detectedCallback,
               audio_recorder_callback=audioRecorderCallback,
               interrupt_check=interrupt_callback,
               silent_count_threshold=15,
               sleep_time=0.01)

detector.terminate()

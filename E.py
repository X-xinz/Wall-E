import os
import signal
import sys
import yaml
from robot import Player, config, constants, logging, statistic
from robot.Conversation import Conversation
from server import server
from snowboy import snowboydecoder

logger = logging.getLogger(__name__)


class wall_e(object):
    def _detectedCallback(self):
        if self.conversation:
            self.conversation.stop()
        Player.play('static/beep_hi.wav', wait=False)
        statistic.set(0)

    def init(self):
        global conversation
        self.conversation = Conversation()
        self._interrupted = False

    def _signal_handler(self,signal, frame):    
        self._interrupted = True

    def _interrupt_callback(self):
        return self._interrupted

    def run(self):
        self.init()

        # capture SIGINT signal, e.g., Ctrl+C
        signal.signal(signal.SIGINT, self._signal_handler)

        server.run(self.conversation)

        try:
            self.initDetector()
        except AttributeError:
            logger.error('初始化离线唤醒失败')
            pass

    def initDetector(self):
        model = config.get('/snowboy/hotwork', 'snowboy/resources/snowboy.umdl')
        self.detector = snowboydecoder.HotwordDetector(model, sensitivity=config.get('/snowboy/sensitivity', 0.38))
        logger.info('Listening... Press Ctrl+C to exit')
        # main loop
        try:
            self.detector.start(detected_callback=self._detectedCallback,
                        audio_recorder_callback=self.conversation.converse,
                        interrupt_check=self._interrupt_callback,
                        silent_count_threshold=config.get('/silent_threshold', 15),
                        recording_timeout=config.get('/recording_timeout', 5) * 4,
                        sleep_time=0.01)

            self.detector.terminate()
        except Exception as e:
            logger.critical('离线唤醒机制初始化失败：{}'.format(e))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        wall_e = wall_e()
        wall_e.run()
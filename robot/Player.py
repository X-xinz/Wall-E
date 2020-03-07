import os
import subprocess
import threading

from robot import utils
from robot import logging

logger = logging.getLogger(__name__)


def play(src, delete):
    foo, ext = os.path.splitext(src)    #分离文件路径(foo)及后缀(ext)
    if ext in ('.wav', '.mp3'):    
        play = SoxPlayer()
        play.play(src, delete)

class AbstractPlayer(threading.Thread):

    def play(self, src):       #src:bo fang wenjian de lujing
        pass


class SoxPlayer(AbstractPlayer):


    def __init__(self):
        super(SoxPlayer,self).__init__()
        self.playing = False


    def run(self):
        cmd=['play',self.src]
        self.proc = subprocess.Popen(cmd,stderr = subprocess.DEVNULL)
        self.playing = True 
        self.proc.wait()
        self.playing = False
        if self.delete:  
            utils.check_and_delete(self.src)    
      
    def play(self, src, delete=False):
        self.src = src
        self.delete = delete
        self.start()
        

    def stop(self):
        if self.proc and self.playing:
            self.proc.terminate()
            if self.delete:  
                utils.check_and_delete(self.src)

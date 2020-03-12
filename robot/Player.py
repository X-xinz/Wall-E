import os
import subprocess
import threading

from robot import utils
from robot import logging

logger = logging.getLogger(__name__)


def play(src, delete):
    _foo, ext = os.path.splitext(src)    #fen li wen jian lujin(foo) ji houzhui(ext)
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
        print('s src is {}'.format(src))
        self.delete = delete
        self.start()
        

    def stop(self):
        if self.proc and self.playing:
            self.proc.pid
            self.proc.terminate()
            print(self.proc.returncode)
            if self.delete:
                utils.check_and_delete(self.src)

class MusicPlayer(SoxPlayer):
     
    def __init__(self):
        pass

    def play(self,path):
        pass



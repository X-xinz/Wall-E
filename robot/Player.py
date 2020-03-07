import os
import subprocess
import threading
import _thread as thread
from robot import logging,utils

logger = logging.getLogger(__name__)


def play(src, delete):
    _foo, ext = os.path.splitext(src)    #分离文件路径(foo)及后缀(ext)
    if ext in ('.wav', '.mp3'):    
        play = SoxPlayer()
        play.play(src, delete)

class AbstractPlayer(object):

    def __init__(self, **kwargs):
        super(AbstractPlayer, self).__init__()

    def play(self):
        pass

    def play_block(self):
        pass

    def stop(self):
        pass

    def is_playing(self):
        return False


class SoxPlayer(AbstractPlayer):


    def __init__(self):
        super(SoxPlayer,self).__init__()
        self.playing = False
        self.onCompleteds=[]

    def run(self):
        cmd=['play',self.src]
        self.proc = subprocess.Popen(cmd,stderr = subprocess.DEVNULL)
        self.playing = True 
        self.proc.wait()
        self.playing = False
        if self.delete:  
            utils.check_and_delete(self.src)    

    def doPlay(self):
        cmd = ['play', str(self.src)]
        logger.debug('Executing %s', ' '.join(cmd))
        self.proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.playing = True
        self.proc.wait()
        self.playing = False
        if self.delete:
            utils.check_and_delete(self.src)
        logger.debug('play completed')
        if self.proc.returncode == 0:
            for onCompleted in self.onCompleteds:
                if onCompleted is not None:
                    onCompleted()
    
    def play(self, src, delete=False, onCompleted=None, wait=False):
        if os.path.exists(src) or src.startswith('http'):
            self.src = src
            self.delete = delete
            if onCompleted is not None:
                self.onCompleteds.append(onCompleted)
            if not wait:
                thread.start_new_thread(self.doPlay, ())
            else:
                self.doPlay()
        else:
            logger.critical('path not exists: {}'.format(src))
        

    def stop(self):
        if self.proc and self.playing:
            self.proc.terminate()
            if self.delete:  
                utils.check_and_delete(self.src)

    def is_playing(self):
        return self.is_playing


class MusicPlayer(SoxPlayer):

    def __init__(self, playlist, plugin, **kwargs):
        super(MusicPlayer, self).__init__(**kwargs)
        self.playlist = playlist
        self.plugin = plugin
        self.idx = 0
        self.pausing = False
        self.last_paused = None
        self.playing=False

    def updatePlayList(self,playlist):
        super().stop()
        self.playlist=playlist
        self.idx=0
        self.play()


    def run(self):
        pass

    def play(self):
        logger.debug('MusicPlayer play')
        path=self.playlist[self.idx]
        super().stop()        
        super().play(path, False, self.next)

    def next(self):
        logger.debug('MusicPlayer next')
        super().stop()
        self.idx=(self.idx+1)%len(self.playlist)
        self.play()
    
    def prev(self):
        logger.debug('MusicPlayer prev')
        super().stop()
        self.idx=(self.idx-1)%len(self.playlist)
        self.play()

    def pause(self):
        logger('MusinPlayer pause')
        self.pausing=True

    def stop(self):
        if self.proc:
            logger.debug('MusicPlayer stop')
            # STOP current play process
            self.last_paused = utils.write_temp_file(str(self.proc.pid), 'pid', 'w')
            self.onCompleteds = []
            subprocess.run(['pkill', '-STOP', '-F', self.last_paused])
    
    def resume(self):
        logger.debug('MusicPlayer resume')
        self.pausing=False
        self.onCompleteds=[self.next]
        if self.last_paused is not None:
            print(self.last_paused)
            subprocess.run(['pkill','-CONT','-F',self.last_paused])

    def is_playing(self):
        return self.playing

    def is_pausing(self):
        return self.pausing


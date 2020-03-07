# -*- coding:utf-8 -*-


from robot import Player,ASR,TTS,AI
import os
import requests
import uuid
from robot.Brain import Brain
from robot import logging,statistic,config,pcm_to_wav

logger = logging.getLogger(__name__)

class Conversation(object):

    def __init__(self):
        self.history = []
        self.player = None
    
    def doResponse(self,query):
        self.appendHistory(0, query)        
        brain = Brain(self)
        if not brain.DoQuery(query):     
            ai = AI.TulingRobot()
            respons = ai.chat(query)
            statistic.set(3)
            self.say(respons,True)          


    def converse(self,fp):  
        asr = ASR.XunfeiASR()
        queryt = asr.transcribe(fp)
        statistic.set(2)
        self.doResponse(queryt)
        os.remove(fp)
        
    def say(self,respons,delete = False):
        '''
        语音反馈（说一句话
        '''
        self.appendHistory(1, respons)
        logger.info(respons)
        self.player=Player.SoxPlayer()
        if config.get('/tts','B') =='B':
            tts = TTS.BaiduTTS()        
            tts.get_speach(respons)
            statistic.set(1)
            
            self.player.play('result.mp3',True)
        else:
            tts =TTS.XunFeiTTS()
            tts.get_speach(respons)
            statistic.set(1)
            pcm_to_wav.p_t_W()
            self.player.play('outfile/xunfei.wav',True)

    def getHistory(self):
        return self.history
    
    def stop(self):
        if self.player:
            self.player.stop()


    def appendHistory(self,type,text):
        if type in (0,1) and text != '':
            self.history.append({'type':type, 'text': text, 'uuid':str(uuid.uuid1())})


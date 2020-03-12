# -*- coding:utf-8 -*-
import os
import requests
import uuid
from robot.Brain import Brain
from robot import logging,statistic,config,utils,constants,Player,ASR,TTS,AI,NLU

logger = logging.getLogger(__name__)

class Conversation(object):

    def __init__(self):
        self.history = []
        self.player = None
        self.reInit()

    def reInit(self):
        """ 重新初始化 """
        try:
            self.asr = ASR.get_engine_by_slug(config.get('/asr_engine', 'xunfei-asr'))
            self.tts = TTS.get_engine_by_slug(config.get('/tts_engine', 'baidu-tts' ))
            self.nlu = NLU.get_engine_by_slug(config.get('/nlu_engine', 'baidu-unit'))
            self.player = None
            self.brain = Brain(self)
        except Exception as e:
            logger.critical("对话初始化失败：{}".format(e))

    def doResponse(self,query):
        self.appendHistory(0, query)        
        brain = Brain(self)
        if not brain.DoQuery(query):     
            ai = AI.TulingRobot()
            respons = ai.chat(query)
            statistic.set(3)
            self.say(respons,True)          


    def converse(self,fp):  
        queryt = self.asr.transcribe(fp)
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
        result = self.tts.get_speach(respons)
        statistic.set(1)            
        self.player.play(result,True)

    def getHistory(self):
        return self.history
    
    def stop(self):
        if self.player:
            self.player.stop()


    def appendHistory(self,type,text):
        if type in (0,1) and text != '':
            self.history.append({'type':type, 'text': text, 'uuid':str(uuid.uuid1())})


# -*- coding:utf-8 -*-
import os
import time
import requests
import uuid
from robot.Brain import Brain
from robot import logging,statistic,config,utils,constants,Player,ASR,TTS,AI,NLU,utils

logger = logging.getLogger(__name__)

class Conversation(object):

    def __init__(self):
        self.history = []
        
        self.reInit()
        self.pluginmod = None
        self.matchPlugin = None
        self.immersiveMode = None
        self.isRecording = False
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
        self.stop()
        self.appendHistory(0, query)        
        lastImmersiveMode = self.immersiveMode
        if not self.brain.query(query):
            # 没命中技能，使用机器人回复   
            ai = AI.TulingRobot()
            respons = ai.chat(query)
            statistic.set(3)
            self.say(respons,True, onCompleted=self.checkRestore)
        else:
            if lastImmersiveMode is not None and lastImmersiveMode != self.matchPlugin:
                time.sleep(1)
                if self.player is not None and self.player.is_playing():
                    logger.debug('等说完再checkRestore')
                    self.player.appendOnCompleted(lambda: self.checkRestore())
                else:
                    logger.debug('checkRestore')
                    self.checkRestore()
  
    def converse(self,fp): 
        Player.play('static/beep_lo.wav', wait = False)    
        queryt = self.asr.transcribe(fp)
        statistic.set(2)
        utils.check_and_delete(fp)
        self.doResponse(queryt)
      
    def doParse(self, query, **args):
        return self.nlu.parse(query, **args)

    def say(self,respons,delete = False, onCompleted=None,wait=False):
        '''
        语音反馈（说一句话
        '''

        self.appendHistory(1, respons)
        logger.info(respons)
        self.player=Player.SoxPlayer()
        result = self.tts.get_speech(respons)
        statistic.set(1)            
        self.player.play(result,delete = True, onCompleted=onCompleted, wait = True)

    def getHistory(self):
        return self.history
    
    def stop(self):
        if self.player is not None and self.player.is_playing():
            self.player.stop()
            self.player = None
        if self.immersiveMode:
            self.brain.pause()

    def appendHistory(self,type,text):
        if type in (0,1) and text != '':
            self.history.append({'type':type, 'text': text, 'uuid':str(uuid.uuid1())})

    def checkRestore(self):
        if self.immersiveMode:
            self.brain.restore()

    def setImmersiveMode(self, slug):
        self.immersiveMode = slug

    def getImmersiveMode(self):
        return self.immersiveMode
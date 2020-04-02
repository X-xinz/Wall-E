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

    def say(self,msg,cache = False, onCompleted=None,wait=False):
        '''
        语音反馈（说一句话
        '''

        self.appendHistory(1, msg)
        logger.info(msg)
        voice = ''
        cache_path = ''
        if utils.getCache(msg):
            logger.info("命中缓存，播放缓存语音")
            voice = utils.getCache(msg)
            cache_path = utils.getCache(msg)
        else:
            try:
                voice = self.tts.get_speech(msg)
                cache_path = utils.saveCache(voice, msg)
            except Exception as e:
                logger.error('保存缓存失败：{}'.format(e))
        self.player=Player.SoxPlayer()
<<<<<<< HEAD
        
=======
        result = self.tts.get_speech(respons)
>>>>>>> 6095ebb181ac71d27cfa62e9c3aafc05af796ef9
        statistic.set(1)            
        self.player.play(voice,not cache, onCompleted, wait)
        if not cache:
            utils.check_and_delete(cache_path, 60) # 60秒后将自动清理不缓存的音频
        utils.lruCache()  # 清理缓存

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


    def play(self, src, delete=False, onCompleted=None, volume=1):
        """ 播放一个音频 """
        if self.player:
            self.stop()
        self.player = Player.SoxPlayer()
        self.player.play(src, delete=delete, onCompleted=onCompleted)
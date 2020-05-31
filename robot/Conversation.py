# -*- coding:utf-8 -*-
import os
import time
import requests
import uuid
from robot.Brain import Brain
from snowboy import snowboydecoder
from robot import logging,statistic,config,utils,constants,Player,ASR,TTS,AI,NLU

logger = logging.getLogger(__name__)

class Conversation(object):

    def __init__(self):
        self.history = []
        
        self.reInit()
        self.pluginmod = None
        self.matchPlugin = None
        self.immersiveMode = None
        self.isRecording = False
        self.hasPardon = False

    def reInit(self):
        """ 重新初始化 """
        try:
            self.asr = ASR.get_engine_by_slug(config.get('/asr_engine', 'xunfei-asr'))
            self.tts = TTS.get_engine_by_slug(config.get('/tts_engine', 'baidu-tts' ))
            self.nlu = NLU.get_engine_by_slug(config.get('/nlu_engine', 'baidu-unit'))
            self.ai = AI.get_robot_by_slug(config.get('/ai_engine', 'tuling'))
            self.player = None
            self.brain = Brain(self)
        except Exception as e:
            logger.critical("对话初始化失败：{}".format(e))
    
    def converse(self,fp): 
        Player.play('static/beep_lo.wav', wait = False)    
        queryt = self.asr.transcribe(fp)
        statistic.set(2)
        utils.check_and_delete(fp)
        self.doResponse(queryt)

    def doResponse(self,query):
        self.stop()
        self.appendHistory(0, query)
        logger.info(query)   
        lastImmersiveMode = self.immersiveMode
        if not self.brain.query(query):
            # 没命中技能，使用机器人回复
            
            respons = self.ai.chat(query)
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
                statistic.set(1) 
            except Exception as e:
                logger.error('保存缓存失败：{}'.format(e))
        if onCompleted is None:
            onCompleted = lambda: self._onCompleted(msg) 
        self.player=Player.SoxPlayer()       
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
        """
        添加会话历史

        :param type: 类型，0代表用户输入，1为技能或机器人回复
        :param text: 对话内容
        """
        if type in (0,1) and text != '':
            self.history.append({'type':type, 'text': text, 'uuid':str(uuid.uuid1())})

    def checkRestore(self):
        if self.immersiveMode:
            self.brain.restore()

    def setImmersiveMode(self, slug):
        self.immersiveMode = slug

    def getImmersiveMode(self):
        return self.immersiveMode

    def _onCompleted(self, msg):
        if config.get('active_mode', False) and \
           (
               msg.endswith('?') or 
               msg.endswith(u'？') or 
               u'告诉我' in msg or u'请回答' in msg
           ):
            query = self.activeListen()
            self.doResponse(query)

    def pardon(self):
        if not self.hasPardon:
            self.say("抱歉，刚刚没听清，能再说一遍吗？", onCompleted=lambda: self.doResponse(self.activeListen()))
            self.hasPardon = True
        else:
            self.say("没听清呢")
            self.hasPardon = False

    def play(self, src, delete=False, onCompleted=None, volume=1):
        """ 播放一个音频 """
        if self.player:
            self.stop()
        self.player = Player.SoxPlayer()
        self.player.play(src, delete=delete, onCompleted=onCompleted)

    def activeListen(self, silent = False):
        """主动询问问题开启新一轮对话"""
        logger.info('activeListen')
        try:
            if not silent:
                #time sleep(1)
                Player.play('static/beep_hi.wav')
            listener = snowboydecoder.ActiveListener([config.get('/snowboy/hotwork', 'snowboy/resources/snowboy.umdl')])
            voice = listener.listen(
                silent_count_threshold=config.get('/silent_threshold', 15),
                recording_timeout=config.get('/recording_timeout', 5) * 4
            )
            if not silent:
                Player.play('static/beep_lo.wav')
            if voice:
                query = self.asr.transcribe(voice)
                utils.check_and_delete(voice)
                return query
            return ''
        except Exception as e:            
            logger.error(e)
            return ''        
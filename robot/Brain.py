#-*- coding=utf-8 -*-
import pkgutil
from robot import config
import requests
from robot import logging
from plugins import Weather
from robot.sdk.AbstractPlugin import AbstractPlugin

logger = logging.getLogger(__name__)

class Brain(object):
    
    def __init__(self, con):
      self.con = con
      self.plugins = self.init_plugins()

    def hasDisable(self,name):
        if config.has('/{}/enable'.format(name)):
            if not config.get('/{}/enable'.format(name)):
                logger.info('插件{}已经被禁用！'.format(name))
                return True
        return False
        
    def init_plugins(self):
        """
        读取所有插件
        """
        plugins = []
        for finder,name,_ispkg in pkgutil.walk_packages(['plugins']):
            try:
                loader = finder.find_module(name) 
                mod = loader.load_module(name)
            except Exception as e:
                logger.error(e)
                continue
            if hasattr(mod, 'Plugin') and issubclass(mod.Plugin,AbstractPlugin) and \
                not self.hasDisable(name):       
                plugins.append(mod.Plugin(self.con))
        return plugins 
            

    def DoQuery(self,query):
        
        for plugin in self.plugins:
            if plugin.isValib(query):
                #存在技能，开启技能支路
                plugin.handle(query)
                return True
        
        #技能不存在，使用机器人回复
        return False
        
        

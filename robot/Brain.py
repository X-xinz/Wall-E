#-*- coding=utf-8 -*-
import pkgutil
from robot import config
import requests
from robot import logging
from plugins import Weather
from .plugin_loader import get_plugins
from robot.sdk.AbstractPlugin import AbstractPlugin

logger = logging.getLogger(__name__)

class Brain(object):
    
    def __init__(self, con):
      self.con = con
      self.plugins = get_plugins(self.con)

    def DoQuery(self,query):
        
        for plugin in self.plugins:
            if plugin.isValid(query,parsed=None):
                #存在技能，开启技能支路
                plugin.handle(query,parsed=None)
                return True
        
        #技能不存在，使用机器人回复
        return False
        
        

# -*- coding:utf-8 -*-

import requests 
import hashlib
import base64
import json
import time
import uuid 

from robot import config,constants
from robot import logging

logger = logging.getLogger(__name__)

class AbstactRobot(object):

    def chat(self,query):
        pass

class TulingRobot(AbstactRobot):

    '''
    图灵Robot
    '''
    
    SLUG = 'tuling-robot'
    def __init__(self):
        self.api_key = config.get('/tuling_robot/api_key','348fa9691d654c3daead676f60ace54e')
    def chat(self,query):

        URL = constants.tuling_robot_URL
        paramsms = {
            "reqType":0,
            "perception": {
                "inputText": {
                    "text": query
                }
            },
            "userInfo": {                
                "apiKey": self.api_key,
                "userId": constants.mac_id
            }           
        }

        r =requests.post(URL,data = json.dumps(paramsms))
        r.encoding = 'utf-8'
        res = r.json()

        try:
            results =res['results']       #遍历
            for result in results:
                 if result['resultType'] == 'text':
                     return result['values']['text']
        except Exception as e:
            logger.error(e)
            return ''
            
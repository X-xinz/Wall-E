#-*- coding=utf-8 -*-

from robot.sdk.AbstractPlugin import AbstractPlugin
import requests,yaml
from robot import config,logging,statistic

logger = logging.getLogger(__name__)


class Plugin(AbstractPlugin):
    def handle(self,query):
        statistic.set(5)
        city = config.get('/Weather/location','武汉')
        url = 'https://free-api.heweather.net/s6/weather/forecast?parameters'
        params = {
            "location": city,
            "key": "1420905c8e0941bb841cee7e20cffefe"
        }
        r = requests.get(url,params = params)
        r.encoding = "utf-8"
        try:
            results = r.json()['HeWeather6'][0]['daily_forecast']
            logger.debug(results)
            res = '{}:'.format(city)
            day_lable = ['今天','明天','后天']
            i = 0
            for result in results:
                tmp_min,tmp_max,cond_txt_d,cond_txt_n =result['tmp_min'],result['tmp_max'],result['cond_txt_d'],result['cond_txt_n']
                res +='{}:白天{},夜间{},气温{}到{}摄氏度;'.format(day_lable[i],cond_txt_d,cond_txt_n,tmp_min,tmp_max)
                i += 1
            self.con.say(res,True)
        except Exception as e:
            logger.error(e)
            self.con.say('天气查询失败了',True)         

    def isValib(self,query):
        return '天气' in query
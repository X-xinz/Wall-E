# -*- coding:utf-8 -*-
import base64
import datetime
import hashlib
import hmac
import json
import os
import ssl
import sys
import time
from abc import ABCMeta, abstractmethod
from datetime import datetime
from time import mktime
from urllib.error import HTTPError
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen
from wsgiref.handlers import format_date_time

import websocket
import yaml

import _thread as thread
from robot import Player, config, constants, logging

from ..utils import p_t_W

logger = logging.getLogger(__name__)
STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识
ASR_wsParam = None
gresult = ''
wsParam =()


class ASR_Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, AudioFile):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.AudioFile = AudioFile

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn",\
             "accent":"mandarin", "vinfo":1,"vad_eos":10000}

    # 生成url
    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        # 进行hmac-sha256进行加密

        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # logger.debug("date: ",date)
        # logger.debug("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # logger.debug('websocket url :', url)
        return url

class TTS_wsParam(object):
    # 初始化
    def __init__(self, APPID, APIKey, apisecret, Text):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = apisecret
        self.Text = Text

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": "x_xiaoshi_cts", "tte": "utf8","ent":"aisound","speed":45}
        self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}
        #使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
        #self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-16')), "UTF8")}

    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url

def TTS_on_message(ws, message):
    try:
        message =json.loads(message)
        code = message["code"]
        sid = message["sid"]
        audio = message["data"]["audio"]
        audio = base64.b64decode(audio)
        status = message["data"]["status"]
        #print(message)
        if status == 2:
            logger.debug("ws is closed")
            ws.close()
        if code != 0:
            errMsg = message["message"]
            logger.debug("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
        else:
            with open(constants.PCM_PATH, 'ab') as f:
                f.write(audio)
    except Exception as e:
        logger.error("receive msg,but parse exception:%s"%(e))

# 收到websocket消息的处理
def ASR_on_message(ws, message):
    global gresult
    try:
        code = json.loads(message)["code"]
        sid = json.loads(message)["sid"]
        if code != 0:
            errMsg = json.loads(message)["message"]
            logger.debug("sid:%s call error:%s code is:%s" % (sid, errMsg, code))

        else:
            data = json.loads(message)["data"]["result"]["ws"]
            # logger.debug(json.loads(message))
            result = ""
            for i in data:
                for w in i["cw"]:
                    result += w["w"]
            gresult = gresult + result
            #logger.debug("sid:%s call success!,data is:%s" % (sid, json.dumps(data, ensure_ascii=False)))
    except Exception as e:
        logger.debug("receive msg,but parse exception:%s"%(e))



# 收到websocket错误的处理
def ASR_on_error(ws, error):
    logger.debug("### error:%s"%(error))

def TTS_on_error(ws, error):
    logger.error("### error:%s"%(error))


# 收到websocket关闭的处理
def ASR_on_close(ws):
    pass
    logger.debug("### XunfeiASR closed ###")

def TTS_on_close(ws):
    logger.debug("###XunfeiTTS closed ###")


# 收到websocket连接建立的处理
def ASR_on_open(ws):
    global ASR_wsParam
    def run(*args):
        frameSize = 8000  # 每一帧的音频大小
        intervel = 0.04  # 发送音频间隔(单位:s)
        status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

        with open(ASR_wsParam.AudioFile, "rb") as fp:
            while True:
                buf = fp.read(frameSize)
                # 文件结束
                if not buf:
                    status = STATUS_LAST_FRAME
                # 第一帧处理
                # 发送第一帧音频，带business 参数
                # appid 必须带上，只需第一帧发送
                if status == STATUS_FIRST_FRAME:

                    d = {"common": ASR_wsParam.CommonArgs,
                         "business": ASR_wsParam.BusinessArgs,
                         "data": {"status": 0, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    d = json.dumps(d)
                    ws.send(d)
                    status = STATUS_CONTINUE_FRAME
                # 中间帧处理
                elif status == STATUS_CONTINUE_FRAME:
                    d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                # 最后一帧处理
                elif status == STATUS_LAST_FRAME:
                    d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                    time.sleep(1)
                    break
                # 模拟音频采样间隔
                time.sleep(intervel)
        ws.close()

    thread.start_new_thread(run, ())

def TTS_on_open(ws):
    def run(*args):
        d = {"common": wsParam.CommonArgs,
             "business": wsParam.BusinessArgs,
             "data": wsParam.Data,
             }
        d = json.dumps(d)
        logger.debug("------>开始发送文本数据")
        ws.send(d)
        if os.path.exists('./demo.pcm'):
            os.remove('./demo.pcm')

    thread.start_new_thread(run, ())

def transcribe(fpath,appid,apikey,apisecret,**arges):
    '''
    科大讯飞asr
    '''
    global ASR_wsParam
    global gresult
    gresult = ''
    time1 = datetime.now()
    ASR_wsParam = ASR_Ws_Param(APPID = appid,APIKey = apikey,APISecret=apisecret,AudioFile=fpath)
    websocket.enableTrace(False)
    wsUrl = ASR_wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=ASR_on_message, on_error=ASR_on_error, on_close=ASR_on_close)
    ws.on_open = ASR_on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    time2 = datetime.now()
    logger.debug(time2-time1)
    return gresult

def get_speach(Text,appid,apikey,apisecret):
    '''xunfei-tts'''
    global wsParam
   
    wsParam = TTS_wsParam(APPID=appid, APIKey=apikey, apisecret=apisecret, Text=Text)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=TTS_on_message, on_error=TTS_on_error, on_close=TTS_on_close)
    ws.on_open = TTS_on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    
    resurt = p_t_W(constants.PCM_PATH,'xunfei-wav',True)
    logger.debug("xunfei-wav saved as :{}".format(resurt))
    return resurt

#存入固定常量
import os
from robot import config
from uuid import getnode as get_mac
APP_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.pardir))

LIB_PATH = os.path.join(APP_PATH, "robot")
DATA_PATH = os.path.join(APP_PATH, "static")
TEMP_PATH = os.path.join(APP_PATH, "temp")
OUTFILES_PATH = os.path.join(APP_PATH, "outfile")
TEMPLATE_PATH = os.path.join(APP_PATH, "server", "templates")
PLUGIN_PATH = os.path.join(APP_PATH, "plugins")
DEFAULT_CONFIG_NAME = 'default.yml'
CUSTOM_CONFIG_NAME = 'config.yml'
CONTRIB_PATH = os.path.expanduser(
    os.getenv('WUKONG_CONFIG', '~/.wukong/contrib')
)
CUSTOM_PATH = os.path.expanduser(
    os.getenv('WUKONG_CONFIG', '~/.wukong/custom')
)
CONFIG_PATH = 'config.yml'
LOGGING_PATH = 'outfile/wukong.log'
DB_PATH ='outfile/response.db'
NEWDB_PATH ='outfile/response'
PCM_PATH='outfile/demo.pcm'
XUNFEITTS_PATH='outfile/xunfei.wav'
Baidu_tts_apikey = 'B4YtVa1VWkn0vdIX9Yawx7Im'
Baidu_tts_secret_key = 'rM7vQN2YatVrhFv1MTzepDXPWpoA4h5e'
Baidu_TTS_URL = 'http://tsn.baidu.com/text2audio'
Baidu_tts_SCOPE = 'audio_tts_post'      # 有此scope表示有tts能力，没有请在网页里勾选
Baidu_tts_TOKEN_URL = 'http://openapi.baidu.com/oauth/2.0/token'
tuling_robot_URL = "http://openapi.tuling123.com/openapi/api/v2"
mac_id =str(get_mac())[:32]              #cuid,身份识别符
LOG = 'DEBUG'                     #log 打印等级（debug/info)
def getConfigPath():
    """
    返回配置文件的完整路径
    :returns:配置文件的完整路径
    """
    return os.path.join(APP_PATH, CONFIG_PATH)
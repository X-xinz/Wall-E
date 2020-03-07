from robot.sdk.AbstractPlugin import AbstractPlugin
from robot import config,logging,statistic
import os

logger = logging.getLogger(__name__)


class Plugin(AbstractPlugin):
    IS_IMMERSIVE = True  # 这是个沉浸式技能


    def __init__(self, con):
        super(Plugin, self).__init__(con)
        self.player = None

    def hand(self,query):
        musicList = self.get_song_list(config.get('/LocalPlayer/path'))
        if musicList == None:
            logger.error('{}插件配置有误'.format(musicList))
        logger.info(musicList)

    def get_song_list(self,path):
        if not os.path.exists(path) or not os.path.isdir(path):
            return []
        #filter():用于过滤序列，过滤掉不符合条件的元素，返回一个迭代器对象，如果要转换为列表，可以使用 list() 来转换。
        flist = list(filter(lambda d: d.endswith('.mp3'), os.listdir(path)))
        return flist

    def restore(self,query):
        pass

    def pause(self):
        pass

    def isValidImmersive(self, text, parsed):
        return False

    def isValib(self,query):
        return '音乐' in query
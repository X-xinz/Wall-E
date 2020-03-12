""" import os

from robot import config, logging, statistic
from robot.Player import MusicPlayer
from robot.sdk.AbstractPlugin import AbstractPlugin

logger = logging.getLogger(__name__)


class Plugin(AbstractPlugin):
    SLUG = 'LocalPlayer'
    IS_IMMERSIVE = True  # 这是个沉浸式技能


    def __init__(self, con):
        super(Plugin, self).__init__(con)
        self.player = None
        self.song_List=None

    def init_music_player(self):
        self.song_List = self.get_song_list(config.get('/LocalPlayer/path'))
        if self.song_List == None:
            logger.error('{}插件配置有误'.format(self.song_List))
        logger.info('本地音乐列表:{}'.format(self.song_List))
        return MusicPlayer(self.song_List,self)
    
    def handle(self,text,parsed):
        if not self.player:
            self.player=self.init_music_player()
        if len(self.song_List)==0:
            self.clearImmersive() #去除沉浸模式
            self.say('本地音乐目录为空，请添加音乐后重试')
            return
        if self.nlu.hasIntent(parsed, 'MUSICRANK'):
            self.player.play()
        elif self.nlu.hasIntent(parsed, 'CHANGE_TO_NEXT'):
            self.player.next()
        elif self.nlu.hasIntent(parsed, 'CHANGE_TO_LAST'):
            self.player.prev()
        elif self.nlu.hasIntent(parsed, 'PAUSE'):
            self.player.pause()
        elif self.nlu.hasIntent(parsed, 'CONTINUE'):
            self.player.resume()
        elif self.nlu.hasIntent(parsed, 'CLOSE_MUSIC'):
            self.player.stop()
            self.clearImmersive()  # 去掉沉浸式
        else:
            self.say('没听懂你的意思呢，要停止播放，请说停止播放', wait=True)
            self.player.resume()

    def get_song_list(self,path):
        if not os.path.exists(path) or not os.path.isdir(path):
            return []
        #filter():用于过滤序列，过滤掉不符合条件的元素，返回一个迭代器对象，如果要转换为列表，可以使用 list() 来转换。
        flist = list(filter(lambda d: d.endswith('.mp3'), os.listdir(path)))
        return flist

    def restore(self,query):
        if self.player and not self.player.is_pausing():
            self.player.resume()

    def pause(self):
        if self.player:
            self.player.stop()

    def isValidImmersive(self, text, parsed):
        return any(self.nlu.hasIntent(parsed, intent) for intent in ['CHANGE_TO_LAST', 'CHANGE_TO_NEXT', 'CHANGE_VOL', 'CLOSE_MUSIC', 'PAUSE', 'CONTINUE'])

    def isValib(self,query):
        return '音乐' in query
 """
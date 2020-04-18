import tornado.ioloop
import tornado.web
import sys
import json
import threading
import asyncio
import yaml
import os,time
from robot import config,logging,statistic

logger = logging.getLogger(__name__)

conversation = None

class BassHandler(tornado.web.RequestHandler):
    def get_current_user(self):       
        return self.get_secure_cookie('user')

class MainHandler(BassHandler):
    global conversation
    def get(self):
        if not self.current_user :
            self.redirect("/login")
            return        
        self.render('index.html', history=conversation.getHistory())

class LoginHandler(BassHandler):
    def get(self):
        if self.current_user:
            type(self.get_secure_cookie('user'))
            self.redirect('/')#重定向到首页
            return
        self.render('login.html')
        
    def post(self):
        if config.get('/server/password')==self.get_argument('password',default='') and 'yin'==self.get_argument('name',default=''):
            self.set_secure_cookie("user", self.get_argument("name"),expires_days=2,expires=time.time()+9000)  
            self.redirect("/")
        else:
            self.redirect("/login")
            logger.warning('登录失败')

class ConfigHandler(BassHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return
        self.render('config.html', config=config.getText())

    def post(self):
        if not self.current_user:
            res ={'code': 1, 'message':'illegal visit'}
            self.write(json.dumps(res))
        else:
            configStr = self.get_argument('config')
            try:
                yaml.load(configStr)
                config.dump(configStr)
                res ={'code': 0 ,'message':'ok'}
                self.write(json.dumps(res))
                logger.debug("配置更改成功")
            except:
                res ={'code': 1 ,'message':'YAML解析失败，请检查内容'}
                logger.debug("YAML解析失败，请检查内容")
                self.write(json.dumps(res))
        self.finish()

class LogHandler(BassHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return
        self.render('log.html',log=logging.readLog())

class GetLogHandler(BassHandler):
    def get(self):
        global conversation
        if not self.current_user:
            res ={'code': 1, 'message':'illegal visit'}
        else:   
            res ={'code': 0 ,'message':'ok', 'log': logging.readLog()}
        self.write(json.dumps(res))
        self.finish()

class HistoryHandler(BassHandler):    
    def get(self):
        global conversation
        if not self.current_user:
            res ={'code': 1, 'message':'illegal visit'}
        else:   
            res ={'code': 0 ,'message': 'ok', 'history':json.dumps(conversation.getHistory())}
        self.write(json.dumps(res))
        self.finish()

class ChatHandler(BassHandler):

    def post(self):
        global conversation
        if not self.current_user:
            res ={'code': 1, 'message':'illegal visit'}
        else:
            query = self.get_argument('query')
            if query == '':
                res = {'code': 1, 'message': 'query is empty'}
            else:
                conversation.doResponse(query)
                res = {'code': 0, 'message': 'ok'}
        self.write(json.dumps(res))
        self.finish()

class OperateHandler(BassHandler):
    def post(self):
        if not self.current_user:
            res ={'code': 1, 'message':'illegal visit'}
            self.write(json.dumps(res))
            self.finish()
        else:
            res = {'code': 0, 'message': 'ok'}
            self.write(json.dumps(res))
            self.finish()
            logger.debug("重启成功")
            python = sys.executable
            os.execl(python,python,*sys.argv)

class ResHandler(BassHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return
        self.render('statistic.html',plugs=statistic.get_numb())

settings = {
       
    "cookie_secret": config.get('/server/cookie_secret',''),
    "template_path": "server/templates",
    "static_path": "server/static",
    "debug": config.get('/server/debug', 'False'),
}

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/login",LoginHandler),
        (r"/config",ConfigHandler),
        (r"/log",LogHandler),
        (r"/history",HistoryHandler),
        (r"/chat",ChatHandler),
        (r"/getlog", GetLogHandler),
        (r"/operate",OperateHandler),
        (r"/statistic",ResHandler),
    ],  **settings )

      
app = make_app()

def start_server():
    asyncio.set_event_loop(asyncio.new_event_loop())
    app.listen(config.get('/server/port', 5000))
    tornado.ioloop.IOLoop.current().start()

def run(con):
    global conversation
    conversation = con
    threading.Thread(target = start_server).start()

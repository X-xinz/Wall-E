#-*- coding=utf-8 -*-

class AbstractPlugin(object):
    def __init__(self, con):
        self.con = con


    def hand(self,query):
        pass


    def isValib(self,query):
        return False
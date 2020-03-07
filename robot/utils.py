import os

def check_and_delete(fpath):
    '''
    检查文件是否存在并删除
    '''

    if os.path.exists(fpath):
        os.remove(fpath)
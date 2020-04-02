import os
import tempfile
import wave
<<<<<<< HEAD
import time
import hashlib
import shutil
from robot import constants,utils,config
import _thread as thread
import subprocess
=======
from robot import constants, utils

>>>>>>> 6095ebb181ac71d27cfa62e9c3aafc05af796ef9

def check_and_delete(fpath,wait=0):
    '''
    检查文件是否存在并删除
    '''
    def run():
        if wait > 0:
            time.sleep(wait)
        if isinstance(fpath, str) and os.path.exists(fpath):
            if os.path.isfile(fpath):
                os.remove(fpath)
            else:
                shutil.rmtree(fpath)
    
    thread.start_new_thread(run, ())


def lruCache():
    """ 清理最近未使用的缓存 """
    def run(*args):
        if config.get('/lru_cache/enable', True):            
            days = config.get('/lru_cache/days', 7)
            subprocess.run('find . -name "*.mp3" -atime +%d -exec rm {} \;' % days, cwd=constants.OUTFILES_PATH, shell=True)

    thread.start_new_thread(run, ())


def write_temp_file(data, suffix, mode='w+b'):
    """ 
    写入临时文件

    :param data: 数据
    :param suffix: 后缀名
    :param mode: 写入模式，默认为 w+b
    :returns: 文件保存后的路径
    """
    with tempfile.NamedTemporaryFile(mode=mode, suffix=suffix, delete=False) as f:
        f.write(data)
        tmpfile = f.name
    return tmpfile


def get_pcm_from_wav(wav_path):
    """ 
    从 wav 文件中读取 pcm

    :param wav_path: wav 文件路径
    :returns: pcm 数据
    """
    wav = wave.open(wav_path, 'rb')
    return wav.readframes(wav.getnframes())

<<<<<<< HEAD

def getCache(msg):
    """ 获取缓存的语音 """
    md5 = hashlib.md5(msg.encode('utf-8')).hexdigest()
    mp3_cache = os.path.join(constants.OUTFILES_PATH, md5 + '.mp3')
    wav_cache = os.path.join(constants.OUTFILES_PATH, md5 + '.wav')
    if os.path.exists(mp3_cache):
        return mp3_cache
    elif os.path.exists(wav_cache):
        return wav_cache
    return None

def saveCache(voice, msg):
    """ 获取缓存的语音 """
    _foo, ext = os.path.splitext(voice)
    md5 = hashlib.md5(msg.encode('utf-8')).hexdigest()
    target = os.path.join(constants.OUTFILES_PATH, md5+ext)
    shutil.copyfile(voice, target)
    return target




def p_t_W(pcm_path,wavname,delect=False):
=======
def p_t_W(pcm_path, wavname, delete=False):
>>>>>>> 6095ebb181ac71d27cfa62e9c3aafc05af796ef9
    """
    pcm to wav
    :param pcm_path:pcm路径
    :param wavname:要生成的wav文件名
    :param delete:是否删除pcm文件，默认false
    :returns: 返回wav文件路径
    """
    f = open(pcm_path, 'rb')
    str_data = f.read()
    wav_path = os.path.join(constants.OUTFILES_PATH, wavname)
    wave_out = wave.open(wav_path, 'wb')
    wave_out.setnchannels(1)
    wave_out.setsampwidth(2)
    wave_out.setframerate(16000)
    wave_out.writeframes(str_data)
    if delete:
        check_and_delete(pcm_path)
    return wav_path

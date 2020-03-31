import os
import tempfile
import wave
from robot import constants, utils


def check_and_delete(fpath):
    '''
    检查文件是否存在并删除
    '''

    if os.path.exists(fpath):
        os.remove(fpath)


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

def p_t_W(pcm_path, wavname, delete=False):
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

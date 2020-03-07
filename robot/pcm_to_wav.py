import wave
import os
from robot import constants,utils

def p_t_W():
    f = open(constants.PCM_PATH,'rb')
    str_data  = f.read()
    wave_out=wave.open("outfile/xunfei.wav",'wb')
    wave_out.setnchannels(1)
    wave_out.setsampwidth(2)
    wave_out.setframerate(16000)
    wave_out.writeframes(str_data)
    utils.check_and_delete(constants.PCM_PATH)

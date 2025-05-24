import API_Key_utils
import numpy as np
import sys
from aip import AipSpeech
from playsound import playsound
import pyaudio
import wave
import requests
import json
import os

def recode_by_linux(MIC_INDEX = 0, DURATION = 5):
    '''
    在linux中使用直接使用命令arecord录音
    MIC_INDEX 麦克风ID
    DURATION 录音时长
    '''
    print("开始录音，时长为{}".format(DURATION))
    os.system('sudo arecord -D "plughw:{}" -f dat -c 1 -r 16000 -d {} temp/speech_record.wav'.format(MIC_INDEX, DURATION))
    print('录音结束')


def record_auto(MIC_INDEX=0):
    '''
    开启麦克风录音，保存至'temp/speech_record.wav'音频文件
    音量超过阈值自动开始录音，低于阈值一段时间后自动停止录音
    MIC_INDEX：麦克风设备索引号
    '''

    CHUNK = 1024  # 采样宽度
    RATE = 16000  # 采样率

    QUIET_DB = 2000  # 分贝阈值，大于则开始录音，否则结束
    delay_time = 1  # 声音降至分贝阈值后，经过多长时间，自动终止录音

    FORMAT = pyaudio.paInt16
    #CHANNELS = 1 if sys.platform == 'darwin' else 2  # 采样通道数
    CHANNELS = 1

    # 初始化录音
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    # input_device_index=MIC_INDEX
                    )

    frames = []  # 所有音频帧

    flag = False  # 是否已经开始录音
    quiet_flag = False  # 当前音量小于阈值
    temp_time = 0  # 当前时间是第几帧
    last_ok_time = 0  # 最后正常是第几帧
    START_TIME = 0  # 开始录音是第几帧
    END_TIME = 0  # 结束录音是第几帧

    print('可以说话啦！')

    while True:

        # 获取当前chunk的声音
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
        # 获取当前chunk的音量分贝值
        temp_volume = np.max(np.frombuffer(data, dtype=np.short))

        if temp_volume > QUIET_DB and flag == False:
            print("音量高于阈值，开始录音")
            flag = True
            START_TIME = temp_time
            last_ok_time = temp_time

        if flag:  # 录音中的各种情况

            if (temp_volume < QUIET_DB and quiet_flag == False):
                print("录音中，当前音量低于阈值")
                quiet_flag = True
                last_ok_time = temp_time

            if (temp_volume > QUIET_DB):
                # print('录音中，当前音量高于阈值，正常录音')
                quiet_flag = False
                last_ok_time = temp_time

            if (temp_time > last_ok_time + delay_time * 15 and quiet_flag == True):
                print("音量低于阈值{:.2f}秒后，检测当前音量".format(delay_time))
                if (quiet_flag and temp_volume < QUIET_DB):
                    print("当前音量仍然小于阈值，录音结束")
                    END_TIME = temp_time
                    break
                else:
                    print("当前音量重新高于阈值，继续录音中")
                    quiet_flag = False
                    last_ok_time = temp_time

        # print('当前帧 {} 音量 {}'.format(temp_time+1, temp_volume))
        temp_time += 1
        if temp_time > 150:  # 超时直接退出
            END_TIME = temp_time
            print('超时，录音结束')
            break

    # 停止录音
    stream.stop_stream()
    stream.close()
    p.terminate()

    # 导出wav音频文件
    output_path = 'temp/speech_record.wav'
    wf = wave.open(output_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    #wf.writeframes(b''.join(frames[START_TIME - 2:END_TIME]))
    wf.writeframes(b''.join(frames))
    wf.close()
    print('保存录音文件', output_path)


# 百度语音识别api权限验证
client = AipSpeech(API_Key_utils.BAIDU_APP_ID, API_Key_utils.BAIDU_API_KEY, API_Key_utils.BAIDU_SECRET_KEY)
def recognize_speech(audio_path="temp/speech_record.wav"):
    with open(audio_path, 'rb') as fp:
        audio_data = fp.read()

    result = client.asr(audio_data, 'wav', 16000, {'dev_pid': 1536})

    if 'result' in result:
        return result['result'][0]
    else:
        return None

if __name__ == '__main__':
    record_auto()
    print(recognize_speech())
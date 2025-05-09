from aip import AipSpeech
import os
import tempfile
import speech_recognition as sr
import playsound

# 配置信息（需要替换为你的实际信息）（https://console.bce.baidu.com/ai-engine/speech/overview/index）
APP_ID = ''
API_KEY = ''
SECRET_KEY = ''
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

r = sr.Recognizer()
mic = sr.Microphone()

def speech_to_text():
    """语音识别"""  
    try:
        with mic as source:
            print("请说话：")
            r.adjust_for_ambient_noise(source, duration=0.5)  # 调整环境噪声
            audio = r.listen(source)  # 设置超时为5秒
        audio_bytes = audio.get_wav_data(convert_rate=16000)
        result = client.asr(audio_bytes, 'wav', 16000, {'dev_pid': 1537})
        print(result)
        if result['err_no'] == 0:
            return result['result'][0]
        else:
            print(f"语音识别失败，错误码：{result['err_no']}")
            return "语音识别失败"
    except Exception as e:
        print(f"语音识别异常: {str(e)}")
        return "语音识别异常"

def text_to_speech(text):
    """语音合成"""
    try:
        result = client.synthesis(text, 'zh', 1, {'vol': 5, 'per': 4})
        if not isinstance(result, dict):
            fd, path = tempfile.mkstemp(suffix='.mp3')
            with os.fdopen(fd, 'wb') as f:
                f.write(result)
            return path
        return None
    except Exception as e:
        print(f"语音合成异常: {str(e)}")
        return None


recognize = speech_to_text()
print("识别结果:", recognize)
path = text_to_speech(recognize)

if path:
    playsound.playsound(path)   
    print("播放完成")

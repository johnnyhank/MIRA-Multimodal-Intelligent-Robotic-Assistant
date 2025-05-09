# 更新系统组件，运行过程中一路选择yes
sudo apt-get update
sudo apt-get upgrade

# pyaudio依赖库
sudo apt-get install portaudio19-dev

# 语音模块
pip install pyaudio chardet playsound

# OCR
pip install opencv-python 

# Ernie Bot
pip install erniebot

# 百度AI开放平台的Python SDK
pip install baidu-aip

# 安装 SpeechRecognition 包
pip install SpeechRecognition -i https://pypi.tuna.tsinghua.edu.cn/simple 
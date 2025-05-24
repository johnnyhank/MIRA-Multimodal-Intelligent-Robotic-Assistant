import gradio as gr
import asyncio
import sys
import wave
import threading
from utils_spe_rec import *
from utils_cam import *
from utils_robot import *
from utils_vlm import *
from utils_vlm_move import *
from utils_tts import *
from utils_micro_bit import *
from start import command_cleaning
from pydub import AudioSegment
from utils_qwen_agent import bot, qwen_agent
def convert_to_wav16k1c(src_path, dst_path):
    audio = AudioSegment.from_file(src_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(dst_path, format="wav")

def check_wav_info(audio_path):
    try:
        with wave.open(audio_path, 'rb') as wf:
            print("channels:", wf.getnchannels())
            print("framerate:", wf.getframerate())
            print("sampwidth:", wf.getsampwidth())
    except Exception as e:
        print("音频文件检查失败：", e)
        
def play_tts_in_background(text):
    asyncio.run(text_to_speech(text))
def process_input(text, audio, image, chatbot_state):
    if chatbot_state is None:
        chatbot_state = []

    # 处理语音输入
    if audio is not None:
        tmp_path = "/tmp/converted.wav"
        convert_to_wav16k1c(audio, tmp_path)
        print("语音识别结果：", text)
        if text is not None and text != "":
            text = text + "," + recognize_speech(tmp_path)
        else:
            text = recognize_speech(tmp_path)
        # text = text + "," + recognize_speech(tmp_path)

    # 处理图像输入
    if image is not None:
        img_desc = QwenVL_api(text, image)
        text = img_desc if not text else text + ", " + img_desc

    if not text:
        response = "请提供语音、文本或图片输入。"
        chatbot_state.append((text, response))
        return chatbot_state, chatbot_state

    final_response = qwen_agent(text)

    threading.Thread(target=play_tts_in_background, args=(final_response,)).start()
    chatbot_state.append((text, final_response))
    yield chatbot_state, chatbot_state
    
# 使用类似 qwen_agent.gui 的界面风格
with gr.Blocks(theme=gr.themes.Default()) as demo:
    gr.Markdown(
        """
        <div align="center" style="font-size:2.5em; font-weight:bold; color:#333;">
            🤖 MIRA：多模态智能机械臂助手
        </div>
        <div align="center" style="color:#555;">
            支持文本、语音、图片输入，体验多模态AI交互
        </div>
        """
    )
    
    with gr.Row(equal_height=False):
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(label="对话历史", height=500, bubble_full_width=False, show_copy_button=True)
            state = gr.State([])
        
        with gr.Column(scale=2, min_width=400):
            txt = gr.Textbox(
                label="输入文本",
                placeholder="请输入指令或问题...",
                lines=3,
                max_lines=6,
                show_label=True
            )
            
            gr.Markdown("#### 语音输入")
            audio = gr.Audio(type="filepath", label="上传语音文件", show_label=True)
            
            gr.Markdown("#### 图片输入")
            image = gr.Image(type="filepath", label="上传图片", height=200)

            submit_btn = gr.Button("🚀 提交", variant="primary", size="lg")

    submit_btn.click(
        fn=process_input,
        inputs=[txt, audio, image, state],
        outputs=[chatbot, state]
    )


demo.launch()
import gradio as gr
import asyncio
import sys
import wave
from utils_spe_rec import *
# from utils_llm import *
from utils_cam import *
from utils_robot import *
from utils_agent import *
from utils_vlm import *
from utils_vlm_move import *
from utils_tts import *
from utils_micro_bit import *
from start import command_cleaning
from pydub import AudioSegment

# # 初始化microbit串口连接
# ser = connect_microbit()

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

def process_input(text, audio, image, chatbot_state):
    # 初始化 history
    if chatbot_state is None:
        chatbot_state = []

    # 处理语音和图像输入
    if audio is not None:
        tmp_path = "/tmp/converted.wav"
        convert_to_wav16k1c(audio, tmp_path)
        check_wav_info(tmp_path)
        text = recognize_speech(tmp_path)
        print("语音识别结果：", text)
    if image is not None:
        img_desc = QwenVL_api(text, image)
        text = img_desc if not text else text + ", " + img_desc

    if not text:
        response = "请提供语音、文本或图片输入。"
        chatbot_state.append((text, response))
        return chatbot_state, chatbot_state

    order = agent_plan(text)
    print("智能体编排结果：", order)
    order = command_cleaning(order)
    # order = order.replace("，", ",")  # 替换中文逗号为英文逗号
    # order = order.replace("、", ",")  # 替换中文顿号为英文逗号
    # order = order.replace("；", ";")  # 替换中文分号为英文分号
    # order = order.replace("！", "!")  # 替换中文感叹号为英文感叹号
    # order = order.replace("？", "?")  # 替换中文问号为英文问号
    # order = order.replace("：", ":")  # 替换中文冒号为英文冒号
    
    try:
        agent_plan_output = eval(order)
        response = agent_plan_output['response']
        for each in agent_plan_output['function']:
            print('执行动作:', each)
            eval(each)
    except Exception as e:
        response = f"发生错误: {str(e)}"
    
    asyncio.run(text_to_speech(response))
    chatbot_state.append((text, response))  # 更新历史记录
    return chatbot_state, chatbot_state

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        <div align="center" style="font-size:2em; font-weight:bold; color:#4F8EF7;">
            🤖 智能机械臂助手
        </div>
        <div align="center" style="color:gray;">
            支持文本、语音、图片输入，体验多模态AI交互
        </div>
        """)
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="对话历史", height=400, show_copy_button=True)
            state = gr.State([])  # 使用 State 组件来保存聊天记录
            with gr.Row():
                txt = gr.Textbox(show_label=False, placeholder="请输入指令或问题", lines=2, container=True)
            submit_btn = gr.Button("🚀 提交", elem_id="submit-btn", scale=1)
        with gr.Column(scale=1):
            with gr.Group():
                gr.Markdown("#### 语音输入")
                audio = gr.Audio(type="filepath", label="", show_label=False)
            with gr.Group():
                gr.Markdown("#### 图片输入")
                image = gr.Image(type="filepath", label="", show_label=False, height=180)

    submit_btn.click(
        fn=process_input,
        inputs=[txt, audio, image, state],
        outputs=[chatbot, state]  # 更新 chatbot 和 state
    )

demo.launch()
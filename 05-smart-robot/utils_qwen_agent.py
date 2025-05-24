# utils_qwen_agent.py
import os
from datetime import datetime
import requests
from typing import Any, Dict
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool
from qwen_agent.utils.output_beautify import typewriter_print
import pprint
import urllib.parse
import json
from qwen_agent.gui import WebUI
import asyncio
from pydub import AudioSegment
from utils_spe_rec import recognize_speech
from utils_tts import text_to_speech
from utils_vlm import QwenVL_api
import gradio as gr

# 假设你已将 API Key 存放在 API_Key_utils.py 中
import API_Key_utils
from utils_vlm_move import vlm_move, say_hello
from utils_micro_bit import connect_microbit, send_data_microbit, disconnect_microbit
from utils_cam import top_view_shot
microbit_ser = connect_microbit()

# ================== 自定义工具类 ==================
        
@register_tool('vlm_detect_object')
class VlmDetectObjectTool(BaseTool):
    description = '使用通义千问 VL 模型识别图像'
    parameters = [{
        'name': 'prompt',
        'type': 'string',
        'description': '用户指令，例如“你都看到桌上有什么”',
        'example': '看看桌上有什么',
        'required': True
    }, {
        'name': 'image_path',
        'type': 'string',
        'description': '图像路径，默认为 temp/item.jpg',
        'example': 'temp/item.jpg',
        'default': 'temp/item.jpg',
        'required': False
    }]

    def call(self, params: str, **kwargs) -> str:
        top_view_shot()
        params_dict = json.loads(params)
        prompt = params_dict.get('prompt', '')
        image_path = params_dict.get('image_path', 'temp/item.jpg')

        result = QwenVL_api(prompt, image_path)
        return result

@register_tool('microbit_connect')
class MicrobitConnectTool(BaseTool):
    description = '连接 micro:bit 设备'
    parameters = []

    def call(self, params: str, **kwargs) -> str:
        global microbit_ser
        microbit_ser = connect_microbit()
        if microbit_ser:
            return "成功连接到 micro:bit！"
        else:
            return "连接 micro:bit 失败。"

@register_tool('microbit_send')
class MicrobitSendTool(BaseTool):
    description = '向 micro:bit 发送数据（例如 happy, heart, birthday 等）'
    parameters = [{
        'name': 'command',
        'type': 'string',
        'description': '要发送的命令，如 "happy", "heart", "birthday"',
        'example': "heart",
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        ITEM_MAPPING = {
            "开心": "happy",
            "伤心": "sad",
            "心脏": "heart",
            "生日": "birthday",
            "结婚": "wedding"
            }
        global microbit_ser
        command = json.loads(params)['command']
        if command in ITEM_MAPPING:
            command = ITEM_MAPPING[command]
        # if not hasattr(self, 'ser') or not self.ser or not self.ser.is_open:
        #     return "请先连接 micro:bit"

        send_data_microbit(microbit_ser, command)
        return f"已发送命令: {command}"

@register_tool('microbit_disconnect')
class MicrobitDisconnectTool(BaseTool):
    description = '断开与 micro:bit 的串口连接'
    parameters = []

    def call(self, params: str, **kwargs) -> str:
        global microbit_ser
        if microbit_ser and microbit_ser.is_open:
            disconnect_microbit(microbit_ser)
            return "已成功断开与 micro:bit 的连接"
        else:
            return "当前未连接 micro:bit，无需断开"

@register_tool('vlm_move')
class VlmMoveTool(BaseTool):
    description = '根据目标物品进行机械臂移动操作'
    parameters = [{
        'name': 'target_item',
        'type': 'string',
        'description': '要抓取的目标物品名称,如：梨(pear)，红苹果(redapple)，青苹果(greenapple)，橙子(orange)，桃子(peach)。',
        
        'example': 'peach',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        ITEM_MAPPING = {
        "梨": "pear",
        "红苹果": "redapple",
        "青苹果": "greenapple",
        "橙子": "orange",
        "桃子": "peach"
        }
        target_item = json.loads(params)['target_item']
        # 如果输入的是中文，尝试从映射表中查找对应的英文标识符
        if target_item in ITEM_MAPPING:
            target_item = ITEM_MAPPING[target_item]
        
        top_view_shot()
        result = vlm_move(target_item)
        return f"vlm_move executed with target item: {target_item}, Result: {result}"

@register_tool('say_hello')
class SayHelloTool(BaseTool):
    description = '执行机械臂的问候动作'
    parameters = []

    def call(self, params: str, **kwargs) -> str:
        say_hello()
        return "say_hello executed successfully"

@register_tool('get_current_time')
class GetCurrentTime(BaseTool):
    description = '返回当前时间'
    parameters = []

    def call(self, params: str, **kwargs) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@register_tool('get_current_weather')
class GetCurrentWeather(BaseTool):
    description = '当你想查询指定城市的天气时非常有用。'
    parameters = [{
        'name': 'location',
        'type': 'string',
        'description': '城市或县区，比如北京市、杭州市、余杭区等。',
        'example': '北京市',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        location = json.loads(params)['location']
        api_key = API_Key_utils.WEATHER_API_KEY
        url = f"https://api.seniverse.com/v3/weather/now.json?key={api_key}&location={location}&language=zh-Hans&unit=c"
        response = requests.get(url)
        data = response.json()

        weather_description = data["results"][0]["now"]["text"]
        temperature = data["results"][0]["now"]["temperature"]

        return f"{location}的天气是：{weather_description}，温度是：{temperature}°C"


@register_tool('get_location_by_gaode')
class GetLocationByGaode(BaseTool):
    description = '通过高德地图查询指定地点的经纬度。'
    parameters = [{
        'name': 'address',
        'type': 'string',
        'description': '要查询的详细地址，如“北京市天安门”',
        'example': '北京市天安门',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        address = json.loads(params)['address']
        api_key = API_Key_utils.GAODE_API_KEY
        para = {"key": api_key, "address": address}
        url = "https://restapi.amap.com/v3/geocode/geo"
        response = requests.get(url, para)
        data = response.json()

        if data.get("status") == "1" and data.get("geocodes"):
            location = data["geocodes"][0]["location"]
            return f"{address}的经纬度为：{location}"
        else:
            return f"无法获取{address}的经纬度信息。"

# ================== MCP 工具配置 ==================
sqlite_tool = {
    "name": "sqlite",
    "description": "用于与本地 SQLite 数据库进行交互的 MCP 工具。",
    "mcpServers": {
        "sqlite": {
            "command": "mcp-server-sqlite",
            "args": ["--db-path", "test.db"]
        }
    }
}

# 注册工具
global_tools = [sqlite_tool,'get_current_time', 'get_current_weather', 'get_location_by_gaode', 'vlm_move', 'say_hello','microbit_connect', 'microbit_send', 'microbit_disconnect', 'vlm_detect_object']
# 初始化 Qwen Agent
llm_cfg = {
    'model': "qwen-plus",
    'model_type': 'qwen_dashscope',
    'api_key': API_Key_utils.QWEN_KEY,
}
bot = Assistant(
    llm=llm_cfg,
    function_list=global_tools,
    system_message='你是一个多模态智能机械臂助手，名叫MIRA，你可以查询时间、天气、地理位置，对本地 SQLite 数据库进行增删改查操作，还能操作机械臂、通过串口向microbit发送信息，以及使用通义千问VL进行图像识别。',
)

# def qwen_agent(prompt: str) -> str:
#     """
#     接收 prompt，返回 Qwen Agent 的完整回复字符串，并自动维护历史上下文。

#     参数:
#         prompt (str): 用户输入的提示语。

#     返回:
#         str: Qwen Agent 的回复内容。
#     """
#     # 初始化历史记录（第一次调用时）
#     if not hasattr(qwen_agent, 'history'):
#         qwen_agent.history = []

#     # 添加用户输入到历史
#     qwen_agent.history.append({'role': 'user', 'content': prompt})

#     response_text = ''

#     # 调用 bot.run 获取回复
#     for response in bot.run(messages=qwen_agent.history):
#         response_text += response[-1]['content']

#     # 添加助手回复到历史
#     qwen_agent.history.append({'role': 'assistant', 'content': response_text})

#     return response_text

def get_full_response(messages):
    full_content = ''
    for response in bot.run(messages=messages):
        if response and isinstance(response, list):
            content = response[-1].get('content', '')
            if content:
                full_content = content  # 只保留最终结果
    return full_content


def qwen_agent(prompt: str) -> str:
    """
    接收 prompt，返回 Qwen Agent 的完整回复字符串，并自动维护历史上下文。

    参数:
        prompt (str): 用户输入的提示语。

    返回:
        str: Qwen Agent 的回复内容。
    """
    # 初始化历史记录（第一次调用时）
    if not hasattr(qwen_agent, 'history'):
        qwen_agent.history = []

    # 添加用户输入到历史
    qwen_agent.history.append({'role': 'user', 'content': prompt})

    full_content = ''

    # 获取模型回复（非流式）
    for response in bot.run(messages=qwen_agent.history):
        if response and isinstance(response, list):
            content = response[-1].get('content', '')
            if content:
                full_content = content  # 只保留最终结果

    # 添加助手回复到历史
    qwen_agent.history.append({'role': 'assistant', 'content': full_content})

    return full_content

# if __name__ == "__main__":
#     # print(qwen_agent("你好，今天上海的天气怎么样？"))  # 第一次调用
#     # print(qwen_agent("请告诉我之前询问天气的城市的经纬度"))  # 第二次调用，继续上下文
#     print(qwen_agent("给我用机械臂拿个桃子"))  # 第三次调用，继续上下文
#     # print(qwen_agent("举个例子说明一下"))   # 第三次调用，继续上下文

# ================== 测试运行 ==================
if __name__ == "__main__":
    messages = []  # 聊天历史记录

    # print("🤖 Qwen Agent 已启动！输入你的问题开始交互（输入 'exit' 退出）")
    
    # while True:
    #     user_input = input("\n用户请求: ").strip()
        
    #     if user_input.lower() in ['exit', 'quit']:
    #         print("👋 正在退出...")
    #         break
        
    #     messages.append({'role': 'user', 'content': user_input})
    #     reply = get_full_response(messages)
    #     print(f"MIRA：{reply}")
    #     messages.append({'role': 'assistant', 'content': reply})
    WebUI(bot).run()
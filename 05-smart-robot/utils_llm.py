import API_Key_utils
import requests
import json
import erniebot
import os
from openai import OpenAI

global_tools = [
    # 工具1 获取当前时刻的时间
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "当你想知道现在的时间时非常有用。",
            "parameters": {}  # 因为获取当前时间无需输入参数，因此parameters为空字典
        }
    },  
    # 工具2 获取指定城市的天气
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "当你想查询指定城市的天气时非常有用。",
            "parameters": {  
                "type": "object",
                "properties": {
                    # 查询天气时需要提供位置，因此参数设置为location
                    "location": {
                        "type": "string",
                        "description": "城市或县区，比如北京市、杭州市、余杭区等。"
                    }
                },
                "required": ["location"]
            }
        }
    },
    
    # 工具3 通过高德地图查询指定地点的经纬度
    {
        "type": "function",
        "function": {
            "name": "get_location_by_gaode",
            "description": "通过高德地图查询指定地点的经纬度。",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "要查询的详细地址，如“北京市天安门”"
                    }
                },
                "required": ["address"]
            }
        }
    }
]

def get_current_time():
    """
    获取当前时间
    """
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def get_current_weather(location):
    """
    获取指定城市的天气
    """
    # 这里使用心知天气API来获取天气信息
    api_key = API_Key_utils.WEATHER_API_KEY
    url = f"https://api.seniverse.com/v3/weather/now.json?key={api_key}&location={location}&language=zh-Hans&unit=c"
    response = requests.get(url)
    data = response.json()
    
    # if data["cod"] != 200:
    #     return f"无法获取{location}的天气信息。"
    
    weather_description = data["results"][0]["now"]["text"]
    temperature = data["results"][0]["now"]["temperature"]
    # weather_description = data["weather"][0]["description"]
    # temperature = data["main"]["temp"]
    
    return f"{location}的天气是：{weather_description}，温度是：{temperature}°C"

def get_location_by_gaode(address):
    """
    调用高德地图API查询地址的经纬度
    """
    api_key = API_Key_utils.GAODE_API_KEY  # 你的高德Key
    para = {
        "key": api_key,
        "address": address}
    url = f"https://restapi.amap.com/v3/geocode/geo"
    response = requests.get(url,para)
    data = response.json()
    if data.get("status") == "1" and data.get("geocodes"):
        location = data["geocodes"][0]["location"]  # "经度,纬度"
        return f"{address}的经纬度为：{location}"
    else:
        return f"无法获取{address}的经纬度信息。"

erniebot.api_type = 'aistudio'
erniebot.access_token = API_Key_utils.ERNIE_BOT_KEY  # 请确保这是有效的token

client = OpenAI(
    api_key=API_Key_utils.QWEN_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def wenxin_llm(message):
    model = 'ernie-3.5'
    messages = [{'role': 'user', 'content': message}]
    response = erniebot.ChatCompletion.create(
        model=model,
        messages=messages,
        top_p=0.95,
        stream=True)
    
    full_response = ""
    for chunk in response:
        delta_content = chunk.get_result()
        if delta_content:
            full_response += delta_content
    return full_response

def qwen_llm(message, tools=global_tools, model="qwen-plus"):
    """
    Qwen大模型聊天接口，支持多轮function call（MCP协议）。
    """
    messages = [{"role": "user", "content": message}]
    while True:
        kwargs = {
            "model": model,
            "messages": messages
        }
        if tools is not None:
            kwargs["tools"] = tools

        completion = client.chat.completions.create(**kwargs)
        result = completion.model_dump()
        msg = result["choices"][0]["message"]

        # 如果有tool_calls，自动调用本地函数，并以tool消息反馈
        if msg.get("tool_calls"):
            messages.append({
                "role": "assistant",
                "tool_calls": msg["tool_calls"]
            })
            for tool_call in msg["tool_calls"]:
                func_name = tool_call["function"]["name"]
                arguments = json.loads(tool_call["function"]["arguments"])
                if func_name == "get_current_weather":
                    reply = get_current_weather(**arguments)
                elif func_name == "get_current_time":
                    reply = get_current_time()
                elif func_name == "get_location_by_gaode":
                    reply = get_location_by_gaode(**arguments)
                # 你可以在这里扩展更多函数
                else:
                    reply = f"未实现的函数：{func_name}"
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": func_name,
                    "content": reply
                })
            # 继续while循环，直到模型直接回复文本
        else:
            # 没有tool_calls，直接返回文本回复
            return msg.get("content", "")

if __name__ == "__main__":
    # print(wenxin_llm("你好"))
    print(qwen_llm("帮我查一下现在的时间和北京天气"))
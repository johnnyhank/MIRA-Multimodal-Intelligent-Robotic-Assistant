import API_Key_utils
import requests
import json
import erniebot

erniebot.api_type = 'aistudio'
erniebot.access_token = API_Key_utils.ERNIE_BOT_KEY  # 请确保这是有效的token

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

if __name__ == "__main__":
    print(wenxin_llm("你好"))
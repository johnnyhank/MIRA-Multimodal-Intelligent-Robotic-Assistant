import random
import erniebot

# 初始化文心一言模型
models = erniebot.Model.list()
# print("可用模型:", models)

# 设置鉴权参数（https://aistudio.baidu.com/account/accessToken）
erniebot.api_type = 'aistudio'
erniebot.access_token = ''  # 请确保这是有效的token

def get_ernie_response(message):
    model = 'ernie-3.5'
    messages = [{'role': 'user', 'content': message}]
    response = erniebot.ChatCompletion.create(
        model=model,
        messages=messages,
        top_p=0.95,
        stream=True)
    
    full_response = ""
    print("文心一言:", end="", flush=True)
    for chunk in response:
        delta_content = chunk.get_result()
        if delta_content:
            full_response += delta_content
            print(delta_content, end="", flush=True)
    print("\n")
    return full_response

def main():
    print("文心一言命令行版 (输入'exit'退出)")
    while True:
        user_input = input("你: ")
        if user_input.lower() in ['exit', 'quit']:
            print("再见！")
            break
        if user_input.strip():
            get_ernie_response(user_input)

if __name__ == "__main__":
    main()
import API_Key_utils
import openai
from openai import OpenAI
import base64
import cv2
import numpy as np
from PIL import Image
from PIL import ImageFont, ImageDraw
import time
import utils_cam
import utils_tts
import asyncio
# 系统提示词1
SYSTEM_PROMPT_1 = '''
我现在要输入一个指令，你将我指令中要求的物体给框选出来
'''

def QwenVL_api(PROMPT='给我一个苹果', img_path='temp/item.jpg'):
    '''
    通义千问VL视觉语言多模态大模型API，模型列表请见：https://help.aliyun.com/zh/model-studio/getting-started/models
    '''

    client = OpenAI(
        api_key=API_Key_utils.QWEN_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"

    )
    print("识别中...")
    # 编码为base64数据
    with open(img_path, 'rb') as image_file:
        image = 'data:image/jpeg;base64,' + base64.b64encode(image_file.read()).decode('utf-8')
        utils_cam.top_view_shot()
        # 向大模型发起请求
        completion = client.chat.completions.create(
            model="qwen-vl-max-latest",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": PROMPT
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image
                            }
                        }
                    ]
                },
            ]
        )


    # 解析大模型返回结果

    result = completion.choices[0].message.content.strip()
    print(result)
    # asyncio.run(utils_tts.text_to_speech(result))
    return result


def post_processing_viz(result, img_path, check=False):
    '''
    视觉大模型输出结果后处理和可视化
    check：是否需要人工看屏幕确认可视化成功，按键继续或退出
    '''

    # 后处理
    img_bgr = cv2.imread(img_path)

    # 缩放因子
    FACTOR = 999
    # 起点物体名称
    START_NAME = result['start']

    # 起点，左上角像素坐标
    START_X_MIN = int(result['start_xyxy'][0][0] )
    START_Y_MIN = int(result['start_xyxy'][0][1] )
    # 起点，右下角像素坐标
    START_X_MAX = int(result['start_xyxy'][1][0] )
    START_Y_MAX = int(result['start_xyxy'][1][1] )
    # 起点，中心点像素坐标
    START_X_CENTER = int((START_X_MIN + START_X_MAX) / 2)
    START_Y_CENTER = int((START_Y_MIN + START_Y_MAX) / 2)

    # 可视化
    # 画起点物体框
    img_bgr = cv2.rectangle(img_bgr, (START_X_MIN, START_Y_MIN), (START_X_MAX, START_Y_MAX), [0, 0, 255], thickness=3)
    # 画起点中心点
    img_bgr = cv2.circle(img_bgr, [START_X_CENTER, START_Y_CENTER], 6, [0, 0, 255], thickness=-1)

    # 保存可视化效果图
    cv2.imwrite('temp/vl_now_viz.jpg', img_bgr)

    formatted_time = time.strftime("%Y%m%d%H%M", time.localtime())
    cv2.imwrite('temp/{}.jpg'.format(formatted_time), img_bgr)

    # 在屏幕上展示可视化效果图
    cv2.imshow('zihao_vlm', img_bgr)

    if check:
        print('请确认可视化成功，按c键继续，按q键退出')
        while (True):
            key = cv2.waitKey(10) & 0xFF
            if key == ord('c'):  # 按c键继续
                break
            if key == ord('q'):  # 按q键退出
                # exit()
                cv2.destroyAllWindows()  # 关闭所有opencv窗口
                raise NameError('按q退出')
    else:
        if cv2.waitKey(1) & 0xFF == None:
            pass

    return START_X_CENTER, START_Y_CENTER

if __name__ == '__main__':
    result = QwenVL_api("你都看到了什么？",True)
    # result = QwenVL_api("给我一个苹果",False)
    # post_processing_viz(result, "temp/item.jpg",True)
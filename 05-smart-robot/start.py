import sys
# 导入常用函数
from utils_spe_rec import *  # 录音+语音识别
from utils_llm import *
from utils_cam import *  # 摄像头
from utils_robot import *  # 连接机械臂,机械臂运动
from utils_agent import *  # 智能体Agent编排
from utils_vlm import * #多模态识别
from utils_vlm_move import *  # 多模态大模型识别图像，吸泵吸取并移动物体
from utils_tts import * # 导入语言合成模块

def command_cleaning(command):
    prefix = "```json"
    suffix = "```"
    if command.startswith(prefix) and command.endswith(suffix):
        command = command[len(prefix):].rstrip(suffix)
    return command

def agent_play():
    '''
    主函数，语音控制机械臂智能体编排动作
    '''
    asyncio.run(text_to_speech("你好，这是你的机械臂助手。"))
    robot=initialize_robot()
    go_initialize_robot_point(robot)
    
    go_flag = True
    while go_flag:
            # 输入指令
        start_record_ok = input('是否开启录音，输入0开始录音，按k打字输入\n')
        if str.isnumeric(start_record_ok):
            # DURATION = int(start_record_ok)
            record_auto()  # 录音
            order = recognize_speech()  # 语音识别
        elif start_record_ok == 'k':
            order = input('请输入指令')
        elif start_record_ok == 'q':
            sys.exit(0)
        else:
            print("重新输入指令")
            continue
            
        if not order :
            print("还没想好说什么吗？没关系,再来一次吧")
            continue

        # 编排动作
        order = agent_plan(order)

        #指令清洗
        order = command_cleaning(order)
        #转换为python字典
        agent_plan_output = eval(order)
        #提取llm答复
        response = agent_plan_output['response']
        print(agent_plan_output)
        print(response)
        #语音回答
        for each in agent_plan_output['function']:
            print('开始执行动作',each)
            eval(each)

# agent_play()
if __name__ == '__main__':
    agent_play()


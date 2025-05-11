from utils_robot import *
import numpy as np
import time
import sys
import utils_onnx_yolo
import threading
from threading import main_thread
import cv2

relation_matrix = np.array([[-2.80316285e-02,6.65940636e-01],
 [-4.71498516e-01,4.82531370e-02],
 [ 1.89347486e+02,3.10735328e+02]]
)
def say_hello():
    robot = initialize_robot()
    
    go_initialize_robot_point(robot)

    joint_pos = [0,-0.3,0,0,0.3,0]
    robot.joint_move(joint_pos,INCR,True,5)
    
    joint_pos = [0,0,0,3,0,3]
    robot.joint_move(joint_pos,INCR,True,5)

    joint_pos = [0,0,0,1,0,-3]
    robot.joint_move(joint_pos,INCR,True,5)

    joint_pos = [0,0,0,-2,0,3]
    robot.joint_move(joint_pos,INCR,True,5)

    joint_pos = [0,0,0,1,0,-3]
    robot.joint_move(joint_pos,INCR,True,5)
    
    joint_pos = [0,0,0,-1,0,0]
    robot.joint_move(joint_pos,INCR,True,3)
    time.sleep(0.3)

    go_initialize_robot_point(robot)

def vlm_move(target_item):
    result = utils_onnx_yolo.onnx_yolo(target_item)
    # result = utils_vlm.QwenVL_api(PROMPT,False)
    print(result)
    
    if result is None or len(result)==0:
        print("没有物体中心点无法抓取")
        return None    
    
    robot = initialize_robot()
    
    #移动到抓取区起点
    go_initialize_robot_point(robot)

    #重置夹爪
    robot.set_digital_output(IO_TOOL,0,0)
    robot.set_digital_output(IO_TOOL,1,0)
    
    camera_point = np.array(result)

    # 将相机坐标系下的点与关系矩阵相乘，得到机械臂坐标系下的齐次坐标向量
    robot_point_homogeneous = np.dot(camera_point, relation_matrix)

    go_initialize_robot_pointby_gripper(robot)

    #目标点正上方
    target_point_top = [robot_point_homogeneous[0], robot_point_homogeneous[1], -150, 0, 0, -3.14/2]
    print(f"target_point_top:{target_point_top}")

    # 移动到目标点正上方
    joint_position = robot.get_joint_position()
    print(joint_position,target_point_top)
    ret = robot.kine_inverse(joint_position[1], target_point_top)
    print(ret)
    
    if ret[0] != 0:
        print("解算错误，回到起点")
        joint_pos = [0.11519592327644017, 0.46927762596946804, 0.7667213095155779, -0.006722023945374499, 1.9057808068748003, 3.1207601924960273]
        robot.joint_move(joint_pos, ABS, False, 1)
        return
    
    joint_pos = ret[1]
    robot.joint_move(joint_pos, ABS, False, 1)

    # 移动到目标点
    target_point = [robot_point_homogeneous[0], robot_point_homogeneous[1], -80, 0, 0, -3.14/2]
    joint_position = robot.get_joint_position()
    ret = robot.kine_inverse(joint_position[1], target_point)
    joint_pos = ret[1]
    robot.joint_move(joint_pos, ABS, True, 1)
    
    # 开启夹爪抓物体
    robot.set_digital_output(IO_TOOL,0,1)
    robot.set_digital_output(IO_TOOL,1,0)
    time.sleep(1)

    # 移动回正上方
    joint_position = robot.get_joint_position()
    ret = robot.kine_inverse(joint_position[1], target_point_top)
    joint_pos = ret[1]
    robot.joint_move(joint_pos, ABS, False, 1)

    go_initialize_robot_pointby_gripper(robot)
    go_initialize_robot_point(robot)
    
    #松开夹爪
    robot.set_digital_output(IO_TOOL,0,0)
    robot.set_digital_output(IO_TOOL,1,1)
    robot.logout()

if __name__ == "__main__":
    # say_hello()
    vlm_move("redapple")
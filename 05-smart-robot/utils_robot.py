# -*- coding: UTF-8 -*-
import jkrc
import time

IO_TOOL = 1
ABS = 0
INCR = 1
initial_path_point = [-285.657937, 235.079726, -185.267725, 0.009283161786908889, 0.03307297647016222, -0.12371577696166221] #[-210.733, 6, 240, -3.14, 0, -3.14]
initial_path_point_by_gripper = [54.210675, 487.171219, -185.208566, -0.023837148011760005, 0.005365351468617778, -1.7534092587630845] # [-48.746,205.106,285,-3.14,0,-3.14]
# 机械臂的初始姿态
joint_pos = [0, 0, 1.57, 0, 1.57, 0]
# 初始化机械臂
def initialize_robot():
    ret=robot = jkrc.RC("10.5.5.100")
    ret = robot.login()
    print(f"ret{ret}")
    robot.power_on()
    robot.enable_robot()
    return robot


#移动到初始起点
def go_initialize_robot_point(robot):
    print("初始起点")
    joint_position = robot.get_joint_position()
    # print(joint_position)
    ret = robot.kine_inverse(joint_position[1],initial_path_point)
    #print(ret)   
    joint_pos = ret[1]
    robot.joint_move(joint_pos,ABS,True,10)


#移动到抓取起点位置
def go_initialize_robot_pointby_gripper(robot):
    print("抓取起点")
    joint_position = robot.get_joint_position()
    ret = robot.kine_inverse(joint_position[1],initial_path_point_by_gripper)
    #print(ret)
    joint_pos = ret[1]
    robot.joint_move(joint_pos,ABS,True,10)


def hello():
    go_initialize_robot_point(robot)

    
if __name__ == "__main__":
    print("初始化")
    robot=initialize_robot()
    go_initialize_robot_point(robot)
    go_initialize_robot_pointby_gripper(robot)
# JAKA Minicobo Toolkit

## 使用方式

该文件夹内已经包含JAKA SDK v2.2.7库（`jkrc.so`，`libjakaAPI.so`），因此不需要额外安装。
使用时请不要随意移动上述文件的位置。

操作方式请参考：https://notes.sjtu.edu.cn/s/qtKNPFdBT

## 代码简介

- 01.login.py：测试能否访问机械臂，请确保IP地址设置为`10.5.5.100`
- 02.get_position.py：获取机械臂各关节点的位置信息
- 03.joint_move.py：机械臂将移动至垂直状态，并按一定间隔时间摆动
- 04.get_tcppos.py：获取Tcppos信息
- 05.digital_output.py：控制机械臂末端的吸盘工作
- 06.move_and_fetch.py：简单的结合机械臂运动和吸盘协同工作的demo
- 09.test_reconnect_robot.py：重新连接和使能机械臂
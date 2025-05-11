import jkrc
import time
IO_CABINET = 0
IO_TOOL = 1
ABS = 0
INCR = 1

robot = jkrc.RC("10.5.5.100")
robot.login()
robot.power_on()
robot.enable_robot()
#索引index = 1为控制数字输出DO1，当其value被设置为1时为打开夹抓，0时关闭
#注查询状态时索引是从1开始的index = 0 时查看DO1的状态

# print(robot.get_digital_output(IO_TOOL,0))

ret = robot.set_digital_output(IO_TOOL, 0, 0)
ret += robot.set_digital_output(IO_TOOL, 1, 0)
# ret2 = robot.get_digital_output(IO_TOOL,0)
# print(f"{ret},{ret2}")
# print(ret)
# time.sleep(5)
# ret=robot.set_digital_output(IO_TOOL,0,1)
print(ret)



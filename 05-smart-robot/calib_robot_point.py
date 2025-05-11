import sys
import os
import time
sys.path.append(os.path.abspath("../"))
import jkrc 
  
robot = jkrc.RC("10.5.5.100")  
robot.login()
print("Use [Free] to move robot, Use [Point] to write msg")
while True:
  ret = robot.get_robot_status()
  if ret[0] == 0:
    if ret[1][24][1] == 1:
      ret1 = robot.get_tcp_position()
      if not ret1[0]:
        print(f"[{ret1[1][0]}, {ret1[1][1]}],")
        time.sleep(1)
      else:
        print(f"Error!")
        break
  else:  
    print("Errcode:",ret[0])
    break
robot.logout()  
import jkrc
import math
import time
IO_CABINET = 0
IO_TOOL = 1
IO_EXTEND = 2

def main():
    jstep_pos = [0.43847400652370466, 0.009023701298661084, 1.6924045858885544, 0.030954112415820228, 1.4631034032944645, -0.0002488839513343914]
    jstep_neg = [-0.6413285640281748, 0.011576419862627989, 1.6923925431167153, -0.015484735656618892, 1.4629836737077777, -0.0002488839513343914]

    rc = jkrc.RC("10.5.5.100")
    print(f"Login: {rc.login()}")
    print(f"Power on: {rc.power_on()}")
    print(f"Enable robot: {rc.enable_robot()}")

    print(f'Joint_move: {jstep_pos}, {rc.joint_move(jstep_pos, 0, True, 0.25)}')
    rc.set_digital_output(IO_TOOL, 1, 1)
    rc.set_digital_output(IO_TOOL, 2, 0)
    time.sleep(1.5)
    print(f'joint_move: {jstep_neg}, {rc.joint_move(jstep_neg, 0, True, 0.25)}')
    rc.set_digital_output(IO_TOOL, 1, 0)
    rc.set_digital_output(IO_TOOL, 2, 1)

if __name__ == '__main__':
    main()


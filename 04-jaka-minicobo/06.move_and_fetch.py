import jkrc
import math
import time
IO_CABINET = 0
IO_TOOL = 1
IO_EXTEND = 2

def main():
    jstep_pos = [-0.3834436965580337, 0.4008117504620091, 1.0588008330352328, 0.009995969461400425, 1.6833895497783686, 0.0019735816196739153]
    jstep_neg = [0.1608797876969606, 0.48733785253865075, 1.0377205818506328, 0.0369844434055274, 1.6008781629642863, 0.00198556584433827]

    rc = jkrc.RC("10.5.5.100")
    print(f"Login: {rc.login()}")
    print(f"Power on: {rc.power_on()}")
    print(f"Enable robot: {rc.enable_robot()}")

    print(f'Joint_move: {jstep_pos}, {rc.joint_move(jstep_pos, 0, True, 0.25)}')
    rc.set_digital_output(IO_TOOL, 0, 1)
    rc.set_digital_output(IO_TOOL, 1, 0)
    time.sleep(1.5)
    print(f'joint_move: {jstep_neg}, {rc.joint_move(jstep_neg, 0, True, 0.25)}')
    rc.set_digital_output(IO_TOOL, 0, 0)
    rc.set_digital_output(IO_TOOL, 1, 1)

if __name__ == '__main__':
    main()


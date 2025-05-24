import jkrc
import math
import time

def main():
    jstep_pos = [0, 0, 0, 0, 15 / 180.0 * math.pi, 0]
    jstep_neg = [0, 0, 0, 0, -15 / 180.0 * math.pi, 0]

    rc = jkrc.RC("10.5.5.100")
    print(f"Login: {rc.login()}")
    print(f"Power on: {rc.power_on()}")
    print(f"Enable robot: {rc.enable_robot()}")

    while True:
        print(f'Joint_move: {jstep_pos}, {rc.joint_move(jstep_pos, 0, True, 0.1)}')
        time.sleep(3)
        print(f'joint_move: {jstep_neg}, {rc.joint_move(jstep_neg, 0, True, 0.1)}')
        time.sleep(3)


if __name__ == '__main__':
    main()

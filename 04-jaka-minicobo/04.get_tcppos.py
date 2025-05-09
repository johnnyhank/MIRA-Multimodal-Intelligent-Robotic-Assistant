import jkrc
import math
import time

def main():
    rc = jkrc.RC("10.5.5.100")
    print(f"Login: {rc.login()}")
    print(f"Power on: {rc.power_on()}")
    print(f"Enable robot: {rc.enable_robot()}")

    while True:
        ret = rc.get_tcp_position()
        if not ret[0]:
            print(f"Tcp pos: {ret[1]}")
        else:
            print(f"Error!")
            
        time.sleep(1)

if __name__ == '__main__':
    main()

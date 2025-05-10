import jkrc
import math
import time

IO_CABINET = 0
IO_TOOL = 1
IO_EXTEND = 2

def main():
    rc = jkrc.RC("10.5.5.100")
    print(f"Login: {rc.login()}")
    print(f"Power on: {rc.power_on()}")
    print(f"Enable robot: {rc.enable_robot()}")
    
    cnt = 0

    while cnt < 5:
        rc.set_digital_output(IO_TOOL, 0, 1)
        rc.set_digital_output(IO_TOOL, 1, 0)
        time.sleep(0.1)
        ret1 = rc.get_digital_output(0, 0)
        ret2 = rc.get_digital_output(0, 1)
        if ret1[0] == 0 and ret2[0] == 0:
            print(f"Open #{cnt}")
        else:
            print(f"Errcode: {ret1[0]}, {ret2[0]}")
        time.sleep(2)


        rc.set_digital_output(IO_TOOL, 0, 0)
        rc.set_digital_output(IO_TOOL, 1, 1)
        time.sleep(0.1)
        ret1 = rc.get_digital_output(0, 0)
        ret2 = rc.get_digital_output(0, 1)
        if ret1[0] == 0 and ret2[0] == 0:
            print(f"Close #{cnt}")
        else:
            print(f"Errcode: {ret1[0]}, {ret2[0]}")
        time.sleep(2)
        
        cnt += 1
        
    rc.logout()        

if __name__ == '__main__':
    main()

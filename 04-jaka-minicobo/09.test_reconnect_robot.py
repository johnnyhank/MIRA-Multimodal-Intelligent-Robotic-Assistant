import jkrc
import math
import time

def main():
    rc = jkrc.RC("10.5.5.100")
 
    print('==========1st login==========')
    print('login: {}'.format(rc.login()))
    print('power_on: {}'.format(rc.power_on()))
    print('enable_robot: {}'.format(rc.enable_robot()))
    time.sleep(1)

    print('==========1st logout==========')
    print('disable_robot: {}'.format(rc.disable_robot()))
    print('power_off: {}'.format(rc.power_off()))
    print('logout: {}'.format(rc.logout()))
    time.sleep(2)

    print('==========2nd login==========')
    print('login: {}'.format(rc.login()))
    print('power_on: {}'.format(rc.power_on()))
    print('enable_robot: {}'.format(rc.enable_robot()))

if __name__ == '__main__':  
    main()
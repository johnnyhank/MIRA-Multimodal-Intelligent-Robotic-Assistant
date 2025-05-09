import jkrc
import time

def main():
    rc = jkrc.RC("10.5.5.100")
    rc.login()

    cnt = 0
    while cnt < 10:
        ret = rc.get_joint_position()

        if ret[0] == 0:
            print(f"Joint position #{cnt+1}: {ret[1]}")
        else:
            print(f"Errcode: {ret[0]}")
        
        time.sleep(1)
        cnt += 1

    rc.logout()

if __name__ == '__main__':
    main()
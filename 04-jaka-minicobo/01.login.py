import jkrc

def main():
    rc = jkrc.RC("10.5.5.100")
    print(f"Login: {rc.login()}")
    print(f"Logout: {rc.logout()}")

if __name__ == '__main__':
    main()
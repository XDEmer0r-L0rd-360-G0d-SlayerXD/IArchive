from winreg import HKEY_CURRENT_USER, OpenKey, QueryValue


def get_browser():
    cmd = str()
    with OpenKey(HKEY_CURRENT_USER, r"Software\Classes\http\shell\open\command") as key:
        cmd = QueryValue(key, None)
    if cmd.lower().__contains__('firefox'):
        return 'firefox'
    elif cmd.lower().__contains__('chrome'):
        return 'chrome'
    else:
        return 'other'


def main():
    browser = get_browser()
    print(browser)


if __name__ == '__main__':
    main()

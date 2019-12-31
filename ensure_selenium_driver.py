from winreg import HKEY_CURRENT_USER, OpenKey, QueryValue
import os
import requests
import zipfile


def check_for_driver(browser):
    done = False
    if browser == 'firefox':
        done = os.path.isfile('geckodriver.exe')
    else:
        done = os.path.isfile('chromedriver.exe')
    if not done:
        dl_link = ''
        if browser == 'firefox':
            dl_link = 'https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-win64.zip'
        else:
            dl_link = 'https://chromedriver.storage.googleapis.com/80.0.3987.16/chromedriver_win32.zip'
        with open('driver.zip', 'wb') as f:
            f.write(requests.get(dl_link).content)
        with zipfile.ZipFile('driver.zip', 'r') as zip_ref:
            zip_ref.extractall('.')
        os.remove('driver.zip')
        print('Downloaded driver')
    else:
        print('Already have driver')


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
    check_for_driver('firefox')
    exit()
    browser = get_browser()
    if browser == 'other':
        input('Must set default browser to firefox or chrome.>')
        exit()
    check_for_driver(browser)

    input(browser)


if __name__ == '__main__':
    main()

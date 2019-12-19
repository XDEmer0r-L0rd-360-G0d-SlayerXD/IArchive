from tkinter import *
import requests
import os
from lxml import html
from pprint import pprint
from selenium import webdriver
import time


class SetupContainer:
    def __init__(self):

        self.login_cookie = ''

        def on_entry_click(event):
            if self.user_box.get() == 'Enter Username':
                self.user_box.delete(0, "end")  # delete all the text in the self.user_box
                self.user_box.insert(0, '')  # Insert blank for user input
                self.user_box.config(fg='black')

        self.root = Tk()
        self.grab_posts_frame = Frame(self.root)
        self.grab_smiles_frame = Frame(self.root)
        self.var = IntVar()
        self.want_posts = IntVar()
        self.want_repubs = IntVar()
        self.want_smiled = IntVar()
        self.folder_for_posts = IntVar()
        self.post_per_folder = IntVar()
        self.fast_mode = IntVar()
        self.user_box = Entry(self.root)
        self.user_box.insert(0, 'Enter Username')
        self.user_box.bind('<FocusIn>', on_entry_click)
        post_check = Checkbutton(self.grab_posts_frame, text='Grab posts', variable=self.want_posts, command=self.post_options)
        but = Button(self.root, text='Start (double check options before)', command=self.done)
        self.repub_check = Checkbutton(self.grab_posts_frame, text='Exclude Repubs', variable=self.want_repubs)
        smile_check = Checkbutton(self.grab_smiles_frame, text='Grab Smiled Posts', variable=self.want_smiled, command=self.check_auth_frame)
        self.auth_label = Label(self.grab_smiles_frame, text='Authentication Unconfirmed')
        self.auth_button = Button(self.grab_smiles_frame, text='Test Authentication', command=self.auth_check)
        save_post_check = Checkbutton(self.root, text='Save all posts in folder', variable=self.folder_for_posts)
        save_posts_data_check = Checkbutton(self.root, text='Save additional data per post', variable=self.post_per_folder)
        fast_mode_check = Checkbutton(self.root, text='Fast Update Mode (may miss some posts)', variable=self.fast_mode)
        self.user_box.pack()
        self.grab_posts_frame.pack()
        post_check.pack()
        self.grab_smiles_frame.pack()
        save_post_check.pack()
        save_posts_data_check.pack()
        smile_check.pack()
        fast_mode_check.pack()
        but.pack()

        self.root.mainloop()

    def cb(self, event=None):
        print("variable is", self.var.get())

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
        options = webdriver.FirefoxOptions()
        # options.add_argument('-headless')
        driver = webdriver.Firefox(options=options)
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
            given = input('check if human is needed(y to click again)>')
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
        return self.user_box.get(), self.want_posts.get(), self.want_repubs.get(), self.want_smiled.get(), self.login_cookie, self.folder_for_posts.get(), self.post_per_folder.get(), self.fast_mode.get()

    def done(self):
        self.root.quit()
    
    def destroy(self):
        self.root.destroy()


def pre_setup():
    box = SetupContainer()
    try:
        values = box.grab()
    except Exception:
        input('Program Terminated')
        exit()
    box.destroy()
    if values[0].__contains__(' ') or values[0] == '' or (values[1] == 0 and values[3] == 0) or (values[5] == 0 and values[6] == 0):
        input('Invalid Setup')
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


def grab_post_urls(start_url, exclude_reposts, token, short_scan=0, already_saved=set()):
    cookie_form = {'UID': token}
    next_url = start_url
    bank = set()
    count = 0
    overlaps = 0
    while True:
        if count == 20:
            break
        count += 1
        response = requests.get(next_url, cookies=cookie_form)
        tree = html.fromstring(response.content)
        grab = tree.xpath('/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/div/div[2]/ul/li[*]/div/div/a/@href')
        cleaned_grab = []
        for num_a, a in enumerate(grab):
            exclude = False
            if exclude_reposts == 1:
                path = f'/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/div/div[2]/ul/li[{num_a + 1}]/div/div/a/svg/@class="Icon grid__icon grid__icon_bottom"'
                exclude = tree.xpath(path)
                print('exclude', exclude)
            if not exclude:
                cur_link = a.split('?')[0]
                if cur_link not in already_saved:
                    cleaned_grab.append(cur_link)
                else:
                    if short_scan == 1:
                        overlaps += 1
                        if overlaps == 5:
                            return bank
        bank.update(cleaned_grab)
        print(bank)
        try:
            next_url = start_url + ('/timeline/' if token == '' else '/') + tree.xpath('/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/div/div[2]/ul/li[1]/@data-next')[0]
            print(next_url)
        except IndexError:
            break
    print('done')
    return bank


def grab_archived(user):
    os.chdir(user)
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
    return post_data_links, post_dump_links, smile_data_links, smile_dump_links


def save_post(url):
    content_type = url.split('/')[1]
    src_link = ''
    response = requests.get('https://ifunny.co' + url)
    print('content', content_type)
    tree = html.fromstring(response.content)
    if content_type == 'picture':
        path = '/html/head/meta[24]/@content'
        grabbed_url = tree.xpath(path)
        name = grabbed_url[0].split('/')[-1]
        prep = 'https://imageproxy.ifunny.co/crop:x-20/images/' + name
    else:
        return

    downloaded = requests.get(prep)
    with open(name, 'wb') as f:
        f.write(downloaded.content)
    return


def main():
    # order: pre_setup(), prep_user_files, grab_archived
    me = 'https://ifunny.co/user/namisboss'
    blast = 'https://ifunny.co/user/Gone_With_The_Blastwave'
    smiles = 'https://ifunny.co/account/smiles'
    my_token = 'c00b9bdc7d3fc37bc313b98c3396ac2dc91a78d93f80a1d6f486532c3e29cd2d'
    save_post('/picture/HA3awnND7')
    exit()
    all_href = grab_post_urls(me, 1, '')
    user, want_posts, exclude_repubs, want_smiles, token, want_dump, want_data, fast_mode = pre_setup()
    prep_user_files(user, want_posts, want_smiles, want_dump, want_data)
    print('teast')


if __name__ == '__main__':
    main()

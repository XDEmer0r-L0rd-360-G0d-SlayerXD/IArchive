from tkinter import *
import requests
import os
import selenium


class SetupContainer:
    def __init__(self):
        def on_entry_click(event):
            """function that gets called whenever self.user_box is clicked"""
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
        self.user_box = Entry(self.root)
        self.user_box.insert(0, 'Enter Username')
        self.user_box.bind('<FocusIn>', on_entry_click)
        post_check = Checkbutton(self.grab_posts_frame, text='Grab posts', variable=self.want_posts, command=self.post_options)
        but = Button(self.root, text='Start (double check options before)', command=self.done)
        self.repub_check = Checkbutton(self.grab_posts_frame, text='Exclude Repubs', variable=self.want_repubs)
        smile_check = Checkbutton(self.grab_smiles_frame, text='Grab Smiled Posts', variable=self.want_smiled, command=self.check_auth_frame)
        self.auth_label = Label(self.grab_smiles_frame, text='Authentication Unconfirmed')
        self.auth_button = Button(self.grab_smiles_frame, text='Test Authentication', command=self.auth_check)
        # c is for example, will be removed
        c = Checkbutton(self.root, text="Enable Tab", variable=self.var, command=self.cb)
        self.user_box.pack()
        self.grab_posts_frame.pack()
        post_check.pack()
        self.grab_smiles_frame.pack()
        smile_check.pack()
        c.pack()
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
        try:
            with open(f'{self.user_box}_key.txt') as f:
                login_cookie = f.read()
        except FileNotFoundError:

            self.auth_label.config(text='checked')

    def done(self):
        # function gets called twice, by button and by box.done() outside
        print('want', self.want_repubs.get())
        self.root.quit()
        return 2


def pre_setup():
    box = SetupContainer()
    values = box.done()
    print('val:', values)
    return 0


def main():
    values = pre_setup()
    print('teast')


if __name__ == '__main__':
    main()

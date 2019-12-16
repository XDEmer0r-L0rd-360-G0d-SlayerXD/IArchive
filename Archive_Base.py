from tkinter import *


class SetupContainer:
    def __init__(self):
        def on_entry_click(event):
            """function that gets called whenever user_box is clicked"""
            if user_box.get() == 'Enter Username':
                user_box.delete(0, "end")  # delete all the text in the user_box
                user_box.insert(0, '')  # Insert blank for user input
                user_box.config(fg='black')

        self.root = Tk()
        self.grab_posts_frame = Frame(self.root)
        self.grab_smiles_frame = Frame(self.root)
        self.var = IntVar()
        self.want_posts = IntVar()
        self.want_repubs = IntVar()
        user_box = Entry(self.root)
        user_box.insert(0, 'Enter Username')
        user_box.bind('<FocusIn>', on_entry_click)
        post_check = Checkbutton(self.grab_posts_frame, text='Grab posts', variable=self.want_posts, command=self.post_options)
        c = Checkbutton(self.root, text="Enable Tab", variable=self.var, command=self.cb)
        but = Button(self.root, text='Start (double check options before)', command=self.done)
        self.repub_check = Checkbutton(self.grab_posts_frame, text='Exclude Repubs', variable=self.want_repubs)
        user_box.pack()
        self.grab_posts_frame.pack()
        post_check.pack()
        self.grab_smiles_frame.pack()
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

    def done(self):
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

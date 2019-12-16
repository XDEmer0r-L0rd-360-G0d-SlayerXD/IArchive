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
        self.var = IntVar()
        user_box = Entry(self.root)
        user_box.insert(0, 'Enter Username')
        user_box.bind('<FocusIn>', on_entry_click)
        user_box.pack()
        c = Checkbutton(self.root, text="Enable Tab", variable=self.var, command=self.cb)
        c.pack()
        but = Button(self.root, text='Start (double check options before)', command=self.done)
        but.pack()
        self.root.mainloop()

    def cb(self, event=None):
        print("variable is", self.var.get())

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

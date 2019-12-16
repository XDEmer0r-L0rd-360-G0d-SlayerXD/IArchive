from tkinter import *


class SetupContainer:
    def __init__(self):
        self.root = Tk()
        self.var = IntVar()
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

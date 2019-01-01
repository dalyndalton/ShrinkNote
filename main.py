#!/usr/bin/env python

import tkinter as tk
from backend import Notes, open_image
from PIL import Image, ImageTk


class NoteShrinkGUI(tk.Frame):
    def __init__(self, master=None):
        # Main Window Options
        tk.Frame.__init__(self, master)
        self.master.title("Note Shrinker")
        self.grid()
        self.master.iconbitmap("assets/notes_icon.ico")

        # Variables
        self.bg_rbg = tk.StringVar()
        self.v_thresh = tk.IntVar()
        self.s_thresh = tk.IntVar()


def main():
    NoteShrinkGUI().mainloop()


main()

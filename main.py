#!/usr/bin/env python

import os
import tkinter as tk
from tkinter import colorchooser as cc
from tkinter import filedialog as fd

from PIL import Image, ImageTk

# Constants
STICKY = tk.N + tk.E + tk.S + tk.W


class NoteShrinkGUI(tk.Frame):
    def __init__(self, master=None):
        # Main Window Options
        tk.Frame.__init__(self, master)
        self.master.title("Note Shrinker")
        self.grid()
        self.master.iconbitmap("assets/notes_icon.ico")

        # Assets
        temp = Image.open('assets/add_file.png')
        temp = temp.resize((32, 32))
        self.img_add_file = ImageTk.PhotoImage(temp)

        # Variables
        self.bg_color = None
        self.bg_color_set_state = tk.IntVar()

        self.file_path = tk.StringVar()
        self.v_thresh = tk.IntVar()
        self.v_thresh.set(25)
        self.s_thresh = tk.IntVar()
        self.s_thresh.set(15)

        # Validation
        vcmd = self.register(self._validate())
        # Choose File
        self.choose_file_frame = tk.LabelFrame(self, text="Choose a file")
        self.choose_file_frame.grid(row=0, column=0, sticky=STICKY)
        self.choose_file_entry = tk.Entry(self.choose_file_frame, textvariable=self.file_path, width=40)
        self.choose_file_entry.grid(row=0, column=0, sticky=tk.W + tk.E)
        self.choose_file_button = tk.Button(self.choose_file_frame, image=self.img_add_file,
                                            command=self._get_file_name)
        self.choose_file_button.grid(row=0, column=1, sticky=STICKY)

        # Set BG Color
        self.bg_color_set = tk.Checkbutton(self, text="Custom Color", command=self._set_bg_color,
                                           variable=self.bg_color_set_state)
        self.bg_color_set.grid(row=1, column=0, sticky=tk.W)

        # Saturation Threshold Slider
        self.s_frame = tk.Frame(self)
        self.s_frame.grid(row=2, column=0, sticky=STICKY)
        self.s_thresh_slider = tk.Scale(self.s_frame, variable=self.s_thresh, from_=10, to=30, orient=tk.HORIZONTAL,
                                        label='Saturation Threshold', length=250)
        self.s_thresh_slider.grid(row=0, column=0)

        self.v_frame = tk.Frame(self)
        self.v_frame.grid(row=3, column=0, sticky=STICKY)
        self.v_thresh_slider = tk.Scale(self.v_frame, variable=self.v_thresh, from_=15, to=40, orient=tk.HORIZONTAL,
                                        label="Value Threshold", length=250)
        self.v_thresh_slider.grid(row=0, column=0)

    def _get_file_name(self):
        file_path = fd.askopenfilename(title="Select Image", initialdir=os.path.expanduser('~') + "/Documents",
                                       filetypes=(("Images", ".jpeg"), ("Images", ".jpg"), ("Images", ".png")))
        self.file_path.set(file_path)

    def _set_bg_color(self):
        if self.bg_color_set_state.get() == 1:
            self.bg_color, _ = cc.askcolor()
        else:
            self.bg_color = None

    def _validate(self, action, index, value_if_allowed,
                  prior_value, text, validation_type, trigger_type, widget_name):
        if text in '0123456789':
            try:
                float(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False


def main():
    NoteShrinkGUI().mainloop()


main()

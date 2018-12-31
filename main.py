#!/usr/bin/env python
import tkinter as tk
from backend import *


class NoteShrinkGUI(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master.title("Note Shrinker")
        self.grid()
        

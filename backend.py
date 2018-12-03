import tkinter as tk
from tkinter import filedialog as fd

import numpy as np
from PIL import Image


def open_image():
    """Function used to test filetype and open image, converts file to RBG"""
    tk.Tk().withdraw()
    while True:
        file = fd.askopenfilename(title="Select Image", initialdir="",
                                  filetypes=(("Images", ".jpeg"), ("Images", ".jpg"), ("Images", ".png")))
        if file != "":
            try:
                img = Image.open(file)
            except IOError:
                print("ERROR: INVALID FILE TYPE")
            break
        else:
            print("ERROR: NO FILE SELECTED")
    if img.mode != 'RGB':
        img = img.convert('RGB')

    img = np.array(img)
    return img


def bitdepth(array, bits=4):
    """Compresses an image's color palette by zeroing out significant bits"""
    shift = 8 - bits
    half = (1 << shift) >> 1
    return ((array.astype(int) >> shift) << shift) + half


def sample(array, percent=.10):
    """Saples the percent of the image specified"""
    array = array.reshape((-1, 3))  # converts the width & height into a single dimension
    amount = int(array.shape[0] * percent)  # gets the length of the array, then takes the sample fraction
    index = np.arange(amount)  # same as list(range(...)), but more condense
    np.random.shuffle(index)

    return array[index[:amount]]


img = open_image()
sample(bitdepth(img))

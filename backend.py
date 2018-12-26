import tkinter as tk
from tkinter import filedialog as fd

import numpy as np
from PIL import Image


def rgb_to_hsv(r, g, b):
    """Converts a rgb to a hsv tuple"""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx - mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g - b) / df) + 360) % 360
    elif mx == g:
        h = (60 * ((b - r) / df) + 120) % 360
    elif mx == b:
        h = (60 * ((r - g) / df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df / mx) * 100
    v = mx * 100
    return h, s, v


def bit_depth(array, bits=4):
    """Compresses an image's color palette by zeroing out significant bits"""
    shift = 8 - bits
    half = (1 << shift) >> 1
    return ((array.astype(np.uint8) >> shift) << shift) + half


def sample(array, percent=.10):
    """Samples the percent of the image specified, returns bg color"""
    array = array.reshape((-1, 3))
    amount = int(float(array.shape[0]) * percent)  # gets the length of the array, then takes the sample fraction
    index = np.arange(amount)  # same as list(range(...)), but more condense
    np.random.shuffle(index)
    subset = array[index[:amount]]
    packed = rgb_packer(bit_depth(subset).astype(int))
    unique, counts = np.unique(packed, return_counts=True)

    return rgb_packer(unique[counts.argmax()], pack=False)


class Notes:

    def __init__(self, hsv_bg_color=None):
        self.image = open_image()
        if hsv_bg_color is None:
            self.bg_color = rgb_to_hsv(sample(img[0], .5))
        else:
            self.bg_color = hsv_bg_color
        self.palette = self.get_palette()

    def threshold(self):
        for x in self.image:
            for y in self.image[1]:

    def get_palette(self):
        _, sat, val = self.bg_color






def open_image():
    """Function used to test filetype and open image, converts file to RBG"""
    tk.Tk().withdraw()
    while True:
        file = fd.askopenfilename(title="Select Image", initialdir="C:/Users/%username%/Documents",
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

    rgb = np.array(img)
    hsv = np.array(img.convert('HSV'))

    return rgb, hsv


def rgb_packer(array, pack=True):
    """Converts rbg triples to single integers for comparison purposes, pack False unpacks the int"""
    if pack:
        orig_shape = array.shape[:-1]
        array = array.astype(int).reshape((-1, 3))
        array = (array[:, 0] << 16 | array[:, 1] << 8 | array[:, 2])
        return array.reshape(orig_shape)
    else:
        orig_shape = array.shape
        array = array.reshape((-1, 1))
        rgb = ((array >> 16) & 0xff, (array >> 8) & 0xff, array & 0xff)
        return np.hstack(rgb).reshape(orig_shape + (3,))


img = open_image()
background_rgb = sample(img[0], .5)
print(*background_rgb)
print(rgb_to_hsv(*background_rgb))

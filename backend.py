import tkinter as tk
from tkinter import filedialog as fd

import numpy as np
from scipy.cluster.vq import kmeans, vq
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


class Notes:

    def __init__(self, bg_rgb=None, v_thresh=30, s_thresh=20, bitdepth=6, colorcount=7, palette=None):
        self.image_rgb, self.image_hsv = open_image()
        self.image_final = Image
        self.bit_depth = bitdepth
        self.color_count = colorcount - 1

        if bg_rgb is None:
            self.bg_color_rbg = self.sample(self.image_rgb, .5)
            self.bg_color_hsv = rgb_to_hsv(*self.bg_color_rbg)
        else:
            self.bg_color_rbg = bg_rgb
            self.bg_color_hsv = rgb_to_hsv(*bg_rgb)

        self.v_threshold = v_thresh
        self.s_threshold = s_thresh

        self.color_palette = palette

    def threshold(self):
        """Determines foreground and background colors, and applies color palette"""
        _, s_bg, v_bg = self.bg_color_hsv
        s_pix = self.image_hsv[:, :, 1]
        v_pix = self.image_hsv[:, :, 2]
        s_diff = np.abs(s_bg - s_pix)
        v_diff = np.abs(v_bg - v_pix)
        foreground = ((v_diff >= self.v_threshold) | (s_diff >= self.s_threshold))
        colors = kmeans(self.image_hsv[foreground].astype(np.float32),
                        self.color_count)  # Thank you fancy SciPy clusters
        self.color_palette = np.vstack((self.bg_color_hsv, colors))
        foreground = foreground.flatten()
        temp = self.image_hsv.reshape((-1, 3))
        palette = np.zeros(temp.shape[0], dtype=np.uint8)
        palette = vq(temp[foreground], palette)  # returns codes and distance, only need codes
        palette = palette.reshape(self.image_hsv.shape[:-1])

        return palette

    def sample(self, array, percent=.10):
        """Samples the percent of the image specified, returns bg color"""
        array = array.reshape((-1, 3))
        amount = int(float(array.shape[0]) * percent)  # gets the length of the array, then takes the sample fraction
        index = np.arange(amount)  # same as list(range(...)), but more condense
        np.random.shuffle(index)
        subset = array[index[:amount]]
        # self.sample_set = subset  #  In the case that a sample set needs to be defined
        packed = rgb_packer(bit_depth(subset, self.bit_depth).astype(int))
        unique, counts = np.unique(packed, return_counts=True)

        return rgb_packer(unique[counts.argmax()], pack=False)

    def process(self):
        self.threshold()



f = Notes()
f.process()

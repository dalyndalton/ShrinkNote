import tkinter as tk
from tkinter import filedialog as fd
import math

import numpy as np
from scipy.cluster.vq import kmeans, vq
from PIL import Image

np.set_printoptions(threshold=np.nan)


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


def hsv_to_rgb(h, s, v):
    h = float(h)
    s = float(s) / 100
    v = float(v) / 100
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0:
        r, g, b = v, t, p
    elif hi == 1:
        r, g, b = q, v, p
    elif hi == 2:
        r, g, b = p, v, t
    elif hi == 3:
        r, g, b = p, q, v
    elif hi == 4:
        r, g, b = t, p, v
    elif hi == 5:
        r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return int(r), int(g), int(b)


def bit_depth(array, bits=4):
    """Compresses an image's color palette by zeroing out significant bits"""
    shift = 8 - bits
    half = (1 << shift) >> 1
    return ((array.astype(np.uint8) >> shift) << shift) + half


def open_image(file_path):
    """Function used to test filetype and open image, converts file to RBG"""
    tk.Tk().withdraw()
    while True:
        if file_path != "":
            try:
                img = Image.open(file_path)
            except IOError:
                print("ERROR: INVALID FILE TYPE")
            break
        else:
            print("ERROR: NO FILE SELECTED")

    if img.mode != 'RGB':
        img = img.convert('RGB')

    rgb = np.array(img)
    return rgb


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


def sample(array, percent=10):
    """Samples the percent of the image specified, returns bg color"""
    array = array.reshape((-1, 3))
    amount = int(
        float(array.shape[0]) * float(percent))  # gets the length of the array, then takes the sample fraction
    index = np.arange(array.shape[0])  # same as list(range(...)), but more condense
    np.random.shuffle(index)
    subset = array[index[:amount]]

    return subset


class Notes:

    def __init__(self, filepath, bg_rgb=None, v_thresh=30, s_thresh=20, bitdepth=6, colorcount=7, palette=None):

        self.file_path = filepath
        self.image_rgb = open_image(filepath)

        self.image_hsv = self.image_rgb
        for x in range(0, self.image_rgb.shape[0]):
            for y in range(0, self.image_rgb.shape[1]):
                self.image_hsv[x, y] = rgb_to_hsv(*self.image_rgb[x, y])
        self.image_rgb = (open_image(filepath))  # reassigns image_rgb, doesnt work without it

        self.image_final = Image
        self.bit_depth = bitdepth
        self.color_count = colorcount

        self.bg_color_rgb = self.get_bg_color(self.image_rgb)
        self.bg_color_hsv = rgb_to_hsv(*self.bg_color_rgb)

        if bg_rgb is not None:
            self.custom_bg = bg_rgb

        else:
            self.custom_bg = None

        self.v_threshold = v_thresh
        self.s_threshold = s_thresh

        self.color_palette = palette
        self.sample_set = []

        self.process()

    def foreground(self, sample_size):

        samp = sample_size

        _, s_bg, v_bg = self.bg_color_hsv
        s_pix = samp[:, 1]
        v_pix = samp[:, 2]
        s_diff = np.abs(s_bg - s_pix)
        v_diff = np.abs(v_bg - v_pix)
        return (v_diff >= self.v_threshold) | (s_diff >= self.s_threshold), samp

    def threshold(self):
        """Determines foreground and background colors, and applies color palette"""
        foreground, samp = self.foreground(sample(self.image_hsv))

        colors, _ = kmeans(samp[foreground].astype(np.float32),
                           self.color_count - 1)  # Thank you fancy SciPy clusters

        # Convert colors back to rgb
        for x in range(colors.shape[0]):
            colors[x] = hsv_to_rgb(*colors[x])

        self.color_palette = np.vstack((self.bg_color_rgb, colors)).astype(np.uint8)

        mask, _ = self.foreground(self.image_hsv.reshape((-1, 3)))

        pix = self.image_rgb.reshape((-1, 3))
        mask = mask.flatten()
        labs = np.zeros(pix.shape[0], dtype=np.uint8)
        labs[mask], _ = vq(pix[mask], self.color_palette)  # returns codes and distance, only need codes
        palette = labs.reshape(self.image_hsv.shape[:-1])
        print(labs, "\n \n \n", palette)

        return palette

    def get_bg_color(self, array, percent=None):
        if percent is not None:
            subset = sample(array, percent)
        else:
            subset = sample(array)

        packed = rgb_packer(bit_depth(subset, self.bit_depth).astype(np.uint8))
        unique, counts = np.unique(packed, return_counts=True)
        return rgb_packer(unique[counts.argmax()], pack=False)

    def process(self):
        temp_image = self.threshold()
        pal = self.color_palette.astype(np.float32)
        # saturate palette
        for x in range(pal.shape[0]):
            pal[x] = rgb_to_hsv(*pal[x])
            hue, sat, _ = pal[x]
            pal[x] = hue, sat, 100
            pal[x] = hsv_to_rgb(*pal[x])

        self.color_palette = pal.astype(np.uint8)
        if self.custom_bg is not None:
            self.color_palette[0] = self.custom_bg
        self.image_final = Image.fromarray(temp_image, 'P')
        self.image_final.putpalette(self.color_palette.flatten())


tk.Tk().withdraw()
file_path = file = fd.askopenfilename(title="Select Image", initialdir="C:/Users/%username%/Documents",
                                      filetypes=(("Images", ".jpeg"), ("Images", ".jpg"), ("Images", ".png")))
f = Notes(file_path, bitdepth=6, v_thresh=30, s_thresh=20, colorcount=8)
f.image_final.show()
input()

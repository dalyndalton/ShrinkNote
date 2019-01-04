import colorsys as cs

import numpy as np
from PIL import Image
from scipy.cluster.vq import kmeans, vq


def rgb_to_hsv(r, g, b):
    """Converts a rgb to a hsv tuple"""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    h, s, v = cs.rgb_to_hsv(r, g, b)
    return h, s, v


def hsv_to_rgb(h, s, v):
    r, g, b = cs.hsv_to_rgb(h, s, v)
    return int(round(r * 255)), int(round(g * 255)), int(round(b * 255))


def bit_depth(array, bits=4):
    """Compresses an image's color palette by zeroing out significant bits"""
    shift = 8 - bits
    half = (1 << shift) >> 1
    return ((array.astype(np.uint8) >> shift) << shift) + half


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
        float(array.shape[0]) * float(percent / 100))  # gets the length of the array, then takes the sample fraction
    index = np.arange(array.shape[0])  # same as list(range(...)), but more condense
    np.random.shuffle(index)
    subset = array[index[:amount]]

    return subset


class Notes:

    def __init__(self, img_file, bg_rgb=None, v_thresh=30, s_thresh=20, bitdepth=6, colorcount=7, palette=None):

        self.image_rgb = np.array(img_file, dtype=np.uint8)

        self.image_hsv = self.image_rgb.astype(np.float32)
        for x in range(0, self.image_rgb.shape[0]):
            for y in range(0, self.image_rgb.shape[1]):
                self.image_hsv[x, y] = rgb_to_hsv(*self.image_rgb[x, y])
        self.image_rgb = np.array(img_file)  # reassigns image_rgb, doesnt work without it
        self.image_final = Image
        self.bit_depth = bitdepth
        self.color_count = colorcount

        self.bg_color_rgb = self._get_bg_color(self.image_rgb)
        self.bg_color_hsv = rgb_to_hsv(*self.bg_color_rgb)

        if bg_rgb is not None:
            self.custom_bg = bg_rgb

        else:
            self.custom_bg = None

        self.v_threshold = v_thresh
        self.s_threshold = s_thresh

        self.color_palette = palette
        self.sample_set = []

    def _foreground(self, sample_size):

        samp = sample_size
        _, s_bg, v_bg = self.bg_color_hsv
        s_pix = samp[:, 1]
        v_pix = samp[:, 2]
        s_diff = np.abs(s_bg - s_pix)
        v_diff = np.abs(v_bg - v_pix)
        return (v_diff >= self.v_threshold / 100) | (s_diff >= self.s_threshold / 100), samp

    def _threshold(self):
        """Determines foreground and background colors, and applies color palette"""
        foreground, samp = self._foreground(sample(self.image_hsv))
        colors, _ = kmeans(samp[foreground].astype(np.float32),
                           self.color_count - 1, iter=40)  # Thank you fancy SciPy clusters

        # Convert colors back to rgb
        for x in range(colors.shape[0]):
            colors[x] = hsv_to_rgb(*colors[x])

        self.color_palette = np.vstack((self.bg_color_rgb, colors)).astype(np.uint8)
        mask, _ = self._foreground(self.image_hsv.reshape((-1, 3)))

        pix = self.image_rgb.reshape((-1, 3))
        mask = mask.flatten()
        labs = np.zeros(pix.shape[0], dtype=np.uint8)
        labs[mask], _ = vq(pix[mask], self.color_palette)  # returns codes and distance, only need codes
        palette = labs.reshape(self.image_hsv.shape[:-1])

        return palette

    def _get_bg_color(self, array, percent=None):
        if percent is not None:
            subset = sample(array, percent)
        else:
            subset = sample(array)

        packed = rgb_packer(bit_depth(subset, self.bit_depth).astype(np.uint8))
        unique, counts = np.unique(packed, return_counts=True)
        return rgb_packer(unique[counts.argmax()], pack=False)

    def process(self):
        temp_image = self._threshold()
        pal = self.color_palette.astype(np.float32)

        # saturate palette, didn't work so depreciating
        for x in range(1, pal.shape[0]):
            pal[x] = rgb_to_hsv(*pal[x])
            hue, sat, val = pal[x]
            pal[x] = hue, 1, val
            pal[x] = hsv_to_rgb(*pal[x])
        # pal = 255 * (pal - pal.min()/(pal.max()-pal.min()))
        self.color_palette = pal.astype(np.uint8)
        if self.custom_bg is not None:
            self.color_palette[0] = self.custom_bg
        self.image_final = Image.fromarray(temp_image, 'P')
        self.image_final.putpalette(self.color_palette.flatten())
        return self.image_final


'''
f = Notes(np.array(Image.open("C:\\Users\\dalyn\\Documents\\Scanned Documents\\Image.jpg")), bitdepth=6, v_thresh=25,
          s_thresh=15,
          colorcount=8, bg_rgb=(254, 254, 254))

f.process().save("C:\\Users\\dalyn\\Documents\\testfile.png")
'''

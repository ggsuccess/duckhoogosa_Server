#!/usr/bin/env python

# This script will take a jpg or png image, pixelate it, and convert those "pixels" to NES colors
# NES colors are the 54 colors available in the original Nintendo color palette
#
# To calculate which color to lock to, the LAB color space is used which is
# better than RGB for calculating the "distance" between two colors
#
# Still, the distance metric could use some work. Some colors choices are puzzling.
# It is a TODO

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import PIL.Image as Image

from colormath.color_diff import delta_e_cie1976 as color_distance
from colormath.color_conversions import XYZ_to_Lab, RGB_to_XYZ
from colormath.color_objects import sRGBColor

# from http://www.thealmightyguru.com/Games/Hacking/Wiki/index.php?title=NES_Palette
from scipy._lib.six import xrange

NES_COLORS_RGB = [
    (124, 124, 124),
    (0, 0, 252),
    (0, 0, 188),
    (68, 40, 188),
    (148, 0, 132),
    (168, 0, 32),
    (168, 16, 0),
    (136, 20, 0),
    (80, 48, 0),
    (0, 120, 0),
    (0, 104, 0),
    (0, 88, 0),
    (0, 64, 88),
    (0, 0, 0),
    (188, 188, 188),
    (0, 120, 248),
    (0, 88, 248),
    (104, 68, 252),
    (216, 0, 204),
    (228, 0, 88),
    (248, 56, 0),
    (228, 92, 16),
    (172, 124, 0),
    (0, 184, 0),
    (0, 168, 0),
    (0, 168, 68),
    (0, 136, 136),
    (248, 248, 248),
    (60, 188, 252),
    (104, 136, 252),
    (152, 120, 248),
    (248, 120, 248),
    (248, 88, 152),
    (248, 120, 88),
    (252, 160, 68),
    (248, 184, 0),
    (184, 248, 24),
    (88, 216, 84),
    (88, 248, 152),
    (0, 232, 216),
    (120, 120, 120),
    (252, 252, 252),
    (164, 228, 252),
    (184, 184, 248),
    (216, 184, 248),
    (248, 184, 248),
    (248, 164, 192),
    (240, 208, 176),
    (252, 224, 168),
    (248, 216, 120),
    (216, 248, 120),
    (184, 248, 184),
    (184, 248, 216),
    (0, 252, 252),
    (248, 216, 248),
]


def RGB_to_Lab(rgb):
    return XYZ_to_Lab(RGB_to_XYZ(sRGBColor(*rgb)))


NES_COLORS_LAB = {RGB_to_Lab(c): c for c in NES_COLORS_RGB}


def closest_color(the_color):
    the_lab_color = RGB_to_Lab(the_color)
    most_similar_lab = min(NES_COLORS_LAB,
                           key=lambda x: color_distance(x, the_lab_color))

    return NES_COLORS_LAB[most_similar_lab]


def load_img(filename):
    # boilerplate code to open an image and make it editable
    img = Image.open(filename)
    data = np.array(img)
    return data


def all_square_pixels(row, col, square_h, square_w):
    # Every pixel for a single "square" (superpixel)
    # Note that different squares might have different dimensions in order to
    # not have extra pixels at the edge not in a square. Hence: int(round())
    for y in xrange(int(round(row * square_h)), int(round((row + 1) * square_h))):
        for x in xrange(int(round(col * square_w)), int(round((col + 1) * square_w))):
            yield y, x


def make_one_square(img, row, col, square_h, square_w):
    # Sets all the pixels in img for the square given by (row, col) to that
    # square's average color
    pixels = []

    # get all pixels
    for y, x in all_square_pixels(row, col, square_h, square_w):
        pixels.append(img[y][x])

    # get the average color
    av_r = 0
    av_g = 0
    av_b = 0
    for r, g, b in pixels:
        av_r += r
        av_g += g
        av_b += b
    av_r /= len(pixels)
    av_g /= len(pixels)
    av_b /= len(pixels)

    gamified_color = closest_color((av_r, av_g, av_b))

    # set all pixels to that average color
    for y, x in all_square_pixels(row, col, square_h, square_w):
        img[y][x] = gamified_color


def make_img_pixel(filename):
    try:
        filename = sys.argv[1]
    except IndexError:
        filename = os.getcwd() + "/download/" + filename
    img = load_img(filename)

    # Figure out the dimensions of each square
    # We want:
    # 1. Square width and height should be about the same
    # 2. No leftover pixels at the edges
    # This means that some squares might have one more or one less pixel
    # depending on rounding
    num_cols = int(75)
    square_w = float(img.shape[1]) / num_cols
    num_rows = int(round(img.shape[0] / square_w))
    square_h = float(img.shape[0]) / num_rows

    # overwrite each square with the average color, one by one
    for row in range(num_rows):
        for col in range(num_cols):
            make_one_square(img, row, col, square_h, square_w)

    # show the image
    fig = plt.figure(frameon=False)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    ax.axis('off')
    fig.add_axes(ax)
    plt.imshow(img)

    # save the image
    filename_parts = filename.rsplit('.', 1)
    filename = '.'.join(filename_parts)
    print("Saving as", filename)
    # KTH CHANGED
    if os.path.isfile(filename):
        os.remove(filename)
        print("Delete Prev File and save file")
    fig.savefig(filename, bbox_inches='tight', transparent=True, pad_inches=0)

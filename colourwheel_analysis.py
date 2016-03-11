#!/usr/bin/env python

from array import array
from collections import defaultdict
import logging
import math


try:
    import gimpfu
except:
    # for unit tests; no gimp environment available
    gimpfu = None


logging.basicConfig(level=logging.WARN)


try:
    # Python 2.x
    irange = xrange
except NameError:
    # Python 3.x
    irange = range


def rgb2hsl(r, g, b):
    """Convert RGB to HSL.

    After http://www.rapidtables.com/convert/color/rgb-to-hsv.htm
    """

    r = r/255.0
    g = g/255.0
    b = b/255.0
    cmax = max((r, g, b))
    cmin = min((r, g, b))
    delta = cmax - cmin

    h = 0
    s = 0
    l = (cmax + cmin) / 2

    if delta != 0:
        s = delta/(1 - abs(2 * l - 1))
        if cmax == r:
            h = 60 * (((g - b) / delta) % 6)
        elif cmax == g:
            h = 60 * (((b - r) / delta) + 2)
        elif cmax == b:
            h = 60 * (((r - g) / delta) + 4)

    return int(h), int(s * 100), int(l * 100)


def hsl2rgb(h, s, l):
    """Convert HSL to RGB.

    After http://www.rapidtables.com/convert/color/hsv-to-rgb.htm
    """
    s = s / 100.0
    l = l / 100.0
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60.0) % 2 - 1))
    m = l - c/2.0

    if h < 60:
        r, g, b = (c, x, 0)
    elif h < 120:
        r, g, b = (x, c, 0)
    elif h < 180:
        r, g, b = (0, c, x)
    elif h < 240:
        r, g, b = (0, x, c)
    elif h < 300:
        r, g, b = (x, 0, c)
    else:
        r, g, b = (c, 0, x)

    return (int(255 * (r + m)), int(255 * (g + m)), int(255 * (b + m)))


def collect_colours(pixels, pixel_size, theshold):
    """Collect colours from an array.

    Count their frequency by hue and saturation, ignoring lightness
    and alpha, and return (hue, saturation) tuples above the threshold.
    """

    colourmap = defaultdict(int)

    for i in irange(0, len(pixels), pixel_size):
        h, s, l = rgb2hsl(pixels[i], pixels[i + 1], pixels[i + 2])
        colourmap[(h, s)] += 1

    logging.debug(colourmap)
    colours = [hs for hs, count in colourmap.items() if count >= theshold]
    logging.debug(colours)
    return colours


def colourwheel_position(h, s, size):
    """Calculates the (x, y)-coordinates of the hue h and saturation s in
    a colour wheel of sizel ``size``.
    """

    h = math.radians(h)
    x = s * math.sin(h) * size/200 + size/2
    y = s * math.cos(h) * size/200 + size/2

    return int(x), int(y)


def get_pixel_array(image, dirty):
    """Returns the image's pixels as Python array.

    Working on the array is a lot faster than accessing individual
    pixels directly.
    """

    layer = image.active_layer
    logging.info('Reading layer "%s"' % layer.name)
    region = layer.get_pixel_rgn(0, 0, layer.width, layer.height, dirty)
    pixels = array("B", region[0:layer.width, 0:layer.height])
    pixel_size = len(layer.get_pixel(0, 0))
    logging.debug('Number of pixels: %s', len(pixels))
    logging.debug('Pixel size: %s', pixel_size)
    return pixels, pixel_size, region


def prepare_output_image(size):
    """Create new image with white background and a black circle for
    the colour wheel."""

    logging.info('Preparing output image')
    img = gimpfu.gimp.Image(size, size, gimpfu.RGB)
    layer = gimpfu.gimp.Layer(
        img, 'Background', size, size, gimpfu.RGB_IMAGE, 100,
        gimpfu.NORMAL_MODE)
    old_fg = gimpfu.gimp.get_foreground()
    old_bg = gimpfu.gimp.get_background()
    gimpfu.gimp.set_foreground((0, 0, 0))
    gimpfu.gimp.set_background((255, 255, 255))
    layer.fill(gimpfu.BACKGROUND_FILL)
    img.add_layer(layer, 1)
    gimpfu.pdb.gimp_ellipse_select(
        img, 0, 0, size, size, 2, True, False, False)
    gimpfu.pdb.gimp_edit_fill(layer, gimpfu.FOREGROUND_FILL)
    gimpfu.pdb.gimp_selection_none(img)
    gimpfu.gimp.set_foreground(old_fg)
    gimpfu.gimp.set_background(old_bg)
    return img, layer


def draw_pixel_to_array(array_, size, x, y, rgb):
    """Draw pixel to Python array.

    Ensure that x, y are within range; cap if necassary.
    """

    x = max(min(x, size - 1), 0)
    y = max(min(y, size - 1), 0)
    pos = (size * y + x) * 3
    array_[pos] = rgb[0]
    array_[pos + 1] = rgb[1]
    array_[pos + 2] = rgb[2]


def draw_colourwheel_distribution(img, layer, size, colours, draw_as):
    """Draws the colour wheel output."""

    logging.info('Drawing output')
    pixels, pixel_sizel, region = get_pixel_array(img, dirty=True)
    size = img.active_layer.width
    for h, s in colours:
        x, y = colourwheel_position(h, s, size)
        rgb = hsl2rgb(h, s, 50)

        draw_pixel_to_array(pixels, size, x, y, rgb)

        if draw_as in ('cross', 'square'):
            draw_pixel_to_array(pixels, size, x - 1, y, rgb)
            draw_pixel_to_array(pixels, size, x + 1, y, rgb)
            draw_pixel_to_array(pixels, size, x, y - 1, rgb)
            draw_pixel_to_array(pixels, size, x, y + 1, rgb)

        if draw_as == 'square':
            draw_pixel_to_array(pixels, size, x - 1, y - 1, rgb)
            draw_pixel_to_array(pixels, size, x - 1, y + 1, rgb)
            draw_pixel_to_array(pixels, size, x + 1, y - 1, rgb)
            draw_pixel_to_array(pixels, size, x + 1, y + 1, rgb)

    region[:size, :size] = pixels.tostring()


def python_colourwheel_analysis(image, drawable, threshold=1, draw_as='cross'):
    """The plugin's main function."""

    # collect colour info
    gimpfu.gimp.progress_init('Analyzing colours...')
    pixels, pixel_size, region = get_pixel_array(image, dirty=False)
    colours = collect_colours(pixels, pixel_size, threshold)

    # write colour info to new image
    gimpfu.gimp.progress_update(0.33)
    size = 200
    out_img, out_layer = prepare_output_image(size)
    gimpfu.gimp.progress_update(0.66)
    draw_colourwheel_distribution(out_img, out_layer, size, colours, draw_as)

    # display results
    gimpfu.gimp.progress_update(1)
    gimpfu.gimp.Display(out_img)
    gimpfu.gimp.displays_flush()


if gimpfu:
    gimpfu.register(
        'python_fu_colourwheel_analysis',
        'Display colour distribution on a colour wheel.',
        'Display colour distribution on a colour wheel.',
        'Rebecca Breu',
        '2016 Rebecca Breu, GPLv3',
        '10 March 2016',
        '<Image>/Colors/Info/Colour Wheel Analysis...',

    'RGB*',
        [
            (gimpfu.PF_INT,
             'threshold',
             'Min. number of occurences per colour',
             1),
            (gimpfu.PF_RADIO,
             'draw_as',
             'Draw colours as',
             'cross',
             (('Single pixels', 'pixel'),
              ('Crosses', 'cross'),
              ('Squares', 'square')),
             )
        ],
        [],
        python_colourwheel_analysis,
    )

    gimpfu.main()

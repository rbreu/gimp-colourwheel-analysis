#!/usr/bin/env python

from array import array
from collections import defaultdict
import logging


try:
    import gimpfu
except:
    # for unit tests; no gimp environment available
    gimpfu = None


logging.basicConfig(level=logging.DEBUG)


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


def collect_colours(pixels, pixel_size):
    """Collect colours from an array.

    Count their frequency by hue and saturation (ignoring lightness
    and alpha).
    """

    colourmap = defaultdict(int)

    for i in irange(0, len(pixels), pixel_size):
        h, s, l = rgb2hsl(pixels[i], pixels[i + 1], pixels[i + 2])
        colourmap[(h, s)] += 1

    logging.debug(colourmap)
    return colourmap


def get_pixel_array(image):
    """Returns the image's pixels as Python array.

    Working on the array is a lot faster than accessing individual
    pixels directly.
    """

    layer = image.active_layer
    logging.info('Collecting colour info on layer "%s"' % layer.name)
    region = layer.get_pixel_rgn(0, 0, layer.width, layer.height, dirty=False)
    pixels = array("B", region[0:layer.width, 0:layer.height])
    pixel_size = len(layer.get_pixel(0, 0))
    logging.debug('Number of pixels: %s', len(pixels))
    logging.debug('Pixel size: %s', pixel_size)
    return pixels, pixel_size


def prepare_output_image():
    """Create new image with white background and a black circle for
    the colour wheel."""
    loggin.info('Preparing output image')
    img = gimpfu.gimp.Image(200, 200, gimpfu.RGB)
    layer = gimpfu.gimp.Layer(
        img, 'Background', 200, 200, gimpfu.RGB_IMAGE, 100, gimpfu.NORMAL_MODE)
    gimpfu.gimp.set_background((0, 0, 0))
    gimpfu.gimp.set_foreground((255, 255, 255))
    layer.fill(gimpfu.BACKGROUND_FILL)
    img.add_layer(layer, 1)
    return img, layer


def python_colourwheel_analysis(image, drawable, threshold=1):
    """The plugin's main function."""

    # collect colour info
    gimpfu.gimp.progress_init('Analyzing colours...')
    pixels, pixel_size = get_pixel_array(image)
    colourmap = collect_colours(pixels, pixel_size)

    # write colour info to new image
    gimpfu.gimp.progress_update(0.5)
    out_img, out_layer = prepare_output_image()

    # display results
    gimpfu.gimp.progress_update(1)
    gimpfu.gimp.Display(out_img)
    gimpfu.gimp.displays_flush()


if gimpfu:
    gimpfu.register(
        'python_fu_colourwheel_analysis',
        'Display colours used in the image on a colour wheel',
        'Display colours used in the image on a colour wheel',
        'Rebecca Breu',
        'Rebecca Breu',
        '2016',
        '<Image>/Colors/Info/Colour Wheel Analysis...',

    'RGB*',
        [
            (gimpfu.PF_INT,
             'threshold',
             'Min. number of occurences per colour', 1),
        ],
        [],
        python_colourwheel_analysis,
    )

    gimpfu.main()

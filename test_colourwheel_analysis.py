import pytest
from colourwheel_analysis import rgb2hsl, hsl2rgb, collect_colours


rgb_hsl_testdata = [
    [(0, 0, 0), (0, 0, 0)],
    [(255, 255, 255), (0, 0, 100)],
    [(255, 0, 0), (0, 100, 50)],
    [(0, 255, 0), (120, 100, 50)],
    [(0, 0, 255), (240, 100, 50)],
    [(255, 255, 0), (60, 100, 50)],
    [(0, 255, 255), (180, 100, 50)],
    [(255, 0, 255), (300, 100, 50)],
    [(63, 191, 191), (180, 50, 50)],
]


epsilon = 1


@pytest.mark.parametrize("rgb,hsl", rgb_hsl_testdata)
def test_rgb2hsl(rgb, hsl):
    result = rgb2hsl(*rgb)
    assert abs(result[0] - hsl[0]) <= epsilon
    assert abs(result[1] - hsl[1]) <= epsilon
    assert abs(result[2] - hsl[2]) <= epsilon


@pytest.mark.parametrize("rgb,hsl", rgb_hsl_testdata)
def test_hsl2rgb(rgb, hsl):
    result = hsl2rgb(*hsl)
    assert abs(result[0] - rgb[0]) <= epsilon
    assert abs(result[1] - rgb[1]) <= epsilon
    assert abs(result[2] - rgb[2]) <= epsilon


def test_collect_colours_rgb():
    pixels = [255, 255, 255,
              255, 255, 255,
              255, 255, 255,
              0, 0, 255]
    assert collect_colours(pixels, 3) == {(0, 0): 3, (240, 100): 1}


def test_collect_colours_rgba():
    pixels = [255, 255, 255, 255,
              255, 255, 255, 255,
              255, 255, 255, 255,
              0, 0, 255, 255]
    assert collect_colours(pixels, 4) == {(0, 0): 3, (240, 100): 1}

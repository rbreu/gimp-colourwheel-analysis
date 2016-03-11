import pytest
from colourwheel_analysis import (
    collect_colours,
    colourwheel_position,
    draw_pixel_to_array,
    hsl2rgb,
    rgb2hsl,
)


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
    assert collect_colours(pixels, 3, 1) == [(0, 0), (240, 100)]


def test_collect_colours_rgba():
    pixels = [255, 255, 255, 255,
              255, 255, 255, 255,
              255, 255, 255, 255,
              0, 0, 255, 255]
    assert collect_colours(pixels, 4, 1) == [(0, 0), (240, 100)]


def test_collect_coulours_threshold():
    pixels = [255, 255, 255,
              255, 255, 255,
              255, 255, 255,
              0, 0, 255]
    assert collect_colours(pixels, 3, 2) == [(0, 0)]


@pytest.mark.parametrize("hs,pos", [
    [(0, 0), (100, 100)],
    [(0, 100), (100, 200)],
    [(0, 50), (100, 150)],
    [(90, 100), (200, 100)],
    [(180, 100), (100, 0)],
    [(270, 100), (0, 100)],
])
def test_colourwheel_position(hs, pos):
    result = colourwheel_position(*hs, size=200)
    assert abs(result[0] - pos[0]) <= epsilon
    assert abs(result[1] - pos[1]) <= epsilon


def test_draw_pixel_to_array():
    a = [0] * 3 * 4 * 4
    draw_pixel_to_array(a, 4, 1, 2, (1, 2, 3))
    assert a == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def test_draw_pixel_to_array_cutoff():
    a = [0] * 3 * 4 * 4
    draw_pixel_to_array(a, 4, 1, 4, (1, 2, 3))
    assert a == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0]

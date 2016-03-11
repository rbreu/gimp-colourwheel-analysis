# gimp-colourwheel-analysis

GIMP-Plugin that displays colour distribution on a colour wheel. It
was inpspired by
[James Gurney's thoughts](http://gurneyjourney.blogspot.de/2011/09/part-1-gamut-masking-method.html) on limited palettes and gamut masking.


## Examples and Usage

Note that only hue and saturation are taken into account; differences
in lightness will be ignored. You can choose how many times a
hue/saturation combination has to occur within the source image before
it gets displayed in the result. Furthermore, you can choose how
results are displayed on the output colour wheel.

![Dialogue Window](images/dialogue.png "Dialogue Window")

Output as pixels:

![Example: display as pixels](images/example2.png "Example: display as pixels")

Output as squares:

![Example: display as squares](images/example1.png "Example: display as squares")


## Installation

Download [colourwheel_analysis.py](https://raw.githubusercontent.com/rbreu/gimp-colourwheel-analysis/master/colourwheel_analysis.py)
and save it in your plug-ins folder, e.g. `~/.gimp-2.8/plug-ins/`. Then restart GIMP.

On Linux and Mac, make sure to give the file executable rights:

```
$ chmod 755 ~/.gimp-2.8/plug-ins/colourwheel_analysis.py
```

## For Developers

The plugin is written in Python. There are unit tests that cover the GIMP-independent calculations. To run them, you need to install pytest, then place both `colourwheel_analysis.py` and `test_colourwheel_analysis.py` in the same folder, preferrably not in your plug-ins folder. Run the tests with:

```
$ py.test
```
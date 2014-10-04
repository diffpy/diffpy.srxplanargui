dpx.srxplanargui
========================================================================

GUI for diffpy.srxplanar

REQUIREMENTS
------------------------------------------------------------------------

The dpx.srxplanargui requires Python 2.7 and the following software:

* ``diffpy.srxplanar``
* ``dpx.confutils``
* ``dpx.srxplanargui``
* ``numpy``
* ``traits``
* ``traitsui``
* ``chaco``
* ``mayavi``

To enable calibrant image calibration function, following packages are required:

* ``pyFAI``
* ``FabIO``
* ``matplotlib``

BACKENDS
------------------------------------------------------------------------

SrXplanargui can use both WX and Qt backends. Please note that traitsui has
compatibility issuses with WX>2.8. It only works with WX 2.8. So it is strongly
recommonded to use QT backend (default). Especailly for MacOSX which the WX2.8 is not
available for the latest distribution.

WX backend requires:
* ``wxpython=2.8``

Qt backend requires:
* ``pyQt``
or
* ``pyside``

If you would like to use image calibration function in pyFAI, please note that
pyside may not work and you probably need to switch to pyQt.

To start SrXplanargui using different backend, use

    srxplanargui --toolkit backend

where backend could be "wx" or "qt"

INSTALLATION
------------------------------------------------------------------------

To install the dpx.pdfgetxgui package:

    python setup.py install

By default the files are installed in the system directories, which are
usually only writeable by the root.  See the usage info "./setup.py install
--help" for options to install as a normal user under a different location.
Note that installation to non-standard directories you may require adjustments
to the PATH and PYTHONPATH environment variables.

CONTACTS
------------------------------------------------------------------------

For more information on diffpy.Structure please visit the project web-page

http://www.diffpy.org/

or email Prof. Simon Billinge at sb2896@columbia.edu.

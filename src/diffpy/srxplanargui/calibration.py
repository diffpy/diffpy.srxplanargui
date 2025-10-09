#!/usr/bin/env python
##############################################################################
#
# diffpy.srxplanargui    by Simon J. L. Billinge group
#                   (c) 2012-2025 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Xiaohao Yang
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

import os
import re
import sys

from pyface.api import ImageResource
from traits.api import (
    Bool,
    DelegatesTo,
    Directory,
    Enum,
    File,
    Float,
    HasTraits,
    Instance,
    Int,
    Str,
    on_trait_change,
)
from traits.etsconfig.api import ETSConfig
from traitsui.api import Group, Handler, HGroup, Item, VGroup, View
from traitsui.menu import CancelButton, OKButton

from diffpy.srxconfutils.tools import module_exists_lower
from diffpy.srxplanar.selfcalibrate import selfCalibrate
from diffpy.srxplanar.srxplanar import SrXplanar
from diffpy.srxplanar.srxplanarconfig import checkMax
from diffpy.srxplanargui.srxconfig import SrXconfig

ETSConfig.toolkit = "qt"

if module_exists_lower("pyfai"):
    import pyFAI

    missingpyFAI = False
else:
    missingpyFAI = True

# determine option name for calibrant used in pyFAI-calib
# The current option is "-c", but it was "-S" in 0.9.3.
pyFAIcalib_opt_calibrant = "-c"
if not missingpyFAI:
    from pkg_resources import parse_version

    if parse_version(pyFAI.version) <= parse_version("0.9.3"):
        pyFAIcalib_opt_calibrant = "-S"
    del parse_version


class CalibrationHandler(Handler):

    def closed(self, info, is_ok):
        """Notify main gui to delete current plot in plots list."""
        if is_ok:
            info.object.calibration()
        return True


class Calibration(HasTraits):
    image = File
    dspacefile = File
    srx = Instance(SrXplanar)
    srxconfig = Instance(SrXconfig)
    pythonbin = File
    pyFAIdir = Directory
    caliscript = File
    missingpyFAI = Bool(False)

    xpixelsize = DelegatesTo("srxconfig")
    ypixelsize = DelegatesTo("srxconfig")
    wavelength = DelegatesTo("srxconfig")
    xbeamcenter = DelegatesTo("srxconfig")
    ybeamcenter = DelegatesTo("srxconfig")
    xdimension = DelegatesTo("srxconfig")
    ydimension = DelegatesTo("srxconfig")
    distance = DelegatesTo("srxconfig")
    rotationd = DelegatesTo("srxconfig")
    tiltd = DelegatesTo("srxconfig")
    configmode = DelegatesTo("srxconfig")
    xpixelsizetem = DelegatesTo("srxconfig")
    ypixelsizetem = DelegatesTo("srxconfig")

    def __init__(self, *args, **kwargs):
        super(Calibration, self).__init__(*args, **kwargs)
        self.locatePyFAI()
        self.missingpyFAI = missingpyFAI
        return

    def locatePyFAI(self):
        pythonbin = sys.executable
        if sys.platform == "win32":
            pyFAIdir = os.path.join(sys.exec_prefix, "Scripts")
        elif sys.platform.startswith("linux"):
            pyFAIdir = os.path.join(sys.exec_prefix, "bin")
        else:
            pyFAIdir = os.path.join(sys.exec_prefix, "bin")
        self.pythonbin = pythonbin
        self.pyFAIdir = pyFAIdir
        return

    @on_trait_change("pyFAIdir")
    def _pyFAIdirChanged(self):
        if sys.platform == "win32":
            caliscript = os.path.join(self.pyFAIdir, "pyFAI-calib.py")
            intescript = os.path.join(self.pyFAIdir, "pyFAI-waxs.py")
        elif sys.platform.startswith("linux"):
            caliscript = os.path.join(self.pyFAIdir, "pyFAI-calib")
            intescript = os.path.join(self.pyFAIdir, "pyFAI-waxs")
        else:
            caliscript = os.path.join(self.pyFAIdir, "pyFAI-calib")
            intescript = os.path.join(self.pyFAIdir, "pyFAI-waxs")
        self.caliscript = caliscript
        self.intescript = intescript
        return

    def callPyFAICalibration(self, image=None, dspacefile=None):
        if image is None:
            image = self.image
        else:
            self.image = image
        if dspacefile is None:
            dspacefile = self.dspacefile
        else:
            self.dspacefile = dspacefile

        flag = False
        if os.path.exists(image) and os.path.isfile(image):
            if os.path.exists(dspacefile) and os.path.isfile(dspacefile):
                flag = True

        if flag:
            image = os.path.abspath(image)
            dspacefile = os.path.abspath(dspacefile)

            # remove .npt and .azim
            for f in [
                os.path.splitext(image)[0] + ".npt",
                os.path.splitext(image)[0] + ".azim",
            ]:
                if os.path.exists(f):
                    os.remove(f)

            ps = [self.xpixelsize * 1000, self.ypixelsize * 1000]

            calicmd = [self.pythonbin, self.caliscript]
            calicmd.extend(["-w", str(self.wavelength)])
            calicmd.extend([pyFAIcalib_opt_calibrant, str(dspacefile)])
            calicmd.extend(["-p", str(ps[0]) + "," + str(ps[1])])
            calicmd.extend([str(image)])

            import subprocess

            try:
                os.environ.pop("QT_API")
            except KeyError:
                pass
            subprocess.call(calicmd)

            # integrate image
            ponifile = os.path.splitext(str(image))[0] + ".poni"
            intecmd = [
                self.pythonbin,
                self.intescript,
                "-p",
                ponifile,
                str(image),
            ]
            subprocess.call(intecmd)
            self.parsePyFAIoutput(image)
            print("Calibration finished!")
        return

    def parsePyFAIoutput(self, image=None):
        if image is None:
            image = self.image

        filename = os.path.splitext(image)[0] + ".xy"
        if os.path.exists(filename):
            f = open(filename, "r")
            lines = f.readlines()
            f.close()
        else:
            raise ValueError("pyFAI results file does not exist.")
        for line in lines:
            if re.search("# Distance Sample-beamCenter", line):
                distance = findFloat(line)[0]
            elif re.search("# Center", line):
                x, y = findFloat(line)
            elif re.search("# Tilt", line):
                tiltd, rotationd = findFloat(line)

        self.distance = distance
        self.xbeamcenter = x  # - 0.5
        self.ybeamcenter = y  # - y - 0.5
        self.tiltd = tiltd
        self.rotationd = rotationd  # + 180
        self.srxconfig.flipvertical = False
        self.srxconfig.fliphorizontal = False
        return

    def selfCalibration(self, image=None):
        # self.addfiles.selected[0].fullname
        if image is None:
            image = self.image

        if os.path.exists(image) and os.path.isfile(image):
            for mode, showresults in zip(
                ["x", "y", "x", "y"], [False, False, False, True]
            ):
                selfCalibrate(
                    self.srx,
                    image,
                    mode=mode,
                    cropedges=self.slice,
                    showresults=showresults,
                    xywidth=self.xywidth,
                )
        return

    slice = Enum(["auto", "x", "y", "box", "full"])
    calibrationmode = Enum(["self", "calibrant"])

    def calibration(self, image=None, dspacefile=None):
        if self.calibrationmode == "calibrant":
            self.callPyFAICalibration(image, dspacefile)
        elif self.calibrationmode == "self":
            self.selfCalibration(image)
        else:
            raise ValueError("calibration mode error")
        return

    xywidth = Int(6)
    qmincali = Float(0.5)
    qmaxcali = Float(10.0)

    @on_trait_change(
        "srxconfig.[xpixelsize, ypixelsize, distance,"
        " wavelength, xdimension, ydimension]"
    )
    def _qmaxChanged(self):
        tthmax, qmax = checkMax(self.srxconfig)
        self.qmincali = min(1.25, qmax / 10)
        self.qmaxcali = qmax / 2
        return

    inst1 = Str(
        "Please install pyFAI and FabIO to use"
        " the calibration function (refer to help)."
    )
    inst2 = Str(
        "(http://github.com/kif/pyFAI,"
        " https://forge.epn-campus.eu/projects/azimuthal/files)"
    )
    main_View = View(
        # Item('calibrationmode', style='custom', label='Calibration mode'),
        Item("image", label="Image file"),
        Group(
            Item("inst1", style="readonly"),
            Item("inst2", style="readonly"),
            visible_when='missingpyFAI and calibrationmode=="calibrant"',
            show_border=True,
            show_labels=False,
        ),
        Group(
            Item("dspacefile", label="D-space file"),
            Item("pyFAIdir", label="pyFAI dir."),
            show_border=True,
            visible_when='calibrationmode=="calibrant"',
            enabled_when="not missingpyFAI",
            label="Please specify the d-space file and"
            + " the location of pyFAI executable",
        ),
        HGroup(
            Item(
                "xpixelsize",
                label="Pixel size x (mm)",
                visible_when='configmode == "normal"',
            ),
            Item(
                "xpixelsizetem",
                label="Pixel size x (A^-1)",
                visible_when='configmode == "TEM"',
            ),
            Item(
                "ypixelsize",
                label="Pixel size y (mm)",
                visible_when='configmode == "normal"',
            ),
            Item(
                "ypixelsizetem",
                label="Pixel size y (A^-1)",
                visible_when='configmode == "TEM"',
            ),
            visible_when='calibrationmode=="calibrant"',
            enabled_when="not missingpyFAI",
            show_border=True,
            label="Please specify the size of pixel",
        ),
        HGroup(
            Item("wavelength", label="Wavelength (A)"),
            visible_when='calibrationmode=="calibrant"',
            enabled_when="not missingpyFAI",
            show_border=True,
            label="Please specify the wavelength",
        ),
        HGroup(
            Item(
                "wavelength",
                visible_when='integrationspace == "qspace"',
                label="Wavelength(Angstrom)",
            ),
            Item(
                "distance",
                label="Distance(mm)",
                visible_when='configmode == "normal"',
            ),
            Item(
                "distance",
                label="Camera Length(mm)",
                visible_when='configmode == "TEM"',
            ),
            label="Please specify the wavelength and"
            + " distance between sample and detector:",
            show_border=True,
            visible_when='calibrationmode=="self"',
        ),
        HGroup(
            VGroup(
                Item("xbeamcenter", label="x beamcenter (pixel)"),
                Item("rotationd", label="Rotation (degree)"),
            ),
            VGroup(
                Item("ybeamcenter", label="y beamcenter (pixel)"),
                Item("tiltd", label="Tilt rotation (degree)"),
            ),
            show_border=True,
            label="Plasee specify the initial value of following parameters:",
            visible_when='calibrationmode=="self"',
        ),
        HGroup(
            VGroup(
                Item("xdimension", label="x dimension (pixel)"),
                Item(
                    "xpixelsize",
                    label="Pixel size x (mm)",
                    visible_when='configmode == "normal"',
                ),
                Item(
                    "xpixelsizetem",
                    label="Pixel size x (A^-1)",
                    visible_when='configmode == "TEM"',
                ),
            ),
            VGroup(
                Item("ydimension", label="y dimension (pixel)"),
                Item(
                    "ypixelsize",
                    label="Pixel size y (mm)",
                    visible_when='configmode == "normal"',
                ),
                Item(
                    "ypixelsizetem",
                    label="Pixel size y (A^-1)",
                    visible_when='configmode == "TEM"',
                ),
            ),
            show_border=True,
            label="Please specify the dimension of detector"
            + " and size of pixel:",
            visible_when='calibrationmode=="self"',
        ),
        HGroup(
            VGroup(
                Item("xywidth", label="(x,y) center searching range, +/-"),
                Item("slice", label="Refining using slab along"),
            ),
            VGroup(
                Item("qmincali", label="Qmin in calibration"),
                Item("qmaxcali", label="Qmax in calibration"),
            ),
            show_border=True,
            label="Others",
            visible_when='calibrationmode=="self"',
        ),
        title="Calibration",
        width=600,
        height=450,
        resizable=True,
        buttons=[OKButton, CancelButton],
        handler=CalibrationHandler(),
        icon=ImageResource("icon.png"),
    )


def findFloat(line):
    pattern = r"[-+]?(?:\d+\.\d*|\.\d+|\d+)"
    return [float(x) for x in re.findall(pattern, line)]


if __name__ == "__main__":
    srxconfig = SrXconfig()
    cali = Calibration(srxconfig=srxconfig)
    # cali.callPyFAICalibration('ceo2.tif', 'ceo2.d')
    # cali.parsePyFAIoutput()
    cali.configure_traits(view="main_View")

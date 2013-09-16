dpx.pdfgetxgui

GUI for PDFgetX3

INSTALLATION

To install the dpx.pdfgetxgui package:

    python setup.py install

By default the files are installed in the system directories, which are
usually only writeable by the root.  See the usage info "./setup.py install --help" for options to install as a normal user under a different location.  Note that installation to non-standard directories you may require adjustments to the PATH and PYTHONPATH environment variables.

DEPENDENCIES

dpx.pdfgetxgui requires the following Python libraries,
diffpy.pdfgetx 
numpy, 
traits,
traitsui,
chaco
diffpy.confutils (included in diffpy.srxplanar)

if python version < 2.7 (these two packages are included in 2.7 but not in 2.6)
ordereddict  
argparse

We recommand to install EPD (Enthought Python Distribution)from http://www.enthought.com/ which include most of them by default. Besides EPD, PDFlive also require these packages:

packages from diffpy:
diffpy.srxplanar and diffpy.confutils (included in srxplanar):
svn+ssh://slapper.apam.columbia.edu/u24/local/svnrepos/trac/research/projects/13SrSig2D

------------------------------------------------------------------------------

For more information on dpx.pdfgetxgui, please email Prof. Simon Billinge at sb2896@columbia.edu

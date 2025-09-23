#!/usr/bin/env python
##############################################################################
#
# dpx.pdfgetxgui    by Simon J. L. Billinge group
#                   (c) 2012 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Xiaohao Yang
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

import os

import numpy as np
from traits.api import (
    Any,
    Array,
    Bool,
    Button,
    CFloat,
    CInt,
    DelegatesTo,
    Dict,
    Directory,
    Enum,
    Event,
    File,
    Float,
    HasTraits,
    Instance,
    Int,
    List,
    Property,
    Range,
    Str,
    cached_property,
    on_trait_change,
    property_depends_on,
)


class DataContainer(HasTraits):

    # The full path and file name of the file:
    fullname = File
    # The base file name of the source file:
    basename = Property  # Str

    @property_depends_on("fullname")
    def _get_basename(self):
        return os.path.basename(self.fullname)


if __name__ == "__main__":
    test = DataContainer()

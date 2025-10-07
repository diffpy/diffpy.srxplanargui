|Icon| |title|_
===============

.. |title| replace:: diffpy.srxplanargui
.. _title: https://diffpy.github.io/diffpy.srxplanargui

.. |Icon| image:: https://avatars.githubusercontent.com/diffpy
        :target: https://diffpy.github.io/diffpy.srxplanargui
        :height: 100px

|PythonVersion| |PR|

|CI| |Black| |Tracking|

.. |Black| image:: https://img.shields.io/badge/code_style-black-black
        :target: https://github.com/psf/black

.. |CI| image:: https://github.com/diffpy/diffpy.srxplanargui/actions/workflows/matrix-and-codecov-on-merge-to-main.yml/badge.svg
        :target: https://github.com/diffpy/diffpy.srxplanargui/actions/workflows/matrix-and-codecov-on-merge-to-main.yml

.. |Codecov| image:: https://codecov.io/gh/diffpy/diffpy.srxplanargui/branch/main/graph/badge.svg
        :target: https://codecov.io/gh/diffpy/diffpy.srxplanargui

.. |Forge| image:: https://img.shields.io/conda/vn/conda-forge/diffpy.srxplanargui
        :target: https://anaconda.org/conda-forge/diffpy.srxplanargui

.. |PR| image:: https://img.shields.io/badge/PR-Welcome-29ab47ff
        :target: https://github.com/diffpy/diffpy.srxplanargui/pulls

.. |PyPI| image:: https://img.shields.io/pypi/v/diffpy.srxplanargui
        :target: https://pypi.org/project/diffpy.srxplanargui/

.. |PythonVersion| image:: https://img.shields.io/pypi/pyversions/diffpy.srxplanargui
        :target: https://pypi.org/project/diffpy.srxplanargui/

.. |Tracking| image:: https://img.shields.io/badge/issue_tracking-github-blue
        :target: https://github.com/diffpy/diffpy.srxplanargui/issues

xPDFsuite, a software for PDF transformation and visualization.

GUI for diffpy.srxplanar

For more information about the diffpy.srxplanargui library, please consult our `online documentation <https://diffpy.github.io/diffpy.srxplanargui>`_.

Citation
--------

If you use diffpy.srxplanargui in a scientific publication, we would like you to cite this package as

        Yang, X., Juhas, P., Farrow, C. L., & Billinge, S. J. (2014).
        xPDFsuite: an end-to-end software solution for high throughput pair distribution function transformation,
        visualization and analysis. arXiv preprint arXiv:1402.3163.

Installation
------------

The preferred method is to be installed with ""xpdfsuite"" package or the wheel file.

If you prefer to install from sources, after installing the dependencies, obtain the source archive from
`GitHub <https://github.com/diffpy/diffpy.srxplanargui/>`_. Once installed, ``cd`` into your ``diffpy.srxplanargui`` directory
and run the following ::

        pip install .

This package also provides command-line utilities. To check the software has been installed correctly, type ::

        diffpy.srxplanargui --version

You can also type the following command to verify the installation. ::

        python -c "import diffpy.srxplanargui; print(diffpy.srxplanargui.__version__)"


To view the basic usage and available commands, type ::

        diffpy.srxplanargui -h

Support
----------------------

If you see a bug or want to request a feature, please `report it as an issue <https://github.com/diffpy/diffpy.srxplanargui/issues>`_ and/or `submit a fix as a PR <https://github.com/diffpy/diffpy.srxplanargui/pulls>`_.

Feel free to fork the project. To install diffpy.srxplanargui
in a development mode, with its sources being directly used by Python
rather than copied to a package directory, use the following in the root
directory ::

        pip install -e .

To ensure code quality and to prevent accidental commits into the default branch, please set up the use of our pre-commit
hooks.

1. Install pre-commit in your working environment by running ``conda install pre-commit``.

2. Initialize pre-commit (one time only) ``pre-commit install``.

Thereafter your code will be linted by black and isort and checked against flake8 before you can commit.
If it fails by black or isort, just rerun and it should pass (black and isort will modify the files so should
pass after they are modified). If the flake8 test fails please see the error messages and fix them manually before
trying to commit again.

Improvements and fixes are always appreciated.

Contact
-------

For more information on diffpy.srxplanargui please visit the project `web-page <https://diffpy.github.io/>`_ or email Simon Billinge at sb2896@columbia.edu.

Acknowledgements
----------------

``diffpy.srxplanargui`` is built and maintained with `scikit-package <https://scikit-package.github.io/scikit-package/>`_.

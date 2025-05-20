# setup.py
from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    name='simulate_core',
    ext_modules=cythonize("simulate_core.pyx", language_level=3),
    include_dirs=[numpy.get_include()],
)

#!/usr/bin/env python

from distutils.core import setup, Extension

module1 = Extension('fract4d',
                    sources = ['fract4dmodule.c', 'cmap.c' ])

setup (name = 'fract4d',
       version = '1.0',
       description = 'A module for calling fractal functions built on-the-fly by Gnofract4D',
       ext_modules = [module1])
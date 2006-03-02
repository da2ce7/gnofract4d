#!/usr/bin/env python

# suppress annoying message during tests we get otherwise
import warnings
warnings.filterwarnings(
    "ignore",
    ".*UIManager.*",
    DeprecationWarning,
    ".*",
    0)

import unittest
import test_gtkfractal
import test_undo
import test_model
import test_preferences
import test_fourway
import test_angle
import test_hig
import test_browser
import test_main_window
import test_settings
import test_painter
import test_colors
import test_fract4dguic

def suite():
    tests = (
        test_gtkfractal.suite(),
        test_undo.suite(),
        test_model.suite(),
        test_preferences.suite(),
        test_fourway.suite(),
        test_angle.suite(),
        test_hig.suite(),
        test_browser.suite(),
        test_settings.suite(),
        test_painter.suite(),
        test_colors.suite(),
        test_fract4dguic.suite(),
        test_main_window.suite())
    return unittest.TestSuite(tests)

def main():
    unittest.main(defaultTest='suite')
    
if __name__ == '__main__':
    main()


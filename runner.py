from curses import wrapper
from sys import path as sys_path
from os import path as os_path

dir_path = os_path.dirname(os_path.realpath(__file__))
sys_path.insert(0, dir_path)

from ep_regression_curses.gui import RegressionGUI  # noqa

wrapper(RegressionGUI.wrapper_function)

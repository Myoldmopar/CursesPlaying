import curses
from ep_regression_curses.enums import ColorPairs, WindowState
from time import sleep
from pyfiglet import Figlet


class RegressionGUIInstance(object):

    def __init__(self, main_window):
        # store the highest level main window instance from curses
        self.main_window = main_window
        # curses view windows
        self.title_window = None
        self.content_window = None
        self.navigation_window = None
        self.status_window = None
        # status variables
        self.screen_width = None
        self.screen_height = None
        self.content_state = WindowState.SETTINGS  # always start on the settings window

    @staticmethod
    def initialize_curses():
        curses.curs_set(False)
        curses.init_pair(ColorPairs.REGULAR, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(ColorPairs.ALERT, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(ColorPairs.BORDER, curses.COLOR_BLACK, curses.COLOR_BLACK)

    def create_initial_windows(self):
        self.title_window = curses.newwin(2, self.screen_width, 0, 0)
        self.content_window = curses.newwin(8, self.screen_width, 2, 0)
        self.navigation_window = curses.newwin(1, self.screen_width, 16, 0)
        self.status_window = curses.newwin(1, self.screen_width, 18, 0)

    def draw_title_bar(self):
        self.title_window.clear()
        self.title_window.addstr(0, 0, 'The Curses of the EnergyPlus Regression Tool')
        self.title_window.refresh()

    def draw_content_window(self):
        self.content_window.clear()
        if self.content_state == WindowState.SETTINGS:
            self.content_window.addstr(0, 0, "SETTINGS SCREEN", curses.A_REVERSE)
        elif self.content_state == WindowState.FILE_SELECTION:
            self.content_window.addstr(0, 0, "FILE SELECTION SCREEN", curses.A_REVERSE)
        elif self.content_state == WindowState.LOG_MESSAGES:
            self.content_window.addstr(0, 0, "LOG MESSAGES", curses.A_REVERSE)
        elif self.content_state == WindowState.LAST_RUN_SUMMARY:
            self.content_window.addstr(0, 0, "LAST RUN SUMMARY", curses.A_REVERSE)
        else:
            self.content_window.addstr(0, 0, "UNKNOWN KEY PRESSED", curses.color_pair(1))
        self.content_window.refresh()

    def draw_navigation_bar(self):
        self.navigation_window.clear()
        navigation_entries = [
            "Settings:       F5  ",
            "File Selection: F6  ",
            "Run Results:    F7  ",
            "Log Messages:   F8  ",
            "Quit Program:    Q  ",
        ]
        for i, navigation_entry in enumerate(navigation_entries):
            self.navigation_window.addstr(0, 25 * i, navigation_entry, curses.color_pair(ColorPairs.REGULAR))
            if i < len(navigation_entries) - 1:
                self.navigation_window.addstr(0, 25 * i + 20, " ||| ", curses.color_pair(ColorPairs.REGULAR))
        self.navigation_window.refresh()

    def draw_status_bar(self):
        self.status_window.clear()
        self.status_window.addstr(0, 0, "Status updates here")
        self.status_window.refresh()

    def draw_gui(self):
        self.main_window.clear()
        self.main_window.refresh()
        self.draw_title_bar()
        self.main_window.hline(1, 0, curses.ACS_HLINE, self.screen_width)
        self.draw_content_window()
        self.main_window.hline(15, 0, curses.ACS_HLINE, self.screen_width)
        self.draw_navigation_bar()
        self.main_window.hline(17, 0, curses.ACS_HLINE, self.screen_width)
        self.draw_status_bar()

    def do_splash(self):
        splash_text_rendered = Figlet().renderText('Regression Tool')
        lines_of_rendered_text = splash_text_rendered.strip().split('\n')
        required_rows_count = len(lines_of_rendered_text)
        required_columns_count = max([len(x) for x in lines_of_rendered_text])
        splash_window = curses.newwin(required_rows_count + 2, required_columns_count + 2, 3, 4)
        splash_window.addstr(1, 1, splash_text_rendered, ColorPairs.ALERT)
        splash_window.border()
        splash_window.refresh()
        sleep(2)

    def run_gui(self):
        # get the initial values of these, though they are free to update over time
        self.screen_height, self.screen_width = self.main_window.getmaxyx()

        # initialize the curses stuff, then program specific stuff
        self.initialize_curses()

        # create the initial windows, they will have to be adjusted as the program runs to account for various things
        self.create_initial_windows()

        # run the splash screen exercise
        self.do_splash()

        # start the main loop waiting on getch
        self.draw_gui()
        while True:
            key_pressed = self.main_window.getch()
            self.main_window.clear()
            if key_pressed == curses.KEY_F5:
                self.content_state = WindowState.SETTINGS
            elif key_pressed == curses.KEY_F6:
                self.content_state = WindowState.FILE_SELECTION
            elif key_pressed == curses.KEY_F7:
                self.content_state = WindowState.LAST_RUN_SUMMARY
            elif key_pressed == curses.KEY_F8:
                self.content_state = WindowState.LOG_MESSAGES
            elif key_pressed in (ord('q'), ord('Q')):
                break
            else:
                pass  # display_unknown_key(stdscr, key_pressed)
            self.draw_gui()


def wrapper_function(main_curses_window):
    r_gui = RegressionGUIInstance(main_curses_window)
    r_gui.run_gui()


curses.wrapper(wrapper_function)

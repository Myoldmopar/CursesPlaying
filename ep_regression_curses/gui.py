import curses
from ep_regression_curses.enums import ColorPairs, WindowState, KNOWN_UNSUPPORTED_KEYS
from time import sleep
from pyfiglet import Figlet


class RegressionGUI(object):

    def __init__(self, main_window):
        # fixed value parameters
        self.minimum_size = (19, 120)
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
        self.status_message = 'Status messages show up here'

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

    def do_splash(self):
        self.main_window.clear()
        self.main_window.refresh()
        splash_text_rendered = Figlet().renderText('Regression Tool')
        lines_of_rendered_text = splash_text_rendered.split('\n')
        lines_of_rendered_text = [x for x in lines_of_rendered_text if x]
        required_rows_count = len(lines_of_rendered_text)
        required_columns_count = max([len(x) for x in lines_of_rendered_text])
        starting_column = int((self.screen_width - required_columns_count - 2) / 2)
        starting_row = int((self.screen_height - required_rows_count - 2) / 2)
        splash_window = curses.newwin(
            required_rows_count + 2, required_columns_count + 2, starting_row, starting_column
        )
        splash_window.clear()
        for line_num, line in enumerate(lines_of_rendered_text):
            splash_window.addstr(line_num + 1, 1, line, ColorPairs.ALERT)
        splash_window.border()
        splash_window.refresh()
        sleep(3)

    def draw_title_bar(self):
        self.title_window.clear()
        self.title_window.addstr(0, 0, 'The Curses of the EnergyPlus Regression Tool')
        self.title_window.refresh()

    def draw_content_window(self):
        self.content_window.clear()
        # add a header line to row zero
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
        # then add dashes to debug and check window sizing, etc.
        content_window_size = self.content_window.getmaxyx()
        for row in range(content_window_size[0] - 2):
            self.content_window.addstr(row + 1, 0, "-" * content_window_size[1], curses.A_REVERSE)
            self.content_window.refresh()
        self.content_window.refresh()

    def draw_navigation_bar(self):
        self.navigation_window.clear()
        navigation_entries = [
            "  Settings:   F5  ",
            " File Listing: F6 ",
            " Run Results:  F7 ",
            " Log Messages: F8 ",
            " Quit Program:  Q ",
        ]
        for i, navigation_entry in enumerate(navigation_entries):
            self.navigation_window.addstr(0, 25 * i, navigation_entry, curses.color_pair(ColorPairs.REGULAR))
            if i < len(navigation_entries) - 1:
                self.navigation_window.addstr(0, 25 * i + 20, "|||    ", curses.A_NORMAL)
        self.navigation_window.refresh()

    def draw_status_bar(self):
        self.status_window.clear()
        self.status_window.addstr(0, 1, self.status_message)
        self.status_window.refresh()

    def draw_gui(self):
        # the row numbers here need to be dynamic based on the screen height
        # the minimum screen height is enforced elsewhere, and the screen size variables are updated elsewhere also

        # clean up any prior window stuff
        self.main_window.clear()
        self.main_window.refresh()

        # resize/move the content and other windows
        # the title window will always be the top row, so no need to do anything there
        # the content window will need to be resized, and I don't see a resize method, so I'll just recreate it? Ugh.
        # the navigation and status windows are just one-liners so they just need to be moved
        self.content_window = curses.newwin(self.screen_height - 5, self.screen_width, 2, 0)
        self.navigation_window.mvwin(self.screen_height - 3, 0)
        self.status_window.mvwin(self.screen_height - 1, 0)

        # redraw the windows and separators
        self.draw_title_bar()
        self.main_window.hline(1, 0, curses.ACS_HLINE, self.screen_width)
        self.draw_content_window()
        self.main_window.hline(self.screen_height - 4, 0, curses.ACS_HLINE, self.screen_width)
        self.draw_navigation_bar()
        self.main_window.hline(self.screen_height - 2, 0, curses.ACS_HLINE, self.screen_width)
        self.draw_status_bar()

    def handle_resize(self, initial_call=False):
        """
        This function will get the current window size, and if it isn't big enough to show the content, then it
        pauses program display, alerting the user that they need to resize their terminal.
        
        :param initial_call: If True, the status bar is _not_ updated with the updated size
        :return: 
        """
        # get the initial values of these, though they are free to update over time
        self.screen_height, self.screen_width = self.main_window.getmaxyx()
        if not initial_call:
            # update the status bar if the program is re-sized during normal use
            self.status_message = 'Current height = ' + str(self.screen_height) + ' rows; '
            self.status_message += 'Current width = ' + str(self.screen_width) + ' columns'

        while self.screen_height < self.minimum_size[0] or self.screen_width < self.minimum_size[1]:
            self.main_window.clear()
            self.main_window.addstr(
                1, 1, 'Screen too small, must be at least %s rows and %s columns' % self.minimum_size
            )
            action = self.main_window.getch()
            if action == curses.KEY_RESIZE:
                self.screen_height, self.screen_width = self.main_window.getmaxyx()

    def run_gui(self):
        # do an initial check on the size of the screen here, if the screen is too small it will wait for the user
        self.handle_resize(initial_call=True)

        # initialize the curses stuff, then program specific stuff
        self.initialize_curses()

        # create the initial windows, they will have to be adjusted as the program runs to account for various things
        self.create_initial_windows()

        # run the splash screen exercise
        self.do_splash()

        # there's a chance the program was re-sized during the splash no events were caught, so recheck the size
        self.handle_resize(initial_call=True)

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
            elif key_pressed == curses.KEY_RESIZE:
                self.handle_resize()
            elif key_pressed in (ord('q'), ord('Q')):
                break
            else:
                if key_pressed <= 126:
                    probably = ' (Probably the %s key' % chr(key_pressed) + ')'
                elif key_pressed in KNOWN_UNSUPPORTED_KEYS:
                    probably = ' (Probably the %s key' % KNOWN_UNSUPPORTED_KEYS[key_pressed] + ')'
                else:
                    probably = ''
                self.status_message = 'Unknown key pressed, code = \"' + str(key_pressed) + '\"' + probably
            self.draw_gui()

    @staticmethod
    def wrapper_function(main_curses_window):
        r_gui = RegressionGUI(main_curses_window)
        r_gui.run_gui()

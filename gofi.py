import gi
import os
import optparse
import logging

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk, Gdk  # NOQA


class MainWindow(Gtk.Window):

    def __init__(self, width=600, max_height=600):
        logging.debug("MainWindow init")
        Gtk.Window.__init__(self, title="gofi")

        self.set_decorated(False)
        self.set_default_size(width, max_height)
        self.set_resizable(False)
        self.set_name("Gofi")

        # Widgets
        self.prompt = Gtk.Label(label="Launch:")
        self.textbox = Gtk.Entry()

        self.listview = Gtk.ListBox()
        self.listview.set_name("listview")

        """
        win
          box_layout
            box_inputbar
              prompt
              textbox
            box_listview
              { list children ... }
        """
        # Layout
        self.box_layout = Gtk.Box(spacing=0, orientation=Gtk.Orientation.VERTICAL)
        self.add(self.box_layout)

        self.box_inputbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.box_layout.pack_start(self.box_inputbar, expand=False, fill=False, padding=0)
        self.box_layout.pack_start(self.listview, expand=True, fill=True, padding=0)

        self.box_inputbar.pack_start(self.prompt, expand=False, fill=False, padding=16)
        self.box_inputbar.pack_start(self.textbox, expand=True, fill=True, padding=16)

        self.show_all()
        self.textbox.grab_focus()


"""
class Entry(Gtk.ListBoxRow):
    def __init__(self, data):
        super(Gtk.ListBoxRow, self).__init__()
        self.data = data
        # TODO: Add icon if enabled

        self.wrapper = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        self.wrapper.set_halign(Gtk.Align.START)

        self.label = Gtk.Label(data)
        self.label.set_justify(Gtk.Justification.LEFT)

        self.wrapper.pack_start(self.label, True, True, 0)

        css_ctx = self.wrapper.get_style_context()
        css_ctx.add_class("row")

        self.add(self.wrapper)
"""


class ListEntry(Gtk.ListBoxRow):
    def __init__(self, data):
        self.data = data
        super().__init__()
        # super().__init__(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        # TODO: Add icon if enabled

        self.box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        self.box.set_halign(Gtk.Align.START)

        self.label = Gtk.Label(label=data)
        self.label.set_justify(Gtk.Justification.LEFT)

        self.box.pack_start(self.label, True, True, 0)

        row_css = self.get_style_context()
        row_css.add_class("row")

        label_css = self.label.get_style_context()
        label_css.add_class("label")

        self.add(self.box)


class App():
    """
    Show on top when called
        Reserve key-combination
    Run in background?
        App indicator?
    Styling engine w/css

    Save all executions in a data object that's pickledd
      Load this object and use it to sort by num execs so that
      favorite apps get to the top
    """
    GOFI_DATA_DIR = os.path.dirname(os.path.realpath(__file__))
    DEFAULT_NUM__ROWS = 20
    DEFAULT_STYLE = b"""
        * {
            font: 12px Operator Mono Book;
            background-color: #3c3836;
        }

        GtkWindow {
            padding: 8px;
        }

        #listview {
            margin: 0px 0px 0px 0px;
            border: solid 2px blue;
        }

        .row {
            margin: 0px;
            padding: 0px;
        }

        .label {
            margin: 0px 0px 0px 0px;
            padding: 0px 0px 0px 0px;
            color: #ffffff;
            border: solid 1px red;
            font-size: 20px;
        }
    """

    def __init__(self, options, args):
        logging.debug("Starting")

        self.win = MainWindow()
        self.win.connect("destroy", self.quit)
        self.win.connect("key-press-event", self.on_key_pressed)

        self.app_info = {}    # id -> info dict
        self.app_search = {}  # keywords -> id
        apps = Gio.DesktopAppInfo.get_all()

        for app in apps:
            _app_info = {
                "name": app.get_name(),
                "display_name": app.get_display_name(),
                "description": app.get_description(),
                "filename": app.get_filename(),
                "executable": app.get_executable(),
                "command": app.get_commandline(),
                "show": app.get_show_in(),
                "nodisplay": app.get_nodisplay(),
                "icon": app.get_icon(),
                "keywords": app.get_keywords(),
            }

            _app_search = self.extract_search_strings(_app_info)

            self.app_info[app.get_id()] = _app_info
            self.app_search[_app_search] = app.get_id()

            # TODO should use a bound model instead
            _widget = ListEntry(_app_info["display_name"])
            self.win.listview.add(_widget)

        logging.debug(f"Fetched {len(self.app_info)} entries")
        self.win.listview.show_all()

        calc_row_size = _widget.size_request()
        logging.debug(self.win.listview.size_request().height)
        logging.debug(self.win.listview.size_request().width)

        logging.debug(calc_row_size.height)
        logging.debug(calc_row_size.width)

    def _style(self, style=DEFAULT_STYLE):
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(style)

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def extract_search_strings(self, info):
        return info["description"]

    def on_key_pressed(self, window, event):
        logging.debug(f"Key press event {event}")
        key = event.keyval
        key_name = Gdk.keyval_name(key)
        state = event.state
        # ctrl = (state & Gdk.CONTROL_MASK)
        ctrl = False
        logging.debug(f"key={key}, key_name={key_name}, state={state}, ctrl={ctrl}")

        if key_name == "Escape":
            self.quit()

    def quit(self, args={}):
        logging.debug("Exiting")
        Gtk.main_quit()

    def run(self):
        return True


parser = optparse.OptionParser()
parser.add_option("-d", "--debug", action="store_true", help="Debug logging")

options, args = parser.parse_args()

if options.debug:
    log_level = logging.DEBUG
else:
    log_level = logging.WARNING

log_level = logging.DEBUG
logging.basicConfig(level=log_level, format="%(asctime)-15s [%(levelname)s] (%(threadName)-10s) %(message)s")

if __name__ == "__main__":
    gofi = App(options, args)
    gofi._style()
    Gtk.main()
    gofi.run()

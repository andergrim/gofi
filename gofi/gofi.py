#!/usr/bin/env python3
import gi
import os
import optparse
import gui
import objects
import logging

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk, Gdk, GObject  # NOQA


class Gofi():
    GOFI_DATA_DIR = os.path.dirname(os.path.realpath(__file__))
    DEFAULT_NUM_ROWS = 20
    DEFAULT_STYLE = b"""
        * {
            font: 12px Operator Mono Book;
            background-color: #3c3836;
        }

        GtkWindow {
            padding: 8px 8px 0px 8px;
        }

        .inputbar {
            border-bottom: solid 4px #458588;
        }

        entry, entry:focus {
            border: 0px;
            box-shadow: none;
        }

        #listview {
            margin: 0px 0px 0px 0px;
            /* border: solid 2px blue; */
        }

        .row {
            margin: 0px;
            padding: 0px;
        }

        .row > *, .row > * > * {
            background: none;
        }

        .row:selected, .row:selected > *, .row:selected > * > * {
            background-color: #ffffff;
            color: #000000;
        }

        overshoot.top,
        overshoot.right,
        overshoot.bottom,
        overshoot.left {
            background: none;
            border: none;
        }

        undershoot.top,
        undershoot.right,
        undershoot.bottom,
        undershoot.left {
            background: none;
            border: none;
        }

        .label {
            margin: 0px 0px 0px 0px;
            padding: 0px 0px 0px 0px;
            color: #ffffff;
            /* border: solid 1px red; */
            font-size: 20px;
        }
    """

    def __init__(self, options, args):
        logging.debug("Starting")

        self.win = gui.MainWindow()
        self.win.connect("destroy", self.quit)
        self.win.connect("key-press-event", self.on_key_pressed)
        self.win.textbox.connect("changed", self.on_change_input)
        self.history = objects.History(self.GOFI_DATA_DIR)
        self.search_string = None

        # Create a master lookup list, id: <App GObject>
        self.apps = {a.get_id(): a for a in Gio.DesktopAppInfo.get_all()}

        # Create list stores, one master and one to represent the current filter
        self.application_list_base = Gio.ListStore().new(objects.Application)
        self.application_list = Gio.ListStore().new(objects.Application)

        for app in self.apps.values():
            popularity, last_use = self.history.entries.get(app.get_id(), (0, 0))
            self.application_list_base.append(objects.Application(app, popularity, last_use))

        # TODO: Sort entries by score based on timestamp, popularity, visibility
        self.application_list_base.sort(lambda x, y: y.last_use - x.last_use)

        logging.debug(f"Fetched {len(self.application_list_base)} entries")

        self._reset()

    def _reset(self):
        # i = 0
        self.application_list = Gio.ListStore().new(objects.Application)
        for app in self.application_list_base:
            if app.visibility > 1:
                # if i < self.DEFAULT_NUM_ROWS:
                self.application_list.append(app)
                # i += 1

        self.win.listview.bind_model(self.application_list, self._add_row)
        self.win.listview.select_row(self.win.listview.get_children()[0])
        self.win.listview.show_all()

    def _search(self, search_string):
        logging.debug(search_string)
        if not search_string:
            # self.application_list = self._reset()[0:self.DEFAULT_NUM_ROWS]
            pass
        else:
            self.application_list.sort(self._search_compare, search_string)
            self.win.listview.select_row(self.win.listview.get_children()[0])
            self.win.listview.show_all()

    def _search_compare(self, app_a, app_b, token):
        return app_b.match(token) - app_a.match(token)

    def _add_row(self, data):
        logging.debug(f"Populating list: {data.app_id} ({data.popularity}, {data.last_use})")
        return gui.ListEntry(data.display_name)

    def _style(self, style=DEFAULT_STYLE):
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(style)

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_change_input(self, widget):
        if widget.get_text() != "":
            self._search(widget.get_text())
        else:
            self._reset()

    def on_key_pressed(self, window, event):
        # logging.debug(f"Key press event {event}")
        key = event.keyval
        key_name = Gdk.keyval_name(key)
        # state = event.state
        # logging.debug(f"key={key}, key_name={key_name}, state={state}")

        if key_name == "Escape":
            if self.win.textbox.get_text() == "":
                self.quit()
            else:
                self.win.textbox.set_text("")
        elif key_name in ["Return", "KP_Enter"]:
            self.execute()
        elif key_name == "Down":
            index = self.win.listview.get_selected_row().get_index()
            self.win.listview.select_row(self.win.listview.get_row_at_index(index + 1))
        elif key_name == "Up":
            index = self.win.listview.get_selected_row().get_index()
            if index > 0:
                self.win.listview.select_row(self.win.listview.get_row_at_index(index - 1))

    def execute(self, **kwargs):
        index = self.win.listview.get_selected_row().get_index()
        app = self.application_list.get_item(index)
        if app:
            logging.debug(f"Launching {app}")
            self.history.update(app)
            launch_context = Gio.AppLaunchContext()
            self.apps[app.app_id].launch(None, launch_context)
            self.quit()

    def quit(self, args={}):
        logging.debug("Exiting")
        Gtk.main_quit()

    def run(self):
        """
        Application loop
        """
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
    gofi = Gofi(options, args)
    gofi._style()
    Gtk.main()
    gofi.run()

#!/usr/bin/env python3
import gi
from gui import MainWindow, ListEntry
from objects import History, Application
from config import Config
import logging

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk, Gdk, GObject  # NOQA

config = Config()


class Gofi():

    def __init__(self, options, args):
        logging.debug("Starting")

        self.win = MainWindow()

        self.win.connect("destroy", self.quit)
        self.win.connect("key-press-event", self.on_key_pressed)
        self.win.textbox.connect("changed", self.on_change_input)
        self.history = History(config.GOFI_DATA_DIR)
        self.search_string = None

        # Create a master lookup list, id: <App GObject>
        self.apps = {a.get_id(): a for a in Gio.DesktopAppInfo.get_all()}

        # Create list stores, one master and one to represent the current filter
        self.application_list_base = Gio.ListStore().new(Application)
        self.application_list = Gio.ListStore().new(Application)

        for app in self.apps.values():
            popularity, last_use = self.history.entries.get(app.get_id(), (0, 0))
            self.application_list_base.append(Application(app, popularity, last_use))

        # TODO: Sort entries by score based on timestamp, popularity, visibility
        self.application_list_base.sort(lambda x, y: y.last_use - x.last_use)

        logging.debug(f"Fetched {len(self.application_list_base)} entries")

        self._reset()

    def _reset(self):
        self.application_list = Gio.ListStore().new(Application)
        for app in self.application_list_base:
            if app.visibility > 1:
                self.application_list.append(app)

        self.win.listview.bind_model(self.application_list, self._add_row)
        self.win.listview.select_row(self.win.listview.get_children()[0])
        self.win.listview.show_all()

    def _search(self, search_string):
        logging.debug(search_string)
        if not search_string:
            pass
        else:
            self.application_list.sort(self._search_compare, search_string)
            self.win.listview.select_row(self.win.listview.get_children()[0])
            self.win.listview.show_all()

    def _search_compare(self, app_a, app_b, token):
        logging.debug(f"Compare {app_b} - {app_a}")
        res = app_b.match(token) - app_a.match(token)
        logging.debug(f"   {res}")
        return res

    def _add_row(self, data):
        # logging.debug(f"Populating list: {data.app_id} ({data.popularity}, {data.last_use})")
        if config.DEFAULT_SHOW_ICONS:
            icon = data.icon
        else:
            icon = None

        return ListEntry(data.display_name, icon)

    def _style(self, style=config.DEFAULT_STYLE):
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


if __name__ == "__main__":
    gofi = Gofi(None, None)
    gofi._style()
    Gtk.main()
    gofi.run()

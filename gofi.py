#!/usr/bin/env python3
import gi
import os
import pickle
import optparse
from time import time
import logging

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk, Gdk, GObject  # NOQA


class History():
    def __init__(self, home):
        self.filename = os.path.join(home, ".gofi_history")
        self.entries = self._get()

    def _save(self):
        try:
            with open(self.filename, "wb") as fh:
                pickle.dump(self.entries, fh)
        except Exception as e:
            logging.error(f"Could not save history file {self.filename}: {e}")

    def _get(self):
        try:
            with open(self.filename, "rb") as fh:
                entries = pickle.load(fh)
        except Exception as e:
            logging.error(f"Could not get history from {self.filename}: {e}")
            return {}

        logging.debug(entries)
        return entries

    def update(self, app):
        app_id = app.app_id
        logging.debug(f"History update {app_id}")
        if not self.entries.get(app_id):
            num = 0
        else:
            num = self.entries[app_id][0]

        self.entries[app_id] = (num + 1, round(time()))
        self._save()


class Application(GObject.GObject):
    app_id = GObject.Property(type=str)
    name = GObject.Property(type=str)
    display_name = GObject.Property(type=str)
    icon = GObject.Property(type=str)
    search_string = GObject.Property(type=str)
    popularity = GObject.Property(type=int)  # Number or uses
    last_use = GObject.Property(type=int)    # Timestamp
    visibility = GObject.Property(type=int)  # 0-2, with 2 being normal

    def __init__(self, app, popularity=0, last_use=0):
        GObject.GObject.__init__(self)
        self.app_id = app.get_id()
        self.name = app.get_name()
        self.display_name = app.get_display_name()
        self.icon = app.get_icon()
        self.search_string = self._extract_search_strings(app)
        self.popularity = popularity
        self.last_use = last_use
        self.visibility = app.get_show_in() + (not app.get_nodisplay())

    def _extract_search_strings(self, app):
        # TODO: Perform some filtering, discarding non alphanumerics
        searchable = set()
        searchable.add(app.get_display_name().lower())
        searchable.add(app.get_name().lower())

        for kw in app.get_keywords():
            searchable.add(kw.lower())

        executable = app.get_executable()
        if executable:
            searchable.add(executable.split(" ", 1)[0].lower())

        searchable_string = " ".join(searchable)
        return searchable_string

    def match(self, token):
        token = token.lower()
        score = (self.search_string.startswith(token) * len(token)) + \
                (self.search_string.count(token))
        logging.debug(f"{self.name}: {score}")
        return score

    def __str__(self):
        return str(f"{self.name} ({self.app_id})")


class MainWindow(Gtk.Window):

    def __init__(self, width=400, max_height=400):
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
        self.listview.set_selection_mode(Gtk.SelectionMode.BROWSE)

        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        self.scroll.add(self.listview)

        # Layout
        self.box_layout = Gtk.Box(spacing=0, orientation=Gtk.Orientation.VERTICAL)
        self.add(self.box_layout)

        self.box_inputbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.box_layout.pack_start(self.box_inputbar, expand=False, fill=False, padding=0)
        # self.box_layout.pack_start(self.listview, expand=True, fill=True, padding=0)
        self.box_layout.pack_start(self.scroll, expand=True, fill=True, padding=0)

        self.box_inputbar.pack_start(self.prompt, expand=False, fill=False, padding=16)
        self.box_inputbar.pack_start(self.textbox, expand=True, fill=True, padding=16)
        input_css = self.box_inputbar.get_style_context()
        input_css.add_class("inputbar")

        self.show_all()
        self.textbox.grab_focus()


class ListEntry(Gtk.ListBoxRow):
    def __init__(self, label, icon=None):
        super().__init__()

        self.box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        self.box.set_halign(Gtk.Align.START)

        self.label = Gtk.Label(label=label)
        self.label.set_justify(Gtk.Justification.LEFT)

        self.box.pack_start(self.label, True, True, 0)

        row_css = self.get_style_context()
        row_css.add_class("row")

        label_css = self.label.get_style_context()
        label_css.add_class("label")

        self.set_selectable(True)
        self.set_can_focus(False)
        self.add(self.box)


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

        self.win = MainWindow()
        self.win.connect("destroy", self.quit)
        self.win.connect("key-press-event", self.on_key_pressed)
        self.win.textbox.connect("changed", self.on_change_input)
        self.history = History(self.GOFI_DATA_DIR)
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
        # i = 0
        self.application_list = Gio.ListStore().new(Application)
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
        return ListEntry(data.display_name)

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

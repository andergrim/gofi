import gi
import logging

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # NOQA


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

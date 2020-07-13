import gi
import os
import pickle
import logging
# from utils import lratio
from time import time

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gio  # NOQA


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
    app_id = GObject.Property(type=GObject.TYPE_STRING)
    name = GObject.Property(type=GObject.TYPE_STRING)
    display_name = GObject.Property(type=GObject.TYPE_STRING)
    icon = GObject.Property(type=GObject.TYPE_OBJECT)
    search_string = GObject.Property(type=GObject.TYPE_PYOBJECT)
    popularity = GObject.Property(type=GObject.TYPE_INT)  # Number or uses
    last_use = GObject.Property(type=GObject.TYPE_INT)    # Timestamp
    visibility = GObject.Property(type=GObject.TYPE_INT)  # 0-2, with 2 being normal

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

    def _extract_search_strings_old(self, app):
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

    def _extract_search_strings(self, app):
        search_strings = [s.lower() for s in app.get_display_name().split(" ")]
        logging.debug(search_strings)
        return search_strings

    def match(self, token):
        score = 0
        token = token.lower()

        search_string = " ".join(self.search_string)
        score = (search_string.startswith(token) * len(token)) + \
                (search_string.count(token))

        # score = (search_string.startswith(token) * len(token)) + \
        #         (search_string.count(token)) / len(self.search_string)

        # for search_part in self.search_string:
        #     score += lratio(search_part, token) * 5
        return score

    def __str__(self):
        return str(f"{self.name} ({self.app_id})")

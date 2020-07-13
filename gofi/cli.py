#!/usr/bin/env python3
import optparse
import gi
import logging
from gofi import Gofi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # NOQA


def main():
    """
    TODO: Load config here and pass it on
    """
    parser = optparse.OptionParser()
    parser.add_option("-d", "--debug", action="store_true", help="Debug logging")

    options, args = parser.parse_args()

    if options.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level, format="%(asctime)-15s [%(levelname)s] (%(threadName)-10s) %(message)s")

    gofi = Gofi(options, args)
    gofi._style()
    Gtk.main()
    gofi.run()


log_level = logging.DEBUG
if __name__ == "__main__":
    main()

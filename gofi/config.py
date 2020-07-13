import os


class Config:

    GOFI_DATA_DIR = os.path.dirname(os.path.realpath(__file__))
    DEFAULT_SHOW_ICONS = True
    DEFAULT_NUM_ROWS = 20
    DEFAULT_STYLE = b"""
        * {
            font: 18px Operator Mono Book;
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
            padding: 2px 0px 2px 4px;
            margin: 0px;
        }

        .row > *, .row > * > * {
            background: none;
        }

        .row:selected, .row:selected > *, .row:selected > * > * {
            background-color: #ebdbb2;
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
            color: #cccccc;
            font-size: 18px;
        }
    """

    def __init__(self):
        pass

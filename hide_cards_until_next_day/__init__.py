#!/usr/bin/env python

from aqt import mw
from aqt.qt import *
from anki.hooks import addHook
from aqt.utils import getText, showInfo
from anki.lang import _
# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *
from anki import Collection

# import constant
# from anki.consts import QUEUE_TYPE_MANUALLY_BURIED, QUEUE_TYPE_LRN
from anki.consts import QUEUE_TYPE_MANUALLY_BURIED
from aqt import gui_hooks
# from time import time_ns

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

# LUCAS_TAG = "z.lucas_tag_hidden."


# def time_marker() -> str:
#     return str(time_ns())


# def lucas_tag() -> str:
#     return f'{LUCAS_TAG}{time_marker()}'


def bury_custom_cards_lucas(*args, **kargs) -> None:
    ids = mw.col.find_cards("is:new -is:suspended added:1")
    # mw.col.tags.bulkAdd(ids, lucas_tag())
    for id in ids:
        card = mw.col.getCard(id)
        card.queue = QUEUE_TYPE_MANUALLY_BURIED
        card.flush()
    mw.reset()


# def unbury_custom_cards_lucas(*args, **kargs) -> None:
#     tag = lucas_tag()
#     ids = mw.col.find_cards(f'tag:"{LUCAS_TAG}*" -is:new')
#     mw.col.tags.bulkRem(ids, lucas_tag())
#     for id in ids:
#         card = mw.col.getCard(id)
#         card.queue = QUEUE_TYPE_LRN
#         card.flush()
#         note = card.note()
#         note.rem
#     mw.reset()


def lucas_main(*args, **kargs) -> None:
    bury_custom_cards_lucas()
    # unbury_custom_cards_lucas()


# execute when overview refresh
# gui_hooks.overview_did_refresh.append(testFunction)
# gui_hooks.deck_browser_will_render_content.append(testFunction)
gui_hooks.add_cards_did_add_note.append(lucas_main)
# create a new menu item, "test"
action = QAction("Organizar Cartões", mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, lucas_main)
# and add it to the tools menu
mw.form.menuTools.addAction(action)

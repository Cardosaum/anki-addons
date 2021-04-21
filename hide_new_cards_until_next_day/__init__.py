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
from anki.consts import QUEUE_TYPE_MANUALLY_BURIED
from aqt import gui_hooks
from datetime import datetime
from time import time_ns
import re

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.
MARKER_SEP = '_'
MARKER_TAG_BASE = 'zTagHidden' + MARKER_SEP
REGEX_TAG = re.compile(f'^{MARKER_TAG_BASE}')


def marker_today():
    d = datetime.fromtimestamp(time_ns()//10**9)
    d = datetime(d.year, d.month, d.day, 0)
    return d


def marker_tag() -> str:
    return f'{MARKER_TAG_BASE}{marker_today().strftime("%Y-%m-%d")}'


def is_marker_tag_from_today(tag: str) -> bool:
    if tag != marker_tag():
        return False
    return True


def remove_mark_tags(note, tags: list) -> None:
    for tag in tags:
        if is_marker_tag_from_today(tag):
            continue
        if REGEX_TAG.search(tag):
            note.delTag(tag)


def custom_bury_cards(*args, **kargs) -> None:
    ids = mw.col.find_cards("is:new -is:suspended added:1")
    mw.col.sched.suspendCards(ids)
    for i in ids:
        card = mw.col.getCard(i)
        note = card.note()
        note.addTag(marker_tag())
        note.flush()
    mw.reset()


def custom_unbury_cards(*args, **kargs) -> None:
    ids = mw.col.find_cards(f'tag:"{MARKER_TAG_BASE}*"')
    for i in ids:
        card = mw.col.getCard(i)
        note = card.note()
        remove_mark_tags(note, note.tags)
        note.flush()
        suspend_note = True
        for tag in note.tags:
            if is_marker_tag_from_today(tag):
                suspend_note = False
        if suspend_note:
            mw.col.sched.unsuspendCards([i])
    mw.reset()


def marker_main(*args, **kargs) -> None:
    custom_bury_cards()
    custom_unbury_cards()


# hooks to automatically execute
gui_hooks.add_cards_did_add_note.append(marker_main)
gui_hooks.main_window_did_init.append(marker_main)
# create a new menu item, "Organizar Cartões"
action = QAction("Hide new cards until next day", mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, marker_main)
# and add it to the tools menu
mw.form.menuTools.addAction(action)

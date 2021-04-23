#!/usr/bin/env python

# import the main window object (mw) from aqt
from aqt import mw
# import all of the Qt GUI library
from aqt.qt import *
# import hooks
from anki.hooks import addHook
from aqt.utils import getText, showInfo
from anki.lang import _
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
from anki import Collection

from aqt import gui_hooks
from datetime import datetime
from time import time_ns
import re
from pathlib import Path
import json


# Load config file
def handle_config() -> dict:
    config = mw.addonManager.getConfig(__name__)
    if not config:
        config = {
            'added_today_only': False
        }
        mw.addonManager.writeConfig(__name__, config)
        config_path = Path(mw.addonManager._addonMetaPath(__name__)).parent.absolute().joinpath('config.json')
        config_path.write_text(json.dumps(config))
    return config


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
    d = datetime.fromtimestamp(note.id//10**3)
    d = datetime(d.year, d.month, d.day, 0)
    for tag in tags:
        tagMO = REGEX_TAG.search(tag)
        if not tagMO:
            continue
        note.delTag(tag)


def bury_cards_all(*args, **kargs) -> None:
    ids = mw.col.find_cards("is:new -is:suspended")
    mw.col.sched.suspendCards(ids)
    for i in ids:
        card = mw.col.getCard(i)
        note = card.note()
        note.addTag(marker_tag())
        note.flush()
    mw.reset()


def bury_cards_today(*args, **kargs) -> None:
    ids = mw.col.find_cards("is:new -is:suspended added:1")
    mw.col.sched.suspendCards(ids)
    for i in ids:
        card = mw.col.getCard(i)
        note = card.note()
        note.addTag(marker_tag())
        note.flush()
    mw.reset()


def unbury_cards(*args, **kargs) -> None:
    ids = mw.col.find_cards(f'tag:"{MARKER_TAG_BASE}*"')
    for i in ids:
        card = mw.col.getCard(i)
        note = card.note()
        remove_mark_tags(note, note.tags)
        note.flush()
        unsuspend_note = True
        added_today_only = kargs.get('added_today_only', False)
        for tag in note.tags:
            if is_marker_tag_from_today(tag) and added_today_only:
                unsuspend_note = False
        if unsuspend_note:
            mw.col.sched.unsuspendCards([i])
    mw.reset()


def marker_main(*args, **kargs) -> None:
    if args:
        config_added_today_only = json.loads(args[0]).get('added_today_only', 'somethin_else')
    else:
        config_added_today_only = handle_config().get('added_today_only', 'something_else')

    if config_added_today_only == 'something_else':
        raise ValueError('the key "added_today_only" must be present on config file!')
    elif config_added_today_only not in [True, False]:
        raise ValueError(f'the key "added_today_only" must be either "true" or "false", but found {config_added_today_only}')

    unbury_cards(added_today_only=config_added_today_only)
    if config_added_today_only:
        bury_cards_today()
    else:
        bury_cards_all()
    if args:
        return args[0]


# hooks to automatically execute
gui_hooks.add_cards_did_add_note.append(marker_main)
gui_hooks.main_window_did_init.append(marker_main)
gui_hooks.addon_config_editor_will_save_json.append(marker_main)
# create a new menu item, "Organizar Cartões"
action = QAction("Hide new cards until next day", mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, marker_main)
# and add it to the tools menu
mw.form.menuTools.addAction(action)

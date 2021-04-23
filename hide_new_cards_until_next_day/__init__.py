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
from anki.tags import TagManager


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


def suspend_cards(*args, **kargs) -> None:
    added_today_only = kargs.get('added_today_only', False)
    if added_today_only:
        desired_cids = mw.col.find_cards("is:new -is:suspended added:1")
    else:
        desired_cids = mw.col.find_cards("is:new -is:suspended")
    if desired_cids:
        mw.col.sched.suspendCards(desired_cids)
    desired_nids = get_ids_to_suspend(added_today_only, 'notes')
    if desired_nids:
        mw.col.tags.bulk_update(desired_nids, ' '.join(get_tags_to_remove()), '', False)
        mw.col.tags.bulk_add(desired_nids, marker_tag())

    # get rid of marker tags for all those other cards that doesn't need
    needed = set(get_ids_to_suspend(added_today_only, 'notes'))
    unneeded = set(mw.col.find_notes(f'tag:"{MARKER_TAG_BASE}*"'))
    diff = list(unneeded - needed)
    mw.col.tags.bulk_update(diff, ' '.join([x for x in mw.col.tags.all() if REGEX_TAG.search(x)]), '', False)
    mw.reset()


def unsuspend_cards(*args, **kargs) -> None:
    # unsuspend all the cards with the custom marker
    # we don't need to worry about which exactly need
    # to be marked/unmarked because we handle this in
    # the suspend_cards function
    desired_cids = mw.col.find_cards(f'tag:"{MARKER_TAG_BASE}*"')
    if desired_cids:
        mw.col.sched.unsuspendCards(desired_cids)

    # remove all the marker tags
    added_today_only = kargs.get('added_today_only', False)
    desired_nids = get_ids_to_suspend(added_today_only, 'notes')
    if desired_nids:
        mw.col.tags.bulk_update(desired_nids, ' '.join(get_tags_to_remove()), '', False)
    mw.reset()


def get_tags_to_remove() -> list:
    all_tags = mw.col.tags.all()
    return [x for x in all_tags if REGEX_TAG.search(x) and x != marker_tag()]


def get_ids_to_suspend(added_today_only: bool, note_or_card: str) -> list:
    if added_today_only:
        d = datetime.fromtimestamp(time_ns()//10**9)
        d = int(int(datetime(d.year, d.month, d.day, 0).timestamp()) * 10**3)
        ids = mw.col.db.all(f"select {note_or_card}.id from cards join notes on cards.nid = notes.id where (cards.type = 0 or cards.queue = 0) and notes.id >= {d}")
    else:
        ids = mw.col.db.all(f"select {note_or_card}.id from cards join notes on cards.nid = notes.id where (cards.type = 0 or cards.queue = 0)")

    if ids:
        ids = [int(x[0]) for x in ids]
    return ids


def marker_main(*args, **kargs) -> None:
    try:
        config_added_today_only = json.loads(args[0]).get('added_today_only', 'somethin_else')
    except Exception:
        config_added_today_only = handle_config().get('added_today_only', 'something_else')

    if config_added_today_only == 'something_else':
        raise ValueError('the key "added_today_only" must be present on config file!')
    elif config_added_today_only not in [True, False]:
        raise ValueError(f'the key "added_today_only" must be either "true" or "false", but found {config_added_today_only}')

    unsuspend_cards(added_today_only=config_added_today_only)
    suspend_cards(added_today_only=config_added_today_only)
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

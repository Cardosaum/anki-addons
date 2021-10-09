#!/usr/bin/env python
from anki import version as anki_version
from aqt import gui_hooks
from aqt import mw
from aqt.qt import QAction, QKeySequence
from aqt.utils import qconnect
from datetime import datetime
from datetime import timedelta
from json import dumps, loads
from pathlib import Path
from re import compile


# Load config file
def handle_config() -> dict:
    config = mw.addonManager.getConfig(__name__)
    if not config:
        config = {
            "added_today_only": False,
            "hide_when_add": False
        }
        mw.addonManager.writeConfig(__name__, config)
        config_path = (
            Path(mw.addonManager._addonMetaPath(__name__))
            .parent.absolute()
            .joinpath("config.json")
        )
        config_path.write_text(dumps(config))
    return config


# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.
MARKER_SEP = "_"
MARKER_TAG_BASE = "ø::hide_new_cards_until_next_day"
MARKER_TAG_HIDDEN = MARKER_TAG_BASE + "::hidden_at::"
MARKER_TAG_REDEEM = MARKER_TAG_BASE + "::redeem_at::"
REGEX_TAG = compile(f"^{MARKER_TAG_HIDDEN}" + r"\d{4}-\d{,2}-\d{,2}$")
REGEX_TAG_REDEEM = compile(f"^{MARKER_TAG_REDEEM}" + r"\d{4}-\d{,2}-\d{,2}$")


def marker_today():
    return datetime.date(datetime.now())


def marker_n(n: int):
    return marker_today() + timedelta(days=n)


def marker_yesterday():
    return marker_n(-1)


def marker_tag() -> str:
    return f'{MARKER_TAG_HIDDEN}{marker_today().strftime("%Y-%m-%d")}'


def marker_tag_yesterday() -> str:
    return f'{MARKER_TAG_BASE}{marker_yesterday().strftime("%Y-%m-%d")}'


def marker_tag_n(n: int) -> str:
    return f'{MARKER_TAG_REDEEM}{marker_n(n).strftime("%Y-%m-%d")}'

def remove_tags(nids: list, tags: str):
    anki_versions = [int(x) for x in anki_version.strip().split('.')]
    if anki_versions[0] == 2 and anki_versions[1] >= 1 and anki_versions[2] >= 45:
        mw.col.tags.bulk_remove(nids, tags)
    else:
        mw.col.tags.bulk_update(nids, tags, "", False)


def suspend_cards_v2(*args, **kargs) -> None:
    added_today_only = kargs.get('added_today_only', False)
    search = f'is:new -is:buried -is:suspended -tag:"{MARKER_TAG_REDEEM}*"'
    if added_today_only:
        search += " added:1"

    cids = mw.col.find_cards(search)
    nids = mw.col.find_notes(search)

    # suspend all cards that are new
    # (either only from today or all new cards)
    if cids:
        mw.col.sched.suspendCards(cids)

    # get the note id of this cards
    # and add a new marker tag from today
    # and a redeem tag for tomorrow
    if nids:
        mw.col.tags.bulk_add(nids, " ".join([marker_tag(), marker_tag_n(1)]))

    # remove unneded tags
    marker_tags = [
        x for x in mw.col.tags.all() if REGEX_TAG.search(x) and x != marker_tag()
    ]
    if marker_tags:
        tags_search = " or ".join([f'tag:"{x}"' for x in marker_tags])
        nids_tags_to_remove = mw.col.find_notes(tags_search)
        if nids_tags_to_remove:
            remove_tags(nids_tags_to_remove, " ".join(marker_tags))
    mw.reset()


def is_redeem_tag_expired(tag: str) -> bool:
    tag = tag.strip().removeprefix(MARKER_TAG_REDEEM)
    d = datetime.strptime(tag, "%Y-%m-%d")
    if (datetime.now() - d).days >= 0:
        return True
    return False


def unsuspend_cards_v2(*args, **kargs) -> None:
    # unsuspend all cards whose redeem date has expired
    added_today_only = kargs.get("added_today_only", False)
    if added_today_only:
        redeem_tags = [x for x in mw.col.tags.all() if REGEX_TAG_REDEEM.search(x)]
    else:
        redeem_tags = [
            x
            for x in mw.col.tags.all()
            if REGEX_TAG_REDEEM.search(x) and is_redeem_tag_expired(x)
        ]

    if redeem_tags:
        tags_search = " or ".join([f'tag:"{x}"' for x in redeem_tags])
    else:
        return

    if added_today_only:
        tags_search = f"({tags_search}) -added:1"

    cids = mw.col.find_cards(tags_search)
    if cids:
        mw.col.sched.unsuspendCards(cids)

    # remove unneeded mark tags
    nids = mw.col.find_notes(tags_search)
    if nids:
        remove_tags(
            nids,
            f'{marker_tag()} {" ".join(redeem_tags)} {" ".join([x for x in mw.col.tags.all() if REGEX_TAG.search(x)])}'
        )
    mw.reset()


def marker_main(*args, **kargs) -> None:
    from pprint import pprint

    pprint(f"ARGS: {args}")
    pprint(f"KARGS: {kargs}")
    execute_suspend = True
    something_else = "something_else"
    try:
        config_added_today_only = loads(args[0]).get('added_today_only', something_else)
    except Exception:
        config_added_today_only = handle_config().get('added_today_only', something_else)

    if config_added_today_only == something_else:
        execute_suspend = False
        # raise ValueError('the key "added_today_only" must be present on config file!')
    elif config_added_today_only not in [True, False]:
        execute_suspend = False
        # raise ValueError(f'the key "added_today_only" must be either "true" or "false", but found {config_added_today_only}')

    if execute_suspend:
        suspend_cards_v2(added_today_only=config_added_today_only)
        unsuspend_cards_v2(added_today_only=config_added_today_only)

    if args:
        return args[0]


# hooks to automatically execute
config_hide_when_add = handle_config().get('hide_when_add', False)
if config_hide_when_add:
    gui_hooks.add_cards_did_add_note.append(marker_main)
gui_hooks.addon_config_editor_will_save_json.append(marker_main)
gui_hooks.main_window_did_init.append(marker_main)
gui_hooks.profile_will_close.append(marker_main)

# create a new menu item
action = QAction("Hide new cards until next day", mw)
action.setShortcuts(QKeySequence("Ctrl+Alt+t"))

# set it to call testFunction when it's clicked
qconnect(action.triggered, marker_main)

# and add it to the tools menu
mw.form.menuTools.addAction(action)

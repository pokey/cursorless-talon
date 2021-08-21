from ..conventions import get_cursorless_list_name
from talon import Module, actions, app
from dataclasses import dataclass
from ..csv_overrides import init_csv_and_watch_changes
from .homophones import run_homophones_action
from .find import run_find_action
from .call import run_call_action

mod = Module()


@dataclass
class MakeshiftAction:
    term: str
    identifier: str
    vscode_command_id: str
    pre_command_sleep: float = 0
    post_command_sleep: float = 0


# NOTE: Please do not change these dicts.  Use the CSVs for customization.
# See https://github.com/pokey/cursorless-talon/blob/master/docs/customization.md
makeshift_actions = [
    MakeshiftAction("define", "revealDefinition", "editor.action.revealDefinition"),
    MakeshiftAction("hover", "showHover", "editor.action.showHover"),
    MakeshiftAction("inspect", "showDebugHover", "editor.debug.action.showDebugHover"),
    MakeshiftAction(
        "quick fix", "quickFix", "editor.action.quickFix", pre_command_sleep=0.3
    ),
    MakeshiftAction("reference", "showReferences", "references-view.find"),
    MakeshiftAction("rename", "rename", "editor.action.rename", post_command_sleep=0.1),
]

makeshift_action_map = {action.identifier: action for action in makeshift_actions}


@dataclass
class CallbackAction:
    term: str
    identifier: str
    callback: callable


# NOTE: Please do not change these dicts.  Use the CSVs for customization.
# See https://github.com/pokey/cursorless-talon/blob/master/docs/customization.md
callbacks = [
    CallbackAction("call", "call", run_call_action),
    CallbackAction("scout", "find", run_find_action),
    CallbackAction("phones", "nextHomophone", run_homophones_action),
]

callbacks_map = {callback.identifier: callback.callback for callback in callbacks}


mod.list("cursorless_simple_action", desc="Supported actions for cursorless navigation")


# NOTE: Please do not change these dicts.  Use the CSVs for customization.
# See https://github.com/pokey/cursorless-talon/blob/master/docs/customization.md
simple_actions = {
    "bottom": "scrollToBottom",
    "breakpoint": "setBreakpoint",
    "carve": "cut",
    "center": "scrollToCenter",
    "chuck": "delete",
    "clear": "clear",
    "clone up": "copyLinesUp",
    "clone": "copyLinesDown",
    "comment": "commentLines",
    "copy": "copy",
    "crown": "scrollToTop",
    "dedent": "outdentLines",
    "drink": "editNewLineAbove",
    "drop": "insertEmptyLineAbove",
    "extract": "extractVariable",
    "float": "insertEmptyLineBelow",
    "fold": "fold",
    "indent": "indentLines",
    "paste to": "paste",
    "post": "setSelectionAfter",
    "pour": "editNewLineBelow",
    "pre": "setSelectionBefore",
    "puff": "insertEmptyLinesAround",
    "reverse": "reverse",
    "scout all": "findInFiles",
    "sort": "sort",
    "take": "setSelection",
    "unfold": "unfold",
    **{action.term: action.identifier for action in makeshift_actions},
    **{callback.term: callback.identifier for callback in callbacks},
}


@mod.action_class
class Actions:
    def cursorless_simple_action(action: str, targets: dict):
        """Perform cursorless simple action"""
        if action in callbacks_map:
            return callbacks_map[action](targets)
        elif action in makeshift_action_map:
            return run_makeshift_action(action, targets)
        else:
            return actions.user.cursorless_single_target_command(action, targets)


def run_makeshift_action(action: str, targets: dict):
    """Execute makeshift action"""
    makeshift_action = makeshift_action_map[action]
    actions.user.cursorless_single_target_command("setSelection", targets)
    actions.sleep(makeshift_action.pre_command_sleep)
    actions.user.vscode(makeshift_action.vscode_command_id)
    actions.sleep(makeshift_action.post_command_sleep)


# NOTE: Please do not change these dicts.  Use the CSVs for customization.
# See https://github.com/pokey/cursorless-talon/blob/master/docs/customization.md
default_values = {
    "simple_action": simple_actions,
    "swap_action": {"swap": "swap"},
    "move_bring_action": {"bring": "bring", "move": "move"},
    "wrap_action": {"wrap": "wrap"},
    "reformat_action": {"format": "reformat"},
}

ACTION_LIST_NAMES = [get_cursorless_list_name(key) for key in default_values]


def on_ready():
    init_csv_and_watch_changes("actions", default_values)


app.register("ready", on_ready)

from dataclasses import dataclass
from pathlib import Path
from ..conventions import get_cursorless_list_name
from talon import Module, actions, app, Context, fs, cron, speech_system
from ..csv_overrides import init_csv_and_watch_changes

mod = Module()
ctx = Context()


mod.list("cursorless_hat_color", desc="Supported hat colors for cursorless")
mod.list("cursorless_hat_shape", desc="Supported hat shapes for cursorless")

# NOTE: Please do not change these dicts.  Use the CSVs for customization.
# See https://github.com/pokey/cursorless-talon/blob/main/docs/customization.md
hat_colors = {
    "blue": "blue",
    "green": "green",
    "rose": "red",
    "plum": "pink",
    "squash": "yellow",
}

hat_shapes = {
    "ex": "ex",
    "fox": "fox",
    "wing": "wing",
    "hole": "hole",
    "frame": "frame",
    "curve": "curve",
    "eye": "eye",
    "play": "play",
    "cross": "crosshairs",
    "bolt": "bolt",
}


@mod.capture(
    rule="[{user.cursorless_hat_color}] [{user.cursorless_hat_shape}] <user.any_alphanumeric_key>"
)
def cursorless_decorated_symbol(m) -> str:
    """A decorated symbol"""
    hat_color = getattr(m, "cursorless_hat_color", "default")
    try:
        hat_style_name = f"{hat_color}-{m.cursorless_hat_shape}"
    except AttributeError:
        hat_style_name = hat_color

    try:
        use_pre_phrase_snapshot = actions.user.did_emit_pre_phrase_signal()
    except AttributeError:
        use_pre_phrase_snapshot = False

    return {
        "mark": {
            "type": "decoratedSymbol",
            "symbolColor": hat_style_name,
            "character": m.any_alphanumeric_key,
            "usePrePhraseSnapshot": use_pre_phrase_snapshot,
        }
    }


@dataclass
class CustomizableTerm:
    defaultSpokenForm: str
    cursorlessIdentifier: str
    value: any


# NOTE: Please do not change these dicts.  Use the CSVs for customization.
# See https://github.com/pokey/cursorless-talon/blob/main/docs/customization.md
special_marks = [
    CustomizableTerm("this", "currentSelection", {"mark": {"type": "cursor"}}),
    CustomizableTerm("that", "previousTarget", {"mark": {"type": "that"}}),
    CustomizableTerm("source", "previousSource", {"mark": {"type": "source"}}),
    # "last cursor": {"mark": {"type": "lastCursorPosition"}} # Not implemented
]

special_marks_map = {term.cursorlessIdentifier: term for term in special_marks}

special_marks_defaults = {
    term.defaultSpokenForm: term.cursorlessIdentifier for term in special_marks
}


mod.list("cursorless_special_mark", desc="Cursorless special marks")


@mod.capture(
    rule=(
        "<user.cursorless_decorated_symbol> | "
        "{user.cursorless_special_mark} |"
        # Because of problems with performance we have to have a simple version for now
        # "<user.cursorless_line_number>" # row, up, down
        "<user.cursorless_line_number_simple>"  # up, down
    )
)
def cursorless_mark(m) -> str:
    try:
        return m.cursorless_decorated_symbol
    except AttributeError:
        pass
    try:
        return special_marks_map[m.cursorless_special_mark].value
    except AttributeError:
        pass
    return m.cursorless_line_number_simple


DEFAULT_COLOR_ENABLEMENT = {
    "blue": True,
    "green": True,
    "red": True,
    "pink": True,
    "yellow": True,
}

DEFAULT_SHAPE_ENABLEMENT = {
    "ex": False,
    "fox": False,
    "wing": False,
    "hole": False,
    "frame": False,
    "curve": False,
    "eye": False,
    "play": False,
    "bolt": False,
    "crosshairs": False,
}

unsubscribe_hat_styles = None


def setup_hat_styles_csv():
    global unsubscribe_hat_styles

    color_enablement = {
        **DEFAULT_COLOR_ENABLEMENT,
        **actions.user.vscode_get_setting("cursorless.hatEnablement.colors", {}),
    }
    shape_enablement = {
        **DEFAULT_SHAPE_ENABLEMENT,
        **actions.user.vscode_get_setting("cursorless.hatEnablement.shapes", {}),
    }

    active_hat_colors = {
        spoken_form: value
        for spoken_form, value in hat_colors.items()
        if color_enablement[value]
    }
    active_hat_shapes = {
        spoken_form: value
        for spoken_form, value in hat_shapes.items()
        if shape_enablement[value]
    }

    if unsubscribe_hat_styles is not None:
        unsubscribe_hat_styles()

    unsubscribe_hat_styles = init_csv_and_watch_changes(
        "hat_styles",
        {
            "hat_color": active_hat_colors,
            "hat_shape": active_hat_shapes,
        },
        [*hat_colors.values(), *hat_shapes.values()],
    )


fast_reload_job = None
slow_reload_job = None


def on_ready():
    init_csv_and_watch_changes(
        "special_marks",
        {
            "special_mark": special_marks_defaults,
        },
    )

    setup_hat_styles_csv()

    vscode_settings_path: Path = actions.user.vscode_settings_path().resolve()

    def on_watch(path, flags):
        global fast_reload_job, slow_reload_job
        cron.cancel(fast_reload_job)
        cron.cancel(slow_reload_job)
        fast_reload_job = cron.after("500ms", setup_hat_styles_csv)
        slow_reload_job = cron.after("10s", setup_hat_styles_csv)

    fs.watch(vscode_settings_path, on_watch)


app.register("ready", on_ready)

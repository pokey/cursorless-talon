from dataclasses import dataclass
from talon import Context, Module, app
from ..csv_overrides import init_csv_and_watch_changes

mod = Module()
ctx = Context()


mod.list("cursorless_symbol_color", desc="Supported symbol colors for cursorless")

# NOTE: Please do not change these dicts.  Use the CSVs for customization.
# See https://github.com/pokey/cursorless-talon/blob/master/docs/customization.md
symbol_colors = {
    "gray": "default",
    "blue": "blue",
    "green": "green",
    "rose": "red",
    "squash": "yellow",
    "plum": "purple",
}


@mod.capture(rule="[{user.cursorless_symbol_color}] <user.any_alphanumeric_key>")
def cursorless_decorated_symbol(m) -> str:
    """A decorated symbol"""
    try:
        symbol_color = m.cursorless_symbol_color
    except AttributeError:
        symbol_color = "default"
    return {
        "mark": {
            "type": "decoratedSymbol",
            "symbolColor": symbol_color,
            "character": m.any_alphanumeric_key,
        }
    }


@dataclass
class CustomizableTerm:
    defaultSpokenForm: str
    cursorlessIdentifier: str
    value: any


# NOTE: Please do not change these dicts.  Use the CSVs for customization.
# See https://github.com/pokey/cursorless-talon/blob/master/docs/customization.md
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


def on_ready():
    init_csv_and_watch_changes(
        "special_marks",
        {
            "special_mark": special_marks_defaults,
        },
    )
    init_csv_and_watch_changes(
        "colors",
        {
            "symbol_color": symbol_colors,
        },
    )


app.register("ready", on_ready)

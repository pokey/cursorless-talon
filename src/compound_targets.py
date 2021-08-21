from .primitive_target import BASE_TARGET
from talon import Module, app
from .csv_overrides import init_csv_and_watch_changes

mod = Module()


mod.list(
    "cursorless_range_specifier",
    desc="A range joiner that indicates whether to include or exclude anchor and active",
)
mod.list(
    "cursorless_list_specifier",
    desc="A list joiner",
)


@mod.capture(
    rule=(
        "[{user.cursorless_range_specifier}] <user.cursorless_primitive_target> | "
        "<user.cursorless_primitive_target> {user.cursorless_range_specifier} <user.cursorless_primitive_target>"
    )
)
def cursorless_range(m) -> str:
    primitive_targets = m.cursorless_primitive_target_list
    range_specifier = getattr(m, "cursorless_range_specifier", None)

    if range_specifier is None:
        return primitive_targets[0]

    if len(primitive_targets) == 1:
        start = BASE_TARGET.copy()
    else:
        start = primitive_targets[0]

    return {
        "type": "range",
        "start": start,
        "end": primitive_targets[-1],
        "excludeStart": range_specifier
        in ["rangeExcludingBothEnds", "rangeExcludingAnchor"],
        "excludeEnd": range_specifier
        in ["rangeExcludingBothEnds", "rangeExcludingActive"],
    }


@mod.capture(
    rule="<user.cursorless_range> ({user.cursorless_list_specifier} <user.cursorless_range>)*"
)
def cursorless_target(m) -> str:
    if len(m.cursorless_range_list) == 1:
        return m.cursorless_range
    return {"type": "list", "elements": m.cursorless_range_list}


# NOTE: Please do not change these dicts.  Use the CSVs for customization.
# See https://github.com/pokey/cursorless-talon/blob/master/docs/customization.md
range_specifiers = {
    "between": "rangeExcludingBothEnds",
    "past": "rangeIncludingBothEnds",
    "skip past": "rangeExcludingAnchor",
    "until": "rangeExcludingActive",
}


def on_ready():
    init_csv_and_watch_changes(
        "compound_targets",
        {
            "range_specifier": range_specifiers,
            "list_specifier": {"and": "listSpecifier"},
        },
    )


app.register("ready", on_ready)
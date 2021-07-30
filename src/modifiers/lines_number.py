from talon import Context, Module

mod = Module()
ctx = Context()

ctx.matches = r"""
tag: user.cursorless
"""

mod.list("cursorless_line_direction", desc="Supported directions for line modifier")

directions = {
    "row": {"isRelative": False, "transformation": lambda number: number - 1},
    "up": {"isRelative": True, "transformation": lambda number: -number},
    "down": {"isRelative": True, "transformation": lambda number: number},
}

ctx.lists["self.cursorless_line_direction"] = directions.keys()


def parse_line(line: dict):
    direction = directions[line["direction"]]
    line_number = line["lineNumber"]
    return {
        "lineNumber": direction["transformation"](line_number),
        "isRelative": direction["isRelative"],
    }


@mod.capture(rule="{user.cursorless_line_direction} <number>")
def cursorless_line_number_anchor(m) -> str:
    return {"direction": m.cursorless_line_direction, "lineNumber": m.number}


@mod.capture(rule="past [{user.cursorless_line_direction}] <number>")
def cursorless_line_number_active(m) -> str:
    try:
        direction = m.cursorless_line_direction
    except:
        direction = None
    return {"direction": direction, "lineNumber": m.number}


@mod.capture(
    rule="<user.cursorless_line_number_anchor> [<user.cursorless_line_number_active>]"
)
def cursorless_line_number(m) -> str:
    anchor = m.cursorless_line_number_anchor
    try:
        active = m.cursorless_line_number_active
        # Infer missing direction from anchor
        if active["direction"] == None:
            active["direction"] = anchor["direction"]
    except:
        active = anchor
    return {
        "selectionType": "line",
        "modifier": {
            "type": "lineNumber",
            "anchor": parse_line(anchor),
            "active": parse_line(active),
        },
    }

@mod.capture(
    rule="(up|down) <number_small>"
)
def cursorless_line_number_simple(m) -> str:
    position = {"direction": m[0], "lineNumber": m.number_small}
    return {
        "selectionType": "line",
        "modifier": {
            "type": "lineNumber",
            "anchor": parse_line(position),
            "active": parse_line(position),
        },
    }
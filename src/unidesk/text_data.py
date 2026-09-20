"""Loads UniDesk's user-facing text from the bundled JSON files."""

import json
from functools import cache
from importlib.resources import files

_TEXT_DATA_PACKAGE = "unidesk.assets.text_data"


@cache
def load(name):
    """Return the parsed contents of <name>.json."""
    path = files(_TEXT_DATA_PACKAGE).joinpath(f"{name}.json")
    return json.loads(path.read_text(encoding="utf-8"))


def faq_body():
    """Flatten the structured FAQ entries into the page body text."""
    entries = load("faq")["entries"]
    return "\n\n".join(f"Q: {e['question']}\nA: {e['answer']}" for e in entries)


def pages():
    """Page bodies keyed by page title, in display order."""
    resolved = {}
    for key, page in load("pages").items():
        if "body_from" in page:
            resolved[key] = {"body": faq_body()}
        else:
            resolved[key] = {"body": page["body"]}
    return resolved

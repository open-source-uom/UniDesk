"""@file text_data.py
@brief Loads UniDesk's user-facing text from the bundled JSON files."""

import json
from functools import cache
from importlib.resources import files

_TEXT_DATA_PACKAGE = "unidesk.assets.text_data"


@cache
def load(name):
    """@brief Reads one of the bundled JSON text files. Results are cached.
    @param name File name inside assets/text_data, without the .json extension.
    @return The parsed JSON data.
    """
    path = files(_TEXT_DATA_PACKAGE).joinpath(f"{name}.json")
    return json.loads(path.read_text(encoding="utf-8"))


def faq_body():
    """@brief Flattens the FAQ entries from faq.json into one block of text.
    @return The FAQ as "Q: ... A: ..." pairs separated by blank lines.
    """
    entries = load("faq")["entries"]
    return "\n\n".join(f"Q: {e['question']}\nA: {e['answer']}" for e in entries)


def pages():
    """@brief Builds the text pages defined in pages.json.

    Entries with a "body_from" key get the FAQ text as their body.
    @return A dict of page title to {"body": text}, in display order.
    """
    resolved = {}
    for key, page in load("pages").items():
        if "body_from" in page:
            resolved[key] = {"body": faq_body()}
        else:
            resolved[key] = {"body": page["body"]}
    return resolved

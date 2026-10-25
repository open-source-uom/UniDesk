"""@file loader.py
@brief Loads UniDesk's Qt stylesheets and assets from the styles package."""

import atexit
from contextlib import ExitStack
from functools import cache
from importlib.resources import as_file, files

# Keeps extracted asset files alive for the whole process (needed when the
# package is imported from a zipped wheel); cleaned up on interpreter exit.
_asset_stack = ExitStack()
atexit.register(_asset_stack.close)


@cache
def load_qss(filename):
    """@brief Reads a stylesheet from the styles package. Results are cached.

    The `__CHECK_SVG__` token is replaced with the real path of check.svg.
    @param filename Path of the .qss file inside the styles package.
    @return The stylesheet text, ready for setStyleSheet().
    """
    qss = files("unidesk.styles").joinpath(filename).read_text(encoding="utf-8")
    if "__CHECK_SVG__" in qss:
        qss = qss.replace("__CHECK_SVG__", str(resolve_asset_path("check.svg")))
    return qss


@cache
def resolve_asset_path(filename):
    """@brief Gives a real file path for an asset in the styles package.

    The file stays available until the program exits, even when installed from a zip.
    @param filename Path of the asset inside the styles package.
    @return A path to the asset on disk.
    """
    return _asset_stack.enter_context(
        as_file(files("unidesk.styles").joinpath(filename))
    )

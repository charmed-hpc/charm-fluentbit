"""Generic utilities for the charm."""

from pathlib import Path
from typing import Tuple

OS_RELEASE = Path("/etc/os-release").read_text().split("\n")
OS_RELEASE_CTXT = {
    k: v.strip("\"")
    for k, v in [item.split("=") for item in OS_RELEASE if item != '']
}


def operating_system() -> Tuple[str, str]:
    """Return what operating system we are running.

    Returns:
        A tuple with two strings, the first with the operating system and the
        second is the version. Examples: ``('ubuntu', '20.04')``,
        ``('centos', '7')``.
    """
    id_ = OS_RELEASE_CTXT["ID"]
    version = OS_RELEASE_CTXT.get("VERSION_ID", "")
    return (id_, version)

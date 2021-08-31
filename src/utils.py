"""Generic utilities for the charm."""

from pathlib import Path
from typing import Tuple


def operating_system() -> Tuple[str, str]:
    """Return what operating system we are running.

    Returns:
        A tuple with two strings, the first with the operating system and the
        second is the version. Examples: ``('ubuntu', '20.04')``,
        ``('centos', '7')``.
    """
    os_release = Path("/etc/os-release").read_text().split("\n")
    os_release_ctxt = {k: v.strip("\"")
                       for k, v in [item.split("=") for item in os_release if item != '']}

    id_ = os_release_ctxt["ID"]
    version = os_release_ctxt.get("VERSION_ID", "")
    return (id_, version)

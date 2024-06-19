# Copyright © 2023, Indiana University
# BSD 3-Clause License

"""
Patch the `jinja2` `collections.abc.Mapping` issue in Python 3.10, 3.11

Usage
-----

python patch_jinja.py

When to use
-----------

If you run `python -m flask --version` and see something like:

```
ImportError: cannot import name 'Mapping' from 'collections'
```
"""

import os
import sys


def get_major_minor():
    """Return (major_version: int, minor_version: int) tuple of the Python interpreter."""
    major, minor, *_ = sys.version_info
    return major, minor


def is_windows():
    """We know we're on windows if the platform starts with 'win' 🤷‍♀️"""
    return sys.platform.startswith("win")


def get_venv_folder():
    """`.venv` and `venv` are the conventional choices"""
    if os.path.isdir("venv"):
        return "venv"
    if os.path.isdir(".venv"):
        return ".venv"
    return None


if __name__ == "__main__":
    major, minor = get_major_minor()

    venvpath = get_venv_folder()
    if venvpath is None:
        print("Error. Did not find venv folder", file=sys.stderr)
        sys.exit(2)

    if is_windows():
        # Setting up venv on Windows seems more consistent with using 'Lib'
        # rather than using separate directories for Python 3.10 or 3.11
        file_path = os.path.join(
            venvpath, "Lib", "site-packages", "jinja2", "tests.py"
        )
    else:
        if (major, minor) == (3, 10):
            pypath = "python3.10"
        elif (major, minor) == (3, 11):
            pypath = "python3.11"
        elif (major, minor) == (3, 12):
            pypath = "python3.12"
        else:
            sys.stderr.write("This should only be ran when using python-3.10 or 3.11")
            sys.exit(1)

        file_path = os.path.join(
            venvpath, "lib", pypath, "site-packages", "jinja2", "tests.py"
        )

    if not os.path.isfile(file_path):
        print(f"Error. Did not find: '{file_path}'", file=sys.stderr)
        print("       venv/pip may have installed files in an unexpected location")
        sys.exit(2)

    with open(file_path, mode="r", encoding="utf-8-sig", newline="") as fh:
        data = fh.read()

    with open(file_path, mode="w", encoding="utf-8-sig", newline="") as fh:
        fh.write(
            data.replace(
                "from collections import Mapping", "from collections.abc import Mapping"
            )
        )

    print(f"Patched {file_path}")
    sys.exit(0)

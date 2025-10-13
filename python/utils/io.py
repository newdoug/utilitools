"""Input/output and logging tools"""

import sys


def eprint(*args, **kwargs) -> None:
    """Print to stderr. This isn't fast, so don't use it if performance
    matters
    """
    kwargs = kwargs or {}
    kwargs["file"] = kwargs.get("file", sys.stderr)
    print(*args, **kwargs)

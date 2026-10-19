"""Small local configuration helpers; environment variables take precedence."""
from __future__ import annotations

import os
from pathlib import Path


def load_local_env() -> None:
    """Load simple KEY=VALUE entries from project .env without overriding shell env."""
    env_file = Path.cwd() / ".env"
    if not env_file.is_file():
        return
    for raw_line in env_file.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if name and name not in os.environ:
            os.environ[name] = value

"""Optional .mpp reader. This machine has no Java, so the extra is not loaded."""

from __future__ import annotations

import shutil
from pathlib import Path

from atlaspmo.model.schedule import Schedule


class MppUnavailable(RuntimeError):
    """Raised when .mpp cannot be read in this environment."""


def read_mpp(path: Path) -> Schedule:
    """Read an .mpp file. Refuses to run when Java or the extra is missing."""
    del path
    if shutil.which("java") is None:
        raise MppUnavailable(
            "Java no está en el PATH. La lectura .mpp queda omitida. "
            "El extra [mpp] no se instaló en esta máquina."
        )
    raise MppUnavailable("Java está, pero el extra [mpp] no se cargó en esta corrida.")

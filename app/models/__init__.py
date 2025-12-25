"""Model exports.

The SQLAlchemy models live in the module :mod:`app.models` (file ``app/models.py``).
Some parts of the code import from the package namespace (``from app.models import User``).

To avoid circular imports (package importing itself), we import from the sibling
module using a relative import.
"""

from ..models import Task, User  # type: ignore[F401]

__all__ = ["User", "Task"]

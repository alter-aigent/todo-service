"""Model exports.

The project defines SQLAlchemy models in :mod:`app.models` (module file) but
other parts of the code import them from the package namespace
(:mod:`app.models`).

This file re-exports the model classes to keep imports stable.
"""

from app.models import Task, User  # noqa: F401

__all__ = ["User", "Task"]

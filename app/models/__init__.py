"""Model exports.

This repository has both:
- ``app/models.py`` (module containing SQLAlchemy models)
- ``app/models/`` (package used as an import namespace)

Code expects ``from app.models import User, Task`` to work.

Importing from ``app.models`` inside this package causes circular imports.
So we import the sibling module explicitly via :mod:`importlib`.
"""

from importlib import import_module

_models_mod = import_module("app.models")

User = getattr(_models_mod, "User")
Task = getattr(_models_mod, "Task")

__all__ = ["User", "Task"]

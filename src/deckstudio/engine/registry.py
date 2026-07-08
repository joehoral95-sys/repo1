"""Slide-type -> renderer registry. Renderers self-register via @renderer."""

from __future__ import annotations

from collections.abc import Callable

_RENDERERS: dict[str, Callable] = {}


def renderer(slide_type: str):
    def decorate(fn: Callable) -> Callable:
        if slide_type in _RENDERERS:
            raise ValueError(f"duplicate renderer for slide type '{slide_type}'")
        _RENDERERS[slide_type] = fn
        return fn
    return decorate


def get_renderer(slide_type: str) -> Callable:
    _ensure_loaded()
    try:
        return _RENDERERS[slide_type]
    except KeyError:
        raise KeyError(
            f"No renderer registered for slide type '{slide_type}'. "
            f"Registered: {sorted(_RENDERERS)}") from None


def registered_types() -> list[str]:
    _ensure_loaded()
    return sorted(_RENDERERS)


def _ensure_loaded() -> None:
    if not _RENDERERS:
        from . import renderers  # noqa: F401  (import populates the registry)

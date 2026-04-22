from __future__ import annotations


class BusinessError(Exception):
    """Base for domain-level errors surfaced as HTTP 4xx."""


class NotFoundError(BusinessError):
    """Resource expected to exist was not found (HTTP 404)."""


class ConflictError(BusinessError):
    """Operation conflicts with current state (HTTP 409)."""

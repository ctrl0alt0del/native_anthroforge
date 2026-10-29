"""Shared dispatch for project-local reconstruction workflows."""

from typing import Any

from . import catalogue_operations, reconstruction_queue, reconstruction_reviews, variant_operations

PREFIXES = ("variant.", "catalogue.", "review.", "reconstruction.")


def execute(session: Any, operation: str, arguments: Any) -> Any:
    handlers = {
        "variant.": variant_operations.execute,
        "catalogue.": catalogue_operations.execute,
        "review.": reconstruction_reviews.execute,
        "reconstruction.queue.": reconstruction_queue.execute,
    }
    handler = next((value for key, value in handlers.items() if operation.startswith(key)), None)
    if handler is None:
        raise ValueError("Unknown reconstruction operation.")
    return handler(session, operation, arguments)

"""Webhook validation and processing for telco platform."""

from typing import Any, Callable, Dict


class WebhookRegistry:
    """Registry for webhook event handlers."""

    def __init__(self) -> None:
        self._handlers: Dict[str, Callable[[Dict[str, Any]], None]] = {}

    def register(self, event: str) -> Callable:
        """Decorator to register a webhook handler for an event."""

        def decorator(func: Callable[[Dict[str, Any]], None]) -> Callable:
            self._handlers[event] = func
            return func

        return decorator

    def dispatch(self, event: str, payload: Dict[str, Any]) -> None:
        """Dispatch a webhook event to the registered handler."""
        if event in self._handlers:
            self._handlers[event](payload)
        else:
            raise ValueError(f"No handler registered for event: {event}")


# Global registry instance
registry = WebhookRegistry()


# Pre-registered webhook events
WEBHOOK_PERSON_CREATED = "person.created"
WEBHOOK_PERSON_UPDATED = "person.updated"
WEBHOOK_PERSON_DELETED = "person.deleted"

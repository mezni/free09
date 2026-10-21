"""Response transformation to canonical format."""

from typing import Any, Dict, Optional


def to_canonical(obj: Any, include: Optional[list] = None) -> Dict[str, Any]:
    """Convert object to canonical (camelCase) format."""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            # Convert snake_case to camelCase
            camel_key = "".join(
                word.capitalize() if i > 0 else word
                for i, word in enumerate(key.split("_"))
            )
            if include and camel_key not in include:
                continue
            result[camel_key] = to_canonical(value, include)
        return result
    elif isinstance(obj, list):
        return [to_canonical(item, include) for item in obj]
    return obj


def from_canonical(obj: Any, exclude: Optional[list] = None) -> Any:
    """Convert from canonical (camelCase) to snake_case format."""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            # Convert camelCase to snake_case
            snake_key = "".join(
                "_" + char.lower() if char.isupper() else char for char in key
            ).lstrip("_")
            if exclude and snake_key in exclude:
                continue
            result[snake_key] = from_canonical(value, exclude)
        return result
    elif isinstance(obj, list):
        return [from_canonical(item, exclude) for item in obj]
    return obj

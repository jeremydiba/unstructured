import _thread
import copy
import functools
from dataclasses import fields

from dataclasses_json.core import (
    Collection,
    Enum,
    Mapping,
    _encode_overrides,
    _handle_undefined_parameters_safe,
    _user_overrides_or_exts,
    is_dataclass,
)


def _recursive_repr(user_function):
    # Decorator to make a repr function return "..." for a recursive
    # call.
    repr_running = set()

    @functools.wraps(user_function)
    def wrapper(self):
        key = id(self), _thread.get_ident()
        if key in repr_running:
            return "..."
        repr_running.add(key)
        try:
            result = user_function(self)
        finally:
            repr_running.discard(key)
        return result

    return wrapper


def _asdict(obj, encode_json=False, preserve_sensitive=True):
    """
    A re-implementation of `asdict` (based on the original in the `dataclasses`
    source) to support arbitrary Collection and Mapping types.
    """
    if is_dataclass(obj):
        result = []
        overrides = _user_overrides_or_exts(obj)
        for field in fields(obj):
            if getattr(field, "sensitive", False) and not preserve_sensitive:
                value = "***REDACTED***"
            elif overrides[field.name].encoder:
                value = getattr(obj, field.name)
            else:
                value = _asdict(getattr(obj, field.name), encode_json=encode_json)
            result.append((field.name, value))

        result = _handle_undefined_parameters_safe(cls=obj, kvs=dict(result), usage="to")
        return _encode_overrides(
            dict(result), _user_overrides_or_exts(obj), encode_json=encode_json
        )
    elif isinstance(obj, Mapping):
        return {
            _asdict(k, encode_json=encode_json): _asdict(v, encode_json=encode_json)
            for k, v in obj.items()
        }
    elif isinstance(obj, Collection) and not isinstance(obj, (str, bytes, Enum)):
        return [_asdict(v, encode_json=encode_json) for v in obj]
    else:
        return copy.deepcopy(obj)

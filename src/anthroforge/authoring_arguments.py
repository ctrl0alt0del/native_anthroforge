"""Transport-only JSON Pointer literals and legacy result-reference substitution."""

import re


def literal_paths(arguments, paths):
    if not isinstance(paths, list) or any(not isinstance(p, str) for p in paths):
        raise ValueError("literal_paths must be an array of RFC 6901 JSON Pointer strings.")
    selected = frozenset(pointer(path) for path in paths)
    for path in selected:
        require_path(arguments, path)
    return selected


def pointer(value):
    if value == "":
        return ()
    if not value.startswith("/") or re.search(r"~([^01]|$)", value):
        raise ValueError("Invalid literal_paths JSON Pointer: " + value)
    return tuple(token.replace("~1", "/").replace("~0", "~") for token in value[1:].split("/"))


def location(path):
    return "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in path)


def require_path(value, path):
    try:
        for token in path:
            value = member(value, token)
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise ValueError("literal_paths points to a missing argument: " + location(path)) from error


def member(value, token):
    if isinstance(value, list):
        if not re.fullmatch(r"0|[1-9][0-9]*", token):
            raise ValueError("Invalid JSON Pointer array index.")
        return value[int(token)]
    if not isinstance(value, dict):
        raise ValueError("JSON Pointer traverses a scalar.")
    return value[token]


def resolve(value, results, literals=frozenset(), path=()):
    if path in literals:
        return value
    if isinstance(value, str) and value.startswith("$"):
        return reference(value, results, path)
    if isinstance(value, dict):
        return {key: resolve(item, results, literals, (*path, key)) for key, item in value.items()}
    if isinstance(value, list):
        return [resolve(item, results, literals, (*path, str(i))) for i, item in enumerate(value)]
    return value


def reference(value, results, path):
    try:
        parts = value[1:].split(".")
        result = results[parts[0]]
        for part in parts[1:]:
            result = result[int(part)] if isinstance(result, (list, tuple)) else result[part]
        return result
    except (KeyError, IndexError, TypeError, ValueError) as error:
        position = location(path)
        raise ValueError(
            f"Unresolved reference {value!r} at arguments{position}. "
            f"For literal text, add {position!r} to request literal_paths."
        ) from error


def arguments(request, results):
    value = request.get("arguments", {})
    if not isinstance(value, dict):
        raise ValueError("arguments must be a JSON object.")
    paths = literal_paths(value, request.get("literal_paths", []))
    return resolve(value, results, paths)

"""Isolated native experiment; no production evaluation or binding policy is replaced."""

import ctypes as c
from pathlib import Path

import numpy as np

D = c.POINTER(c.c_double)


def load(path):
    library = c.CDLL(str(Path(path).resolve()))
    library.compare.argtypes = [D, c.c_int, D, c.c_int, c.c_int, c.c_int]
    library.compare.argtypes += [c.c_double, c.c_double, D, D, D]
    library.compare.restype = c.c_int
    library.corner_error.argtypes = [D, c.c_int, D, c.c_int]
    library.corner_error.restype = c.c_double
    return library


def pointer(array):
    return array.ctypes.data_as(D)


def geometry(library, rows, count):
    first, second = [np.ascontiguousarray(row[:, :3]) for row in rows]
    capacity = max(len(first) + len(second), count)
    vertices, axis, marker = np.empty((3 * capacity, 3)), np.empty(capacity), np.empty(3)
    inputs = (pointer(first), len(first), pointer(second), len(second), count, 2)
    n = library.compare(*inputs, 0.33, 0.5, pointer(vertices), pointer(axis), pointer(marker))
    grid = vertices[: 3 * n].reshape(3, n, 3)
    error = library.corner_error(pointer(first), len(first), pointer(grid[0]), n)
    return dict(vertices=grid.copy(), axis=axis[:n].copy(), marker=marker, error=error)

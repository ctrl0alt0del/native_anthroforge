"""Owned compiled expressions and batched typed input frames; evaluation is entirely C++."""

import ctypes as c
from typing import Any

import numpy as np

from anthroforge.core.expressions import ResultType, Symbol
from anthroforge.core.numeric_properties import validate_number

from .mesh import INT64, D, GeometryEngine, U, pointer

INT = c.POINTER(c.c_int)


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_expression_compile", [c.c_char_p, c.c_char_p, INT, c.c_int, U], U)
    engine.bind("af_expression_info", [U, INT, c.POINTER(U)])
    engine.bind("af_expression_evaluate", [U, INT64, D, c.c_int, INT64, D, U])
    engine.bind("af_expression_release", [U], None)


class Program:
    def __init__(self, engine: GeometryEngine, handle: int, symbols: tuple[Symbol, ...]) -> None:
        engine.check(not handle)
        self.engine, self.handle, self.symbols = engine, handle, symbols
        output, size = (c.c_int * 4)(), U()
        engine.check(engine.library.af_expression_info(handle, output, c.byref(size)))
        self.output = ResultType(output[0], output[1], output[2], bool(output[3]))
        self.bytes = size.value
        if engine.resource_observer is not None:
            engine.resource_observer(self)

    def __del__(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_expression_release(self.handle)

    def evaluate(self, values: dict[str, int | float], cancel: int = 0) -> int | float:
        return self.batch([values], cancel)[0].item()  # type: ignore[no-any-return]

    def batch(self, values: list[dict[str, int | float]], cancel: int = 0) -> Any:
        integers, reals = frames(self.symbols, values)
        output_integer, output_real = np.empty(len(values), dtype=np.int64), np.empty(len(values))
        arguments = (
            self.handle,
            integers.ctypes.data_as(INT64),
            pointer(reals),
            len(values),
            output_integer.ctypes.data_as(INT64),
            pointer(output_real),
            cancel,
        )
        self.engine.check(self.engine.library.af_expression_evaluate(*arguments))
        return output_integer if self.output.kind == 0 else output_real


def frames(symbols: tuple[Symbol, ...], values: list[dict[str, int | float]]) -> tuple[Any, Any]:
    integers = np.zeros((len(values), len(symbols)), dtype=np.int64)
    reals = np.zeros((len(values), len(symbols)), dtype=np.float64)
    for row, inputs in enumerate(values):
        if inputs.keys() != {symbol.name for symbol in symbols}:
            raise ValueError("Expression frame requires exactly the declared input names.")
        for column, symbol in enumerate(symbols):
            value = inputs[symbol.name]
            validate_number(value, symbol.numeric_type)
            if symbol.numeric_type == "INTEGER":
                integers[row, column] = value
            else:
                reals[row, column] = value
    return integers, reals


def compile(
    engine: GeometryEngine, source: str, symbols: tuple[Symbol, ...] = (), cancel: int = 0
) -> Program:
    if not source or len(source) > 8192 or "\0" in source:
        raise ValueError("Expression requires 1–8192 characters without embedded NUL.")
    key = (source, symbols)
    cached = engine.expressions.get(key)
    if cached is not None:
        return cached
    handle = compile_handle(engine, source, symbols, cancel)
    program = Program(engine, handle, symbols)
    size = program.bytes + len(source) * 4 + sum(len(s.name) * 4 for s in symbols) + 2048
    return engine.expressions.store(key, program, size)


def compile_handle(
    engine: GeometryEngine, source: str, symbols: tuple[Symbol, ...], cancel: int
) -> int:
    names = "\n".join(symbol.name for symbol in symbols).encode("ascii")
    types = np.ascontiguousarray([symbol.native_type for symbol in symbols], dtype=np.int32)
    return int(
        engine.library.af_expression_compile(
            source.encode("utf-8"), names, types.ctypes.data_as(INT), len(symbols), cancel
        )
    )

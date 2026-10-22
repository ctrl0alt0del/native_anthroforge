"""Application language qualification, independent of third-party parser defaults."""

from concurrent.futures import ThreadPoolExecutor

import pytest

from anthroforge.core.expressions import Symbol
from anthroforge.native import expressions
from anthroforge.native.mesh import NativeCancellation


@pytest.mark.parametrize(
    "source,expected,kind",
    [
        ("12", 12, 0),
        ("12.0", 12.0, 1),
        ("1e3", 1000.0, 1),
        ("5/2", 2.5, 1),
        ("2+3*4", 14, 0),
        ("2^3^2", 512, 0),
        ("-2^2", -4, 0),
        ("2^-2", 0.25, 1),
        ("round(2.5)", 3, 0),
        ("floor(-2.1)", -3, 0),
        ("ceil(2.1)", 3, 0),
        ("9007199254740993-9007199254740992", 1, 0),
        ("min(4,3)", 3, 0),
        ("clamp(4,0,3)", 3, 0),
        ("2 < 3", 1, 0),
        ("2 >= 3", 0, 0),
        ("abs(-3)", 3, 0),
        ("sqrt(4)", 2.0, 1),
        ("2**3", 8, 0),
    ],
)
def test_typed_arithmetic(session, source, expected, kind):
    program = expressions.compile(session.engine, source)
    assert program.output.kind == kind
    assert program.evaluate({}) == expected


@pytest.mark.parametrize(
    "source",
    [
        "1?2:3",
        "if(1,2,3)",
        "x=2",
        "x:=2",
        "while(1)",
        "1;2",
        "a[0]",
        "'hello'",
        "__import__(1)",
        "open(1)",
        "1,2",
        "sin()",
        "sin(1,2)",
        "1e+",
        "1.2.3",
        "",
    ],
)
def test_script_assignment_conditional_and_malformed_inputs_rejected(session, source):
    with pytest.raises(ValueError):
        expressions.compile(session.engine, source)


def test_units_and_expected_output_type(session):
    symbols = (Symbol("radius", dimension="LENGTH"), Symbol("theta", dimension="ANGLE"))
    program = expressions.compile(session.engine, "radius*cos(theta)", symbols)
    program.output.require("REAL", "LENGTH")
    assert program.evaluate(dict(radius=0.5, theta=0)) == 0.5
    with pytest.raises(ValueError, match="dimensions"):
        expressions.compile(session.engine, "radius+theta", symbols)
    with pytest.raises(ValueError, match="Integer"):
        expressions.compile(session.engine, "12.0").output.require("INTEGER", "SCALAR")
    expressions.compile(session.engine, "0").output.require("REAL", "LENGTH")


@pytest.mark.parametrize(
    "source",
    [
        "1/0",
        "sqrt(-1)",
        "log(0)",
        "exp(10000)",
        "9223372036854775807+1",
        "3037000500*3037000500",
        "2^63",
        "round(1e30)",
        "clamp(1,3,2)",
        "1%0",
    ],
)
def test_nonfinite_and_integer_overflow_fail(session, source):
    with pytest.raises(ValueError):
        expressions.compile(session.engine, source).evaluate({})


def test_immutable_program_can_evaluate_concurrent_owned_frames(session):
    program = expressions.compile(session.engine, "value*value+1", (Symbol("value", "INTEGER"),))
    with ThreadPoolExecutor(max_workers=4) as pool:
        values = list(pool.map(program.evaluate, [dict(value=i) for i in range(64)]))
    assert values == [i * i + 1 for i in range(64)]
    assert expressions.compile(session.engine, "value*value+1", program.symbols) is program


def test_native_batch_and_cancellation(session):
    program = expressions.compile(session.engine, "value/2", (Symbol("value", "INTEGER"),))
    assert list(program.batch([dict(value=1), dict(value=3)])) == [0.5, 1.5]
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        program.evaluate(dict(value=4), cancel.handle)


def test_bounded_cache_keeps_leased_program_usable(session):
    retained = expressions.compile(session.engine, "1")
    session.engine.expressions.capacity = 2
    for source in ("2", "3", "4"):
        expressions.compile(session.engine, source)
    assert len(session.engine.expressions.items) == 2
    session.engine.expressions.clear()
    assert retained.evaluate({}) == 1

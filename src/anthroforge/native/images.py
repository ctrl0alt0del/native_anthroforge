"""Qt-independent prepared image tiles and physical landmark calibration."""

import ctypes as c
from typing import Any

from .mesh import D, GeometryEngine, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_image_create", [c.c_char_p, c.c_int, c.c_int, U], U)
    engine.bind("af_image_info", [U, c.POINTER(U)])
    engine.bind("af_image_release", [U], None)
    engine.bind("af_image_calibration", [D, D, D, c.c_double, D])


class Image:
    def __init__(
        self, engine: GeometryEngine, rgba: bytes, width: int, height: int, cancel: int = 0
    ) -> None:
        if len(rgba) != width * height * 4:
            raise ValueError("Decoded RGBA bytes must match image dimensions.")
        configure(engine)
        self.engine, self.handle = (
            engine,
            engine.library.af_image_create(rgba, width, height, cancel),
        )
        engine.check(not self.handle)
        info = (U * 4)()
        engine.check(engine.library.af_image_info(self.handle, info))
        self.width, self.height, self.chunks, self.bytes = info

    def __del__(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_image_release(self.handle)


def calibrate(
    engine: GeometryEngine, frame: Any, size: Any, landmarks: Any, distance: float
) -> tuple[float, float]:
    configure(engine)
    frame, size, landmarks = doubles(frame), doubles(size), doubles(landmarks)
    if frame.size != 16 or size.size != 2 or landmarks.size != 4:
        raise ValueError("Invalid calibration dimensions.")
    output = (c.c_double * 2)()
    engine.check(
        engine.library.af_image_calibration(
            pointer(frame), pointer(size), pointer(landmarks), distance, output
        )
    )
    return output[0], output[1]

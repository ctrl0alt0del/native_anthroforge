"""Qt-independent prepared image tiles and physical landmark calibration."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import D, GeometryEngine, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_image_create", [c.c_char_p, c.c_int, c.c_int, U], U)
    engine.bind("af_image_info", [U, c.POINTER(U)])
    engine.bind("af_image_release", [U], None)
    engine.bind("af_image_calibration", [D, D, D, c.c_double, D])
    engine.bind("af_images_pick", [D, D, c.POINTER(c.c_int), c.c_int, D, D, D])
    engine.bind("af_images_axis_aligned", [D, c.c_int, D, c.POINTER(c.c_int)])


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


def pick(
    engine: GeometryEngine, frames: Any, sizes: Any, sides: Any, origin: Any, direction: Any
) -> Any:
    configure(engine)
    frames, sizes, sides = picking_arrays(frames, sizes, sides)
    origin, direction = picking_ray(origin, direction)
    output = np.empty((len(frames), 8))
    pointers = (pointer(frames), pointer(sizes), sides.ctypes.data_as(c.POINTER(c.c_int)))
    ray = (pointer(origin), pointer(direction))
    count = engine.library.af_images_pick(*pointers, len(frames), *ray, pointer(output))
    engine.check(count < 0)
    return output[:count]


def picking_ray(origin: Any, direction: Any) -> tuple[Any, Any]:
    origin, direction = doubles(origin), doubles(direction)
    if origin.size != 3 or direction.size != 3:
        raise ValueError("Image picking requires a 3D ray.")
    return origin, direction


def aligned(engine: GeometryEngine, frames: Any, direction: Any) -> Any:
    configure(engine)
    frames, direction = doubles(frames).reshape((-1, 16)), doubles(direction)
    if direction.size != 3:
        raise ValueError("Image view axis must contain three coordinates.")
    output = np.empty(len(frames), dtype=np.int32)
    engine.check(
        engine.library.af_images_axis_aligned(
            pointer(frames),
            len(frames),
            pointer(direction),
            output.ctypes.data_as(c.POINTER(c.c_int)),
        )
    )
    return output


def picking_arrays(frames: Any, sizes: Any, sides: Any) -> tuple[Any, Any, Any]:
    frames, sizes = doubles(frames).reshape((-1, 16)), doubles(sizes).reshape((-1, 2))
    sides = np.ascontiguousarray(sides, dtype=np.int32)
    if len(frames) != len(sizes) or sides.shape != (len(frames),):
        raise ValueError("Image picking arrays must describe the same images.")
    if np.any((sides < 0) | (sides > 2)):
        raise ValueError("Invalid image side visibility.")
    if not np.isfinite(frames).all() or not np.isfinite(sizes).all() or np.any(sizes <= 0):
        raise ValueError("Image picking requires finite frames and positive dimensions.")
    return frames, sizes, sides

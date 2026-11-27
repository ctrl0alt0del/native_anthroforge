"""Wait for the observable frame barrier, independent of automatic mesh chunk count."""

from time import monotonic, sleep


def publish(controller):
    deadline = monotonic() + 10
    while monotonic() < deadline:
        controller.process_tick()
        controller.frame_presented()
        if all(displayed(model) for model in controller.geometry_models()):
            return
        sleep(0.001)
    raise AssertionError("Viewport geometry did not reach its frame publication barrier")


def displayed(model):
    return not model.pending and {row["key"] for row in model.displayed} == set(model.wanted)

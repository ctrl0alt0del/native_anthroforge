"""Reproduce the current exact-consumer failure independently of the transport prototype."""

import json

import scene

from anthroforge.application.session import Session


def check(session):
    objects = scene.create(session)
    tissue = session.command("tissue.create", source=objects["exact"], preset="CUSTOM")
    session.wait()
    anchor = scene.attachment(session, tissue, "TISSUE_BASE")
    before = session.document.object(anchor)
    scene.move(session, objects["supports"][-1], [0, 0, 0])
    after = session.document.object(anchor)
    assert before.result.status == "ready" and after.result.status == "failed"
    assert "topology changed" in after.result.error and before.binding == after.binding
    return dict(
        error=after.result.error, binding_preserved=True, source_errors=session.scheduler.errors
    )


def main():
    session = Session()
    try:
        print(json.dumps(check(session), indent=2))
    finally:
        session.close()


if __name__ == "__main__":
    main()

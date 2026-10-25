"""Migrate effective attachment policies; raw unset Blender flags are not defaults."""


def effective_backsolve(row):
    if "owner_backsolve_effective" not in row:
        raise ValueError("Recapture shortcut inventory with effective Backsolve policies.")
    return row["owner_backsolve_effective"]


def policy(row):
    from skeleton_shortcut_pelvis import override

    return dict(
        scope=row["owner_id"],
        backsolve=effective_backsolve(row),
        descendants=[override(item) for item in row["overrides"]],
    )


def apply(session, row, mapping):
    settings = policy(row)
    if "driver" in mapping:
        session.command("driver.configure", driver=mapping["driver"], changes=dict(policy=settings))
    else:
        session.command("shortcut.configure", reference=mapping["reference"], policy=settings)

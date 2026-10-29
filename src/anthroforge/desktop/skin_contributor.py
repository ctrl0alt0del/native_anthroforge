"""Desktop adapter for shared effective skin settings and contributor availability."""

from anthroforge.application import skin_contributor_queries


def describe(session, target):
    return skin_contributor_queries.inspect(session, target)

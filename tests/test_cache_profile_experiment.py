"""Evidence classification must not confuse later misses with concurrent work."""

from collections import Counter, defaultdict

from tools.summarize_cache_profile import observe, track


def event(action, job, thread=1, key="shared"):
    return dict(
        name=action, tid=thread, args=dict(cache="fixture", key=key, job=job, reason="byte_budget")
    )


def test_misses_overlap_only_until_a_result_is_installed():
    pending, overlaps = {}, []
    observe(event("miss", "a"), pending, overlaps)
    observe(event("miss", "b", 2), pending, overlaps)
    assert len(overlaps) == 1
    observe(event("insert", "a"), pending, overlaps)
    observe(event("miss", "c"), pending, overlaps)
    assert len(overlaps) == 1


def test_separate_keys_and_unattributed_threads_remain_distinct():
    pending, overlaps = {}, []
    observe(event("miss", "", 1), pending, overlaps)
    observe(event("miss", "", 2, "different"), pending, overlaps)
    assert not overlaps
    observe(event("miss", "", 2), pending, overlaps)
    assert len(overlaps) == 1


def test_evicted_rebuilds_are_separate_from_first_misses():
    counts, keys, evicted, rebuilt = defaultdict(Counter), defaultdict(set), set(), Counter()
    for action in ("miss", "insert", "evict", "miss"):
        track(event(action, "a"), counts, keys, evicted, rebuilt)
    assert counts["fixture"]["miss"] == 2
    assert rebuilt["fixture"] == 1

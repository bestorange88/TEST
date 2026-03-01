"""Tests for constraints module: slot detection, config building, enumeration."""

import pytest
from core.constraints import (
    detect_unknown_slots,
    build_slot_config,
    enumerate_combinations,
    SlotConfig,
)


class TestDetectUnknownSlots:
    def test_all_known(self):
        words = ["word"] * 12
        assert detect_unknown_slots(words) == []

    def test_all_unknown(self):
        words = [None] * 12
        assert detect_unknown_slots(words) == list(range(12))

    def test_mixed(self):
        words = ["a", None, "c", "", "e", None, "g", "h", "i", "j", "k", "l"]
        assert detect_unknown_slots(words) == [1, 3, 5]


class TestBuildSlotConfig:
    def test_global_candidates(self):
        config = build_slot_config([1, 3], global_candidates=["apple", "banana"])
        assert config.unknown_positions == [1, 3]
        assert config.total_combinations == 4  # 2 * 2

    def test_per_slot_candidates(self):
        config = build_slot_config(
            [0, 2],
            per_slot_candidates={0: ["x", "y"], 2: ["a", "b", "c"]},
        )
        assert config.total_combinations == 6  # 2 * 3

    def test_no_candidates_raises(self):
        with pytest.raises(ValueError, match="没有候选词"):
            build_slot_config([0], global_candidates=None, per_slot_candidates=None)

    def test_empty_candidates_raises(self):
        with pytest.raises(ValueError, match="没有候选词"):
            build_slot_config([0], global_candidates=[])


class TestEnumerateCombinations:
    def test_single_slot(self):
        known = ["a", None, "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"]
        config = SlotConfig(slot_candidates={1: ["x", "y"]})
        combos = list(enumerate_combinations(known, config))
        assert len(combos) == 2
        assert combos[0][1] == "x"
        assert combos[1][1] == "y"
        # Other positions unchanged
        assert combos[0][0] == "a"
        assert combos[0][2] == "c"

    def test_two_slots(self):
        known = [None, "b", None, "d", "e", "f", "g", "h", "i", "j", "k", "l"]
        config = SlotConfig(slot_candidates={0: ["a1", "a2"], 2: ["c1", "c2", "c3"]})
        combos = list(enumerate_combinations(known, config))
        assert len(combos) == 6  # 2 * 3

    def test_preserves_known_words(self):
        known = ["w1", None, "w3", "w4", "w5", "w6", "w7", "w8", "w9", "w10", "w11", "w12"]
        config = SlotConfig(slot_candidates={1: ["candidate"]})
        combos = list(enumerate_combinations(known, config))
        assert len(combos) == 1
        assert combos[0] == ["w1", "candidate", "w3", "w4", "w5", "w6", "w7", "w8", "w9", "w10", "w11", "w12"]

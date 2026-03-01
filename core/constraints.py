"""Unknown-slot detection, candidate parsing, combination estimation, and cartesian product generation."""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field


@dataclass
class SlotConfig:
    """Configuration for unknown mnemonic slots and their candidate words."""
    # Mapping: slot_index (0-based) -> list of candidate words for that slot
    slot_candidates: dict[int, list[str]] = field(default_factory=dict)

    @property
    def unknown_positions(self) -> list[int]:
        return sorted(self.slot_candidates.keys())

    @property
    def total_combinations(self) -> int:
        if not self.slot_candidates:
            return 0
        total = 1
        for candidates in self.slot_candidates.values():
            total *= len(candidates)
        return total


def detect_unknown_slots(words: list[str | None]) -> list[int]:
    """Return indices (0-based) of unknown/empty word positions in 12-word list."""
    unknown = []
    for i, w in enumerate(words):
        if w is None or w.strip() == "":
            unknown.append(i)
    return unknown


def build_slot_config(
    unknown_slots: list[int],
    global_candidates: list[str] | None = None,
    per_slot_candidates: dict[int, list[str]] | None = None,
) -> SlotConfig:
    """Build a SlotConfig from either global or per-slot candidate lists.

    Args:
        unknown_slots: list of 0-based indices for unknown positions.
        global_candidates: if provided, used for all unknown slots.
        per_slot_candidates: if provided, maps slot index -> candidates.

    Returns:
        SlotConfig with slot_candidates populated.

    Raises:
        ValueError: if any unknown slot has zero candidates.
    """
    config = SlotConfig()
    for idx in unknown_slots:
        if per_slot_candidates and idx in per_slot_candidates:
            cands = per_slot_candidates[idx]
        elif global_candidates:
            cands = list(global_candidates)
        else:
            cands = []
        if not cands:
            raise ValueError(
                f"位置 {idx + 1} 没有候选词。请先填写候选词集合。"
            )
        config.slot_candidates[idx] = cands
    return config


def enumerate_combinations(
    known_words: list[str | None],
    slot_config: SlotConfig,
):
    """Generator yielding complete 12-word lists by filling unknown slots via cartesian product.

    Args:
        known_words: 12-element list; None/empty for unknown slots.
        slot_config: SlotConfig with candidates per unknown slot.

    Yields:
        list[str]: complete 12-word mnemonic candidate.
    """
    positions = slot_config.unknown_positions
    candidate_lists = [slot_config.slot_candidates[p] for p in positions]

    base = list(known_words)
    for combo in itertools.product(*candidate_lists):
        result = list(base)
        for pos, word in zip(positions, combo):
            result[pos] = word
        yield result

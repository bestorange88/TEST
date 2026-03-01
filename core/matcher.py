"""Address matching logic: exact, prefix, suffix."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MatchResult:
    """Result of a successful address match."""
    index: int
    address: str
    match_type: str  # "exact", "prefix", "suffix"


def match_addresses(
    derived: list[tuple[int, str]],
    known_addresses: set[str],
    prefix: str = "",
    suffix: str = "",
    use_prefix: bool = False,
    use_suffix: bool = False,
) -> list[MatchResult]:
    """Match derived addresses against known addresses or prefix/suffix rules.

    Args:
        derived: list of (index, address) from derivation.
        known_addresses: set of user-provided known TRON addresses.
        prefix: address prefix to match (if use_prefix is True).
        suffix: address suffix to match (if use_suffix is True).
        use_prefix: enable prefix matching.
        use_suffix: enable suffix matching.

    Returns:
        List of MatchResult for all matches found.
    """
    results: list[MatchResult] = []
    for idx, addr in derived:
        # Exact match takes priority
        if addr in known_addresses:
            results.append(MatchResult(index=idx, address=addr, match_type="exact"))
            continue
        # Prefix match
        if use_prefix and prefix and addr.startswith(prefix):
            results.append(MatchResult(index=idx, address=addr, match_type="prefix"))
            continue
        # Suffix match
        if use_suffix and suffix and addr.endswith(suffix):
            results.append(MatchResult(index=idx, address=addr, match_type="suffix"))
            continue
    return results

"""Tests for BIP39 checksum validation."""

import pytest
from core.checksum import is_valid_mnemonic


# A known-valid 12-word BIP39 mnemonic
VALID_MNEMONIC = [
    "abandon", "abandon", "abandon", "abandon",
    "abandon", "abandon", "abandon", "abandon",
    "abandon", "abandon", "abandon", "about",
]

# Invalid checksum (last word changed)
INVALID_CHECKSUM = [
    "abandon", "abandon", "abandon", "abandon",
    "abandon", "abandon", "abandon", "abandon",
    "abandon", "abandon", "abandon", "abandon",
]


class TestChecksum:
    def test_valid_mnemonic(self):
        assert is_valid_mnemonic(VALID_MNEMONIC) is True

    def test_invalid_checksum(self):
        assert is_valid_mnemonic(INVALID_CHECKSUM) is False

    def test_wrong_length(self):
        assert is_valid_mnemonic(VALID_MNEMONIC[:11]) is False
        assert is_valid_mnemonic(VALID_MNEMONIC + ["zoo"]) is False

    def test_empty(self):
        assert is_valid_mnemonic([]) is False

    def test_non_bip39_word(self):
        bad = list(VALID_MNEMONIC)
        bad[0] = "notaword"
        assert is_valid_mnemonic(bad) is False

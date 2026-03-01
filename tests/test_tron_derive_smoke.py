"""Smoke tests for TRON address derivation."""

import pytest
from core.tron_derive import derive_tron_addresses, parse_derivation_path


# Known mnemonic for testing (the "abandon" mnemonic)
TEST_MNEMONIC = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"


class TestParseDerivationPath:
    def test_valid_path(self):
        result = parse_derivation_path("m/44'/195'/0'/0/i")
        assert result is not None

    def test_invalid_purpose(self):
        with pytest.raises(ValueError, match="Purpose"):
            parse_derivation_path("m/49'/195'/0'/0/i")

    def test_invalid_coin(self):
        with pytest.raises(ValueError, match="Coin type"):
            parse_derivation_path("m/44'/60'/0'/0/i")

    def test_too_short(self):
        with pytest.raises(ValueError, match="格式无效"):
            parse_derivation_path("m/44'/195'")


class TestDeriveTronAddresses:
    def test_derive_returns_addresses(self):
        addresses = derive_tron_addresses(TEST_MNEMONIC, index_start=0, index_end=2)
        assert len(addresses) == 3
        for idx, addr in addresses:
            assert isinstance(idx, int)
            assert isinstance(addr, str)
            assert addr.startswith("T"), f"TRON address should start with T: {addr}"

    def test_derive_index_range(self):
        addresses = derive_tron_addresses(TEST_MNEMONIC, index_start=5, index_end=10)
        assert len(addresses) == 6
        indices = [idx for idx, _ in addresses]
        assert indices == [5, 6, 7, 8, 9, 10]

    def test_derive_with_passphrase_differs(self):
        addr_no_pass = derive_tron_addresses(TEST_MNEMONIC, index_start=0, index_end=0)
        addr_with_pass = derive_tron_addresses(
            TEST_MNEMONIC, passphrase="test", index_start=0, index_end=0
        )
        assert addr_no_pass[0][1] != addr_with_pass[0][1]

    def test_deterministic(self):
        addr1 = derive_tron_addresses(TEST_MNEMONIC, index_start=0, index_end=0)
        addr2 = derive_tron_addresses(TEST_MNEMONIC, index_start=0, index_end=0)
        assert addr1[0][1] == addr2[0][1]

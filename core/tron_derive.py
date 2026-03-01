"""TRON address derivation from BIP39 mnemonic using bip_utils."""

from __future__ import annotations

from bip_utils import (
    Bip39SeedGenerator,
    Bip39MnemonicValidator,
    Bip39Languages,
    Bip44,
    Bip44Coins,
    Bip44Changes,
)


def parse_derivation_path(path: str) -> tuple[int, int, int]:
    """Parse a BIP44-style derivation path for TRON.

    Expected format: m/44'/195'/account'/change/index
    Returns (account, change, -1) where -1 means index is variable.
    For validation purposes only.

    Raises:
        ValueError: if path format is invalid.
    """
    parts = path.strip().split("/")
    if len(parts) < 5:
        raise ValueError(f"派生路径格式无效: {path}")
    if parts[0] != "m":
        raise ValueError(f"派生路径必须以 m 开头: {path}")
    # Validate purpose = 44'
    purpose = parts[1].replace("'", "")
    if purpose != "44":
        raise ValueError(f"Purpose 必须为 44: {path}")
    # Validate coin_type = 195' (TRON)
    coin = parts[2].replace("'", "")
    if coin != "195":
        raise ValueError(f"Coin type 必须为 195 (TRON): {path}")
    return (0, 0, -1)  # simplified validation


def derive_tron_addresses(
    mnemonic: str,
    passphrase: str = "",
    index_start: int = 0,
    index_end: int = 20,
) -> list[tuple[int, str]]:
    """Derive TRON addresses from a mnemonic for index range [start, end].

    Args:
        mnemonic: 12-word BIP39 mnemonic string.
        passphrase: optional BIP39 passphrase.
        index_start: starting address index (inclusive).
        index_end: ending address index (inclusive).

    Returns:
        List of (index, tron_address) tuples.
    """
    seed = Bip39SeedGenerator(mnemonic).Generate(passphrase)
    bip44_ctx = Bip44.FromSeed(seed, Bip44Coins.TRON)
    account = bip44_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)

    addresses: list[tuple[int, str]] = []
    for i in range(index_start, index_end + 1):
        addr_ctx = account.AddressIndex(i)
        address = addr_ctx.PublicKey().ToAddress()
        addresses.append((i, address))
    return addresses

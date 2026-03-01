"""BIP39 checksum validation wrapper."""

from bip_utils import Bip39MnemonicValidator, Bip39Languages


def is_valid_mnemonic(words: list[str]) -> bool:
    """Check if a 12-word mnemonic passes BIP39 checksum validation.

    Args:
        words: list of 12 English BIP39 words.

    Returns:
        True if checksum is valid.
    """
    if len(words) != 12:
        return False
    mnemonic_str = " ".join(words)
    try:
        Bip39MnemonicValidator(Bip39Languages.ENGLISH).Validate(mnemonic_str)
        return True
    except Exception:
        return False

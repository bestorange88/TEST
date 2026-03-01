"""BIP39 English wordlist loading and validation."""

from bip_utils import Bip39MnemonicDecoder, Bip39Languages

_WORDLIST: list[str] | None = None


def get_wordlist() -> list[str]:
    """Return the BIP39 English wordlist (2048 words), cached after first call."""
    global _WORDLIST
    if _WORDLIST is None:
        decoder = Bip39MnemonicDecoder(Bip39Languages.ENGLISH)
        wl = decoder.m_words_list
        _WORDLIST = [wl.GetWordAtIdx(i) for i in range(wl.Length())]
    return _WORDLIST


def is_valid_bip39_word(word: str) -> bool:
    """Check if a single word is in the BIP39 English wordlist."""
    return word.lower().strip() in get_wordlist()


def validate_candidates(candidates: list[str]) -> tuple[list[str], list[str]]:
    """Validate a list of candidate words against BIP39 wordlist.

    Returns:
        (valid_words, invalid_words)
    """
    wordlist = set(get_wordlist())
    valid = []
    invalid = []
    for w in candidates:
        w_clean = w.lower().strip()
        if not w_clean:
            continue
        if w_clean in wordlist:
            valid.append(w_clean)
        else:
            invalid.append(w_clean)
    return valid, invalid

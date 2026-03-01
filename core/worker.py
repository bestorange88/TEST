"""Background worker for mnemonic enumeration, validation, derivation, and matching."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime

from PySide6.QtCore import QObject, Signal, QThread

from core.checksum import is_valid_mnemonic
from core.constraints import SlotConfig, enumerate_combinations
from core.tron_derive import derive_tron_addresses
from core.matcher import match_addresses, MatchResult


@dataclass
class HitRecord:
    """A single successful match record."""
    timestamp: str
    mnemonic: str
    index: int
    address: str
    match_type: str


class RecoveryWorker(QObject):
    """Worker that runs mnemonic enumeration in a background thread.

    Signals:
        progress(tested: int, total: int, speed: float)
        hit(HitRecord)
        finished(tested: int, hits: int)
        error(str)
    """

    progress = Signal(int, int, float)  # tested, total, speed
    hit = Signal(object)  # HitRecord
    finished = Signal(int, int)  # tested, total_hits
    error = Signal(str)

    def __init__(
        self,
        known_words: list[str | None],
        slot_config: SlotConfig,
        known_addresses: set[str],
        passphrase: str = "",
        index_start: int = 0,
        index_end: int = 20,
        prefix: str = "",
        suffix: str = "",
        use_prefix: bool = False,
        use_suffix: bool = False,
        stop_on_hit: bool = True,
    ):
        super().__init__()
        self._known_words = known_words
        self._slot_config = slot_config
        self._known_addresses = known_addresses
        self._passphrase = passphrase
        self._index_start = index_start
        self._index_end = index_end
        self._prefix = prefix
        self._suffix = suffix
        self._use_prefix = use_prefix
        self._use_suffix = use_suffix
        self._stop_on_hit = stop_on_hit
        self._stopped = False

    def stop(self):
        """Request the worker to stop."""
        self._stopped = True

    def run(self):
        """Main worker loop: enumerate, validate checksum, derive, match."""
        try:
            total = self._slot_config.total_combinations
            if total == 0:
                # No unknown slots: just validate the given mnemonic
                total = 1

            tested = 0
            hits = 0
            start_time = time.time()
            last_progress_time = start_time

            if total == 0:
                self.finished.emit(0, 0)
                return

            # If no unknown slots, treat the known words as the only candidate
            if not self._slot_config.unknown_positions:
                combo_gen = [list(self._known_words)]  # type: ignore
            else:
                combo_gen = enumerate_combinations(self._known_words, self._slot_config)

            for words in combo_gen:
                if self._stopped:
                    break

                tested += 1

                # BIP39 checksum validation (fast filter)
                if not is_valid_mnemonic(words):
                    # Emit progress periodically
                    now = time.time()
                    if now - last_progress_time >= 0.3:
                        elapsed = now - start_time
                        speed = tested / elapsed if elapsed > 0 else 0
                        self.progress.emit(tested, total, speed)
                        last_progress_time = now
                    continue

                # Derive TRON addresses
                mnemonic_str = " ".join(words)
                try:
                    derived = derive_tron_addresses(
                        mnemonic_str,
                        passphrase=self._passphrase,
                        index_start=self._index_start,
                        index_end=self._index_end,
                    )
                except Exception:
                    continue

                # Match against known addresses
                matches = match_addresses(
                    derived,
                    self._known_addresses,
                    prefix=self._prefix,
                    suffix=self._suffix,
                    use_prefix=self._use_prefix,
                    use_suffix=self._use_suffix,
                )

                for m in matches:
                    hits += 1
                    record = HitRecord(
                        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        mnemonic=mnemonic_str,
                        index=m.index,
                        address=m.address,
                        match_type=m.match_type,
                    )
                    self.hit.emit(record)

                    if self._stop_on_hit:
                        self._stopped = True
                        break

                # Progress update
                now = time.time()
                if now - last_progress_time >= 0.3:
                    elapsed = now - start_time
                    speed = tested / elapsed if elapsed > 0 else 0
                    self.progress.emit(tested, total, speed)
                    last_progress_time = now

                if self._stopped:
                    break

            # Final progress
            elapsed = time.time() - start_time
            speed = tested / elapsed if elapsed > 0 else 0
            self.progress.emit(tested, total, speed)
            self.finished.emit(tested, hits)

        except Exception as e:
            self.error.emit(str(e))

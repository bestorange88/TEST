"""12-slot mnemonic word input grid widget."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QGroupBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
)
from PySide6.QtCore import Signal

from core.bip39_words import is_valid_bip39_word


class MnemonicGrid(QGroupBox):
    """A group of 12 input fields for BIP39 mnemonic words.

    Supports:
    - Single-word entry per field
    - Paste a full mnemonic into any field to auto-split
    - Visual validation (red border for invalid BIP39 words)

    Signals:
        words_changed: emitted whenever any word field changes.
    """

    words_changed = Signal()

    def __init__(self, parent=None):
        super().__init__("A) 助记词 12 格输入", parent)
        self._inputs: list[QLineEdit] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        grid = QGridLayout()
        for i in range(12):
            row, col = divmod(i, 4)
            label = QLabel(f"#{i + 1}")
            line = QLineEdit()
            line.setPlaceholderText(f"Word {i + 1}")
            line.setMaximumWidth(200)
            line.textChanged.connect(self._on_text_changed)
            # Connect paste detection
            line.setProperty("slot_index", i)
            self._inputs.append(line)

            h = QHBoxLayout()
            h.addWidget(label)
            h.addWidget(line)
            grid.addLayout(h, row, col)

        layout.addLayout(grid)

        # Clear button
        btn_clear = QPushButton("清空所有词位")
        btn_clear.clicked.connect(self.clear_all)
        layout.addWidget(btn_clear)

        # Install event filter for paste detection
        for inp in self._inputs:
            inp.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Detect paste events: if pasted text contains spaces, auto-split into slots."""
        from PySide6.QtCore import QEvent
        from PySide6.QtWidgets import QApplication

        if event.type() == QEvent.Type.KeyPress:
            from PySide6.QtCore import Qt
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_V:
                clipboard = QApplication.clipboard()
                text = clipboard.text().strip()
                if " " in text:
                    words = text.split()
                    slot_idx = obj.property("slot_index")
                    if slot_idx is not None:
                        self._fill_from(int(slot_idx), words)
                        return True  # consume event
        return super().eventFilter(obj, event)

    def _fill_from(self, start: int, words: list[str]):
        """Fill fields starting from `start` with the given words."""
        for i, w in enumerate(words):
            idx = start + i
            if idx >= 12:
                break
            self._inputs[idx].setText(w.strip().lower())
        self.words_changed.emit()

    def _on_text_changed(self):
        """Validate each non-empty field and update styling."""
        for inp in self._inputs:
            text = inp.text().strip().lower()
            if text:
                if is_valid_bip39_word(text):
                    inp.setStyleSheet("")
                else:
                    inp.setStyleSheet("border: 2px solid red;")
            else:
                inp.setStyleSheet("")
        self.words_changed.emit()

    def get_words(self) -> list[str | None]:
        """Return list of 12 words; None for empty slots."""
        result: list[str | None] = []
        for inp in self._inputs:
            text = inp.text().strip().lower()
            result.append(text if text else None)
        return result

    def get_unknown_indices(self) -> list[int]:
        """Return 0-based indices of empty/unknown slots."""
        return [i for i, inp in enumerate(self._inputs) if not inp.text().strip()]

    def clear_all(self):
        """Clear all input fields."""
        for inp in self._inputs:
            inp.blockSignals(True)
            inp.clear()
            inp.setStyleSheet("")
            inp.blockSignals(False)
        self.words_changed.emit()

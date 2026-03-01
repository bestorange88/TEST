"""Candidate words configuration panel."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QTextEdit,
    QLineEdit,
    QButtonGroup,
    QWidget,
    QScrollArea,
    QSpinBox,
    QFormLayout,
)
from PySide6.QtCore import Signal

from core.bip39_words import validate_candidates


class CandidatesPanel(QGroupBox):
    """Panel for configuring candidate words for unknown mnemonic slots.

    Two modes:
    1. Global candidate pool (one list for all unknown slots)
    2. Per-slot candidates (separate list per unknown slot)

    Signals:
        candidates_changed: emitted when candidate configuration changes.
    """

    candidates_changed = Signal()

    def __init__(self, parent=None):
        super().__init__("B) 候选词配置", parent)
        self._mode = "global"  # "global" or "per_slot"
        self._unknown_slots: list[int] = []
        self._per_slot_edits: dict[int, QTextEdit] = {}
        self._combo_limit = 200000
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Mode selection
        mode_layout = QHBoxLayout()
        self._radio_global = QRadioButton("全局候选池")
        self._radio_per_slot = QRadioButton("按位置候选")
        self._radio_global.setChecked(True)
        btn_group = QButtonGroup(self)
        btn_group.addButton(self._radio_global)
        btn_group.addButton(self._radio_per_slot)
        self._radio_global.toggled.connect(self._on_mode_changed)
        mode_layout.addWidget(self._radio_global)
        mode_layout.addWidget(self._radio_per_slot)
        layout.addLayout(mode_layout)

        # Combination limit
        limit_layout = QHBoxLayout()
        limit_layout.addWidget(QLabel("组合数上限:"))
        self._limit_spin = QSpinBox()
        self._limit_spin.setRange(1, 100_000_000)
        self._limit_spin.setValue(self._combo_limit)
        self._limit_spin.valueChanged.connect(self._on_candidates_edited)
        limit_layout.addWidget(self._limit_spin)
        layout.addLayout(limit_layout)

        # Combination estimate label
        self._combo_label = QLabel("组合数估算: 0")
        self._combo_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self._combo_label)

        # Global candidate text area
        self._global_edit = QTextEdit()
        self._global_edit.setPlaceholderText(
            "每行一个候选词，或用逗号分隔。\n例如:\nabout\nabove\nabsent"
        )
        self._global_edit.setMaximumHeight(150)
        self._global_edit.textChanged.connect(self._on_candidates_edited)
        layout.addWidget(self._global_edit)

        # Per-slot container (hidden by default)
        self._per_slot_scroll = QScrollArea()
        self._per_slot_container = QWidget()
        self._per_slot_layout = QVBoxLayout(self._per_slot_container)
        self._per_slot_scroll.setWidget(self._per_slot_container)
        self._per_slot_scroll.setWidgetResizable(True)
        self._per_slot_scroll.setMaximumHeight(250)
        self._per_slot_scroll.hide()
        layout.addWidget(self._per_slot_scroll)

    def _on_mode_changed(self, checked: bool):
        if self._radio_global.isChecked():
            self._mode = "global"
            self._global_edit.show()
            self._per_slot_scroll.hide()
        else:
            self._mode = "per_slot"
            self._global_edit.hide()
            self._per_slot_scroll.show()
        self._on_candidates_edited()

    def update_unknown_slots(self, slots: list[int]):
        """Update the list of unknown slot indices and rebuild per-slot editors."""
        self._unknown_slots = slots
        self._rebuild_per_slot_editors()
        self._on_candidates_edited()

    def _rebuild_per_slot_editors(self):
        """Rebuild the per-slot candidate text editors."""
        # Clear old editors
        for edit in self._per_slot_edits.values():
            edit.textChanged.disconnect(self._on_candidates_edited)
        self._per_slot_edits.clear()

        # Clear layout
        while self._per_slot_layout.count():
            item = self._per_slot_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Create new editors
        for idx in self._unknown_slots:
            label = QLabel(f"位置 #{idx + 1} 候选词:")
            edit = QTextEdit()
            edit.setPlaceholderText(f"位置 #{idx + 1} 的候选词（每行一个或逗号分隔）")
            edit.setMaximumHeight(80)
            edit.textChanged.connect(self._on_candidates_edited)
            self._per_slot_edits[idx] = edit
            self._per_slot_layout.addWidget(label)
            self._per_slot_layout.addWidget(edit)

    def _on_candidates_edited(self):
        self._combo_limit = self._limit_spin.value()
        self._update_combo_estimate()
        self.candidates_changed.emit()

    def _parse_text(self, text: str) -> list[str]:
        """Parse candidate words from text (comma or newline separated)."""
        words = []
        for line in text.strip().split("\n"):
            for w in line.split(","):
                w = w.strip().lower()
                if w:
                    words.append(w)
        return list(dict.fromkeys(words))  # deduplicate preserving order

    def _update_combo_estimate(self):
        """Update the combination estimate label."""
        if not self._unknown_slots:
            self._combo_label.setText("组合数估算: 0（无未知位）")
            return

        total = 1
        if self._mode == "global":
            candidates = self._parse_text(self._global_edit.toPlainText())
            n = len(candidates) if candidates else 0
            for _ in self._unknown_slots:
                total *= max(n, 1)
            if n == 0:
                total = 0
        else:
            for idx in self._unknown_slots:
                edit = self._per_slot_edits.get(idx)
                if edit:
                    cands = self._parse_text(edit.toPlainText())
                    total *= max(len(cands), 1)
                    if not cands:
                        total = 0
                        break

        limit = self._limit_spin.value()
        color = "red" if total > limit else "green"
        self._combo_label.setText(
            f'组合数估算: <span style="color:{color};">{total:,}</span>'
            f' （上限: {limit:,}）'
        )

    def get_combo_limit(self) -> int:
        return self._limit_spin.value()

    def get_global_candidates(self) -> list[str] | None:
        """Return parsed global candidates if in global mode, else None."""
        if self._mode != "global":
            return None
        return self._parse_text(self._global_edit.toPlainText()) or None

    def get_per_slot_candidates(self) -> dict[int, list[str]] | None:
        """Return per-slot candidates if in per-slot mode, else None."""
        if self._mode != "per_slot":
            return None
        result: dict[int, list[str]] = {}
        for idx, edit in self._per_slot_edits.items():
            cands = self._parse_text(edit.toPlainText())
            if cands:
                result[idx] = cands
        return result or None

    def get_total_combinations(self) -> int:
        """Calculate total combinations from current config."""
        if not self._unknown_slots:
            return 1  # just validate existing mnemonic

        total = 1
        if self._mode == "global":
            candidates = self._parse_text(self._global_edit.toPlainText())
            n = len(candidates) if candidates else 0
            if n == 0:
                return 0
            for _ in self._unknown_slots:
                total *= n
        else:
            for idx in self._unknown_slots:
                edit = self._per_slot_edits.get(idx)
                if edit:
                    cands = self._parse_text(edit.toPlainText())
                    if not cands:
                        return 0
                    total *= len(cands)
                else:
                    return 0
        return total

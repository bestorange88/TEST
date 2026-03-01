"""Main application window assembling all panels."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QTextEdit,
    QCheckBox,
    QSpinBox,
    QFormLayout,
    QMessageBox,
    QSplitter,
)
from PySide6.QtCore import Qt, QThread

from ui.mnemonic_grid import MnemonicGrid
from ui.candidates_panel import CandidatesPanel
from ui.results_table import ResultsTable
from core.bip39_words import is_valid_bip39_word, validate_candidates
from core.constraints import (
    detect_unknown_slots,
    build_slot_config,
)
from core.tron_derive import parse_derivation_path
from core.worker import RecoveryWorker, HitRecord


class MainWindow(QMainWindow):
    """Main window for the TRON Mnemonic Recovery Tool."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TRON 助记词缺词补全工具（约束式枚举）")
        self.setMinimumSize(1000, 800)

        self._worker: RecoveryWorker | None = None
        self._worker_thread: QThread | None = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Disclaimer banner
        disclaimer = QLabel(
            "⚠ 本工具仅用于找回用户自有钱包助记词。"
            "必须提供候选词集合，禁止全量枚举。"
            "所有操作离线完成，严禁用于任何未授权用途。"
        )
        disclaimer.setStyleSheet(
            "background-color: #fff3cd; color: #856404; padding: 8px; "
            "border: 1px solid #ffc107; border-radius: 4px; font-weight: bold;"
        )
        disclaimer.setWordWrap(True)
        main_layout.addWidget(disclaimer)

        # Top half: Mnemonic grid + Candidates panel
        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        self._mnemonic_grid = MnemonicGrid()
        top_splitter.addWidget(self._mnemonic_grid)

        self._candidates_panel = CandidatesPanel()
        top_splitter.addWidget(self._candidates_panel)

        top_splitter.setStretchFactor(0, 3)
        top_splitter.setStretchFactor(1, 2)
        main_layout.addWidget(top_splitter)

        # Section C: Verification target & derivation settings
        self._target_group = QGroupBox("C) 验证目标与派生设置")
        target_layout = QVBoxLayout(self._target_group)

        # Known addresses
        addr_label = QLabel("已知 TRON 地址（每行一个）:")
        self._addr_edit = QTextEdit()
        self._addr_edit.setPlaceholderText("T... (每行一个地址)")
        self._addr_edit.setMaximumHeight(80)
        target_layout.addWidget(addr_label)
        target_layout.addWidget(self._addr_edit)

        # Prefix/suffix matching
        prefix_layout = QHBoxLayout()
        self._use_prefix_cb = QCheckBox("前缀匹配")
        self._prefix_edit = QLineEdit()
        self._prefix_edit.setPlaceholderText("地址前缀（如 TXyz...）")
        self._prefix_edit.setEnabled(False)
        self._use_prefix_cb.toggled.connect(self._prefix_edit.setEnabled)
        prefix_layout.addWidget(self._use_prefix_cb)
        prefix_layout.addWidget(self._prefix_edit)

        self._use_suffix_cb = QCheckBox("后缀匹配")
        self._suffix_edit = QLineEdit()
        self._suffix_edit.setPlaceholderText("地址后缀")
        self._suffix_edit.setEnabled(False)
        self._use_suffix_cb.toggled.connect(self._suffix_edit.setEnabled)
        prefix_layout.addWidget(self._use_suffix_cb)
        prefix_layout.addWidget(self._suffix_edit)
        target_layout.addLayout(prefix_layout)

        # Derivation path settings
        derive_layout = QHBoxLayout()

        form = QFormLayout()
        self._path_edit = QLineEdit("m/44'/195'/0'/0/i")
        form.addRow("派生路径:", self._path_edit)
        derive_layout.addLayout(form)

        form2 = QFormLayout()
        self._index_start = QSpinBox()
        self._index_start.setRange(0, 1000)
        self._index_start.setValue(0)
        form2.addRow("Index 起始:", self._index_start)
        derive_layout.addLayout(form2)

        form3 = QFormLayout()
        self._index_end = QSpinBox()
        self._index_end.setRange(0, 1000)
        self._index_end.setValue(20)
        form3.addRow("Index 结束:", self._index_end)
        derive_layout.addLayout(form3)

        form4 = QFormLayout()
        self._passphrase_edit = QLineEdit()
        self._passphrase_edit.setPlaceholderText("（可选）")
        self._passphrase_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form4.addRow("Passphrase:", self._passphrase_edit)
        derive_layout.addLayout(form4)

        target_layout.addLayout(derive_layout)
        main_layout.addWidget(self._target_group)

        # Section D: Control & Results
        self._results_table = ResultsTable()
        main_layout.addWidget(self._results_table)

    def _connect_signals(self):
        self._mnemonic_grid.words_changed.connect(self._on_words_changed)
        self._results_table.btn_start.clicked.connect(self._on_start)
        self._results_table.btn_stop.clicked.connect(self._on_stop)

    def _on_words_changed(self):
        """Update candidates panel when mnemonic words change."""
        unknown = self._mnemonic_grid.get_unknown_indices()
        self._candidates_panel.update_unknown_slots(unknown)

    def _on_start(self):
        """Validate inputs and start the recovery worker."""
        # 1. Validate mnemonic words
        words = self._mnemonic_grid.get_words()
        unknown_slots = detect_unknown_slots(words)

        # Validate filled words
        for i, w in enumerate(words):
            if w is not None and not is_valid_bip39_word(w):
                QMessageBox.warning(
                    self, "输入错误",
                    f"位置 #{i + 1} 的词 \"{w}\" 不在 BIP39 词库中。"
                )
                return

        # 2. Validate candidates
        if unknown_slots:
            global_cands = self._candidates_panel.get_global_candidates()
            per_slot_cands = self._candidates_panel.get_per_slot_candidates()

            if global_cands is None and per_slot_cands is None:
                QMessageBox.warning(
                    self, "候选词缺失",
                    "请先填写候选词集合！\n"
                    "存在未知词位但未提供任何候选词。"
                )
                return

            # Validate candidate words against BIP39
            if global_cands:
                valid, invalid = validate_candidates(global_cands)
                if invalid:
                    QMessageBox.warning(
                        self, "候选词错误",
                        f"以下候选词不在 BIP39 词库中:\n{', '.join(invalid)}"
                    )
                    return
                global_cands = valid

            if per_slot_cands:
                for idx, cands in per_slot_cands.items():
                    valid, invalid = validate_candidates(cands)
                    if invalid:
                        QMessageBox.warning(
                            self, "候选词错误",
                            f"位置 #{idx + 1} 的以下候选词不在 BIP39 词库中:\n"
                            f"{', '.join(invalid)}"
                        )
                        return
                    per_slot_cands[idx] = valid

            # Build slot config
            try:
                slot_config = build_slot_config(
                    unknown_slots, global_cands, per_slot_cands
                )
            except ValueError as e:
                QMessageBox.warning(self, "配置错误", str(e))
                return

            # Check combination limit
            total = slot_config.total_combinations
            limit = self._candidates_panel.get_combo_limit()
            if total > limit:
                QMessageBox.warning(
                    self, "组合数超限",
                    f"总组合数 {total:,} 超过上限 {limit:,}。\n"
                    "请缩小候选词范围或调整上限。"
                )
                return
        else:
            # No unknown slots: just validate existing mnemonic
            from core.constraints import SlotConfig
            slot_config = SlotConfig()

        # 3. Validate known addresses
        addr_text = self._addr_edit.toPlainText().strip()
        if not addr_text:
            QMessageBox.warning(
                self, "地址缺失",
                "请输入至少一个已知 TRON 地址作为验证目标。"
            )
            return

        known_addresses = set()
        for line in addr_text.split("\n"):
            addr = line.strip()
            if addr:
                if not addr.startswith("T"):
                    QMessageBox.warning(
                        self, "地址格式错误",
                        f"TRON 地址应以 T 开头: {addr}"
                    )
                    return
                known_addresses.add(addr)

        # 4. Validate derivation path
        path = self._path_edit.text().strip()
        try:
            parse_derivation_path(path)
        except ValueError as e:
            QMessageBox.warning(self, "路径错误", str(e))
            return

        idx_start = self._index_start.value()
        idx_end = self._index_end.value()
        if idx_start > idx_end:
            QMessageBox.warning(
                self, "范围错误",
                "Index 起始值不能大于结束值。"
            )
            return

        passphrase = self._passphrase_edit.text()

        # 5. Start worker
        self._worker = RecoveryWorker(
            known_words=words,
            slot_config=slot_config,
            known_addresses=known_addresses,
            passphrase=passphrase,
            index_start=idx_start,
            index_end=idx_end,
            prefix=self._prefix_edit.text().strip(),
            suffix=self._suffix_edit.text().strip(),
            use_prefix=self._use_prefix_cb.isChecked(),
            use_suffix=self._use_suffix_cb.isChecked(),
            stop_on_hit=self._results_table.stop_on_hit,
        )

        self._worker_thread = QThread()
        self._worker.moveToThread(self._worker_thread)

        # Connect signals
        self._worker_thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._results_table.update_progress)
        self._worker.hit.connect(self._on_hit)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)

        self._results_table.set_running(True)
        self._worker_thread.start()

    def _on_stop(self):
        """Stop the worker."""
        if self._worker:
            self._worker.stop()

    def _on_hit(self, record: HitRecord):
        """Handle a hit from the worker."""
        self._results_table.add_hit(record)

    def _on_finished(self, tested: int, hits: int):
        """Handle worker completion."""
        self._results_table.set_running(False)
        self._cleanup_thread()
        msg = f"枚举完成！已测试 {tested:,} 个组合，命中 {hits} 个。"
        if hits == 0:
            msg += "\n未找到匹配的地址。请检查候选词和目标地址。"
        QMessageBox.information(self, "完成", msg)

    def _on_error(self, error_msg: str):
        """Handle worker error."""
        self._results_table.set_running(False)
        self._cleanup_thread()
        QMessageBox.critical(self, "错误", f"枚举过程中出错:\n{error_msg}")

    def _cleanup_thread(self):
        """Clean up worker thread."""
        if self._worker_thread and self._worker_thread.isRunning():
            self._worker_thread.quit()
            self._worker_thread.wait(5000)
        self._worker_thread = None
        self._worker = None

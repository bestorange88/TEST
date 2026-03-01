"""Results table widget for displaying hit records."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QApplication,
    QLabel,
    QProgressBar,
    QCheckBox,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt

from core.worker import HitRecord


class ResultsTable(QGroupBox):
    """Widget displaying enumeration progress and hit results.

    Shows:
    - Progress bar + statistics
    - Results table with hit records
    - Controls: start, stop, clear, export
    """

    def __init__(self, parent=None):
        super().__init__("D) 控制与结果", parent)
        self._hit_records: list[HitRecord] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Progress section
        progress_layout = QVBoxLayout()
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        progress_layout.addWidget(self._progress_bar)

        self._stats_label = QLabel("已测试: 0 / 0 | 速度: 0 combos/s")
        progress_layout.addWidget(self._stats_label)
        layout.addLayout(progress_layout)

        # Stop on hit checkbox
        self._stop_on_hit_cb = QCheckBox("命中后自动停止（默认开启）")
        self._stop_on_hit_cb.setChecked(True)
        layout.addWidget(self._stop_on_hit_cb)

        # Buttons
        btn_layout = QHBoxLayout()
        self._btn_start = QPushButton("▶ 开始")
        self._btn_start.setStyleSheet("font-weight: bold; font-size: 14px; padding: 6px 20px;")
        self._btn_stop = QPushButton("■ 停止")
        self._btn_stop.setEnabled(False)
        self._btn_clear = QPushButton("清空结果")
        self._btn_export = QPushButton("导出命中结果")
        self._btn_export.setEnabled(False)

        btn_layout.addWidget(self._btn_start)
        btn_layout.addWidget(self._btn_stop)
        btn_layout.addWidget(self._btn_clear)
        btn_layout.addWidget(self._btn_export)
        layout.addLayout(btn_layout)

        # Results table
        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels([
            "命中时间", "Index", "地址", "助记词", "操作"
        ])
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self._table)

        # Connect clear
        self._btn_clear.clicked.connect(self.clear_results)
        self._btn_export.clicked.connect(self._export_results)

    @property
    def btn_start(self) -> QPushButton:
        return self._btn_start

    @property
    def btn_stop(self) -> QPushButton:
        return self._btn_stop

    @property
    def stop_on_hit(self) -> bool:
        return self._stop_on_hit_cb.isChecked()

    def set_running(self, running: bool):
        """Update button states for running/stopped."""
        self._btn_start.setEnabled(not running)
        self._btn_stop.setEnabled(running)

    def update_progress(self, tested: int, total: int, speed: float):
        """Update progress bar and stats label."""
        if total > 0:
            pct = min(int(tested / total * 100), 100)
            self._progress_bar.setValue(pct)
        self._stats_label.setText(
            f"已测试: {tested:,} / {total:,} | 速度: {speed:,.1f} combos/s"
        )

    def add_hit(self, record: HitRecord):
        """Add a hit record to the table."""
        self._hit_records.append(record)
        row = self._table.rowCount()
        self._table.insertRow(row)

        self._table.setItem(row, 0, QTableWidgetItem(record.timestamp))
        self._table.setItem(row, 1, QTableWidgetItem(str(record.index)))
        self._table.setItem(row, 2, QTableWidgetItem(record.address))

        # Mnemonic cell: hidden by default
        mnemonic_item = QTableWidgetItem("●●●●●●●●")
        mnemonic_item.setData(Qt.ItemDataRole.UserRole, record.mnemonic)
        mnemonic_item.setData(Qt.ItemDataRole.UserRole + 1, False)  # hidden state
        self._table.setItem(row, 3, mnemonic_item)

        # Action buttons
        action_widget = QHBoxLayout()
        btn_toggle = QPushButton("显示")
        btn_copy_mnemonic = QPushButton("复制助记词")
        btn_copy_addr = QPushButton("复制地址")

        btn_toggle.clicked.connect(lambda checked, r=row: self._toggle_mnemonic(r))
        btn_copy_mnemonic.clicked.connect(
            lambda checked, r=row: self._copy_mnemonic(r)
        )
        btn_copy_addr.clicked.connect(
            lambda checked, addr=record.address: QApplication.clipboard().setText(addr)
        )

        from PySide6.QtWidgets import QWidget
        container = QWidget()
        h = QHBoxLayout(container)
        h.setContentsMargins(2, 2, 2, 2)
        h.addWidget(btn_toggle)
        h.addWidget(btn_copy_mnemonic)
        h.addWidget(btn_copy_addr)
        self._table.setCellWidget(row, 4, container)

        self._btn_export.setEnabled(True)

        # Highlight row
        for col in range(3):
            item = self._table.item(row, col)
            if item:
                item.setBackground(Qt.GlobalColor.green)

    def _toggle_mnemonic(self, row: int):
        """Toggle mnemonic visibility for a row."""
        item = self._table.item(row, 3)
        if item is None:
            return
        hidden = item.data(Qt.ItemDataRole.UserRole + 1)
        mnemonic = item.data(Qt.ItemDataRole.UserRole)
        if hidden:
            item.setText(mnemonic)
            item.setData(Qt.ItemDataRole.UserRole + 1, False)
        else:
            item.setText("●●●●●●●●")
            item.setData(Qt.ItemDataRole.UserRole + 1, True)

    def _copy_mnemonic(self, row: int):
        """Copy mnemonic to clipboard."""
        item = self._table.item(row, 3)
        if item:
            mnemonic = item.data(Qt.ItemDataRole.UserRole)
            QApplication.clipboard().setText(mnemonic)

    def clear_results(self):
        """Clear all results."""
        self._table.setRowCount(0)
        self._hit_records.clear()
        self._progress_bar.setValue(0)
        self._stats_label.setText("已测试: 0 / 0 | 速度: 0 combos/s")
        self._btn_export.setEnabled(False)

    def _export_results(self):
        """Export hit results to a text file (addresses only, no seeds)."""
        if not self._hit_records:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "导出命中结果", "hits.txt", "Text Files (*.txt)"
        )
        if not path:
            return

        confirm = QMessageBox.warning(
            self,
            "安全提示",
            "导出文件将包含命中的地址和索引信息。\n"
            "出于安全考虑，助记词不会写入文件。\n"
            "请在 GUI 中查看并手动复制助记词。\n\n"
            "确认导出？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("# TRON Recovery Hits\n")
                f.write("# 助记词出于安全考虑未导出，请在 GUI 中查看。\n\n")
                for rec in self._hit_records:
                    f.write(f"时间: {rec.timestamp}\n")
                    f.write(f"Index: {rec.index}\n")
                    f.write(f"地址: {rec.address}\n")
                    f.write(f"匹配类型: {rec.match_type}\n")
                    f.write("---\n")
            QMessageBox.information(self, "导出成功", f"结果已导出到:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", str(e))

import os
import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QFileDialog,
    QMessageBox, QSplitter, QTabWidget, QScrollArea, QGroupBox,
    QStatusBar, QMenuBar, QToolBar, QAction, QAbstractItemView,
    QCheckBox, QProgressDialog,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QFont

from core.pdf_loader import load_pdf, unload_pdf
from core.pii_detector import detect, LABELS
from core.redactor import find_pii_in_pages, apply_redaction, post_process
from core.pdf_generator import save_public_version
from core.report_generator import generate_oficio
from core.activity_log import log as log_activity
from .styles import STYLESHEET

import fitz
from io import BytesIO


def _pixmap_from_page(page, zoom=1.0):
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
    return QPixmap.fromImage(img)


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self._user = user
        self.setWindowTitle(
            f"SIT v1.0 — {user['nombre']} ({user['departamento']})"
        )
        self.resize(1200, 800)
        self.setStyleSheet(STYLESHEET)

        self._doc = None
        self._pages = None
        self._current_path = None
        self._page_matches = {}
        self._redacted_doc = None
        self._redacted_items = []
        self._current_orig_page = 1
        self._current_prev_page = 1

        self._build_menu()
        self._build_toolbar()
        self._build_central()
        self._build_statusbar()
        self._update_ui_state()

        log_activity(self._user, "inicio_sesion", "Inicio de sesión en el sistema")

    def _log(self, action, detail=""):
        log_activity(self._user, action, detail)

    # ── UI Construction ──────────────────────────────────────────

    def _build_menu(self):
        menubar = QMenuBar(self)

        file_menu = menubar.addMenu("&Archivo")
        self._act_open = QAction("&Abrir PDF...", self)
        self._act_open.setShortcut("Ctrl+O")
        self._act_open.triggered.connect(self._on_open)
        file_menu.addAction(self._act_open)

        self._act_save = QAction("&Guardar Versión Pública...", self)
        self._act_save.setShortcut("Ctrl+G")
        self._act_save.triggered.connect(self._on_save)
        file_menu.addAction(self._act_save)

        self._act_report = QAction("Guardar &Oficio de Protección...", self)
        self._act_report.setShortcut("Ctrl+R")
        self._act_report.triggered.connect(self._on_generate_report)
        file_menu.addAction(self._act_report)

        file_menu.addSeparator()
        act_exit = QAction("&Salir", self)
        act_exit.setShortcut("Ctrl+Q")
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        tool_menu = menubar.addMenu("&Herramientas")
        self._act_detect = QAction("&Detectar PII", self)
        self._act_detect.setShortcut("Ctrl+D")
        self._act_detect.triggered.connect(self._on_detect)
        tool_menu.addAction(self._act_detect)

        help_menu = menubar.addMenu("&Ayuda")
        act_about = QAction("&Acerca de", self)
        act_about.triggered.connect(self._on_about)
        help_menu.addAction(act_about)

        self.setMenuBar(menubar)

    def _build_toolbar(self):
        toolbar = QToolBar("Herramientas", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        btn_open = QAction("Abrir PDF", self)
        btn_open.triggered.connect(self._on_open)
        toolbar.addAction(btn_open)

        self._btn_save = QAction("Guardar VP", self)
        self._btn_save.triggered.connect(self._on_save)
        toolbar.addAction(self._btn_save)

        self._btn_report = QAction("Oficio", self)
        self._btn_report.triggered.connect(self._on_generate_report)
        toolbar.addAction(self._btn_report)

        toolbar.addSeparator()

        self._btn_detect = QAction("Detectar PII", self)
        self._btn_detect.triggered.connect(self._on_detect)
        toolbar.addAction(self._btn_detect)

    def _build_central(self):
        splitter = QSplitter(Qt.Horizontal, self)

        # Left: Document viewer
        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)

        # Original tab — page viewer
        orig_box = QWidget()
        orig_layout = QVBoxLayout(orig_box)
        orig_layout.setContentsMargins(0, 0, 0, 0)
        orig_nav = QHBoxLayout()
        self._orig_prev_btn = QPushButton("< Anterior")
        self._orig_prev_btn.clicked.connect(self._on_orig_prev)
        self._orig_next_btn = QPushButton("Siguiente >")
        self._orig_next_btn.clicked.connect(self._on_orig_next)
        self._orig_page_label = QLabel("Página 0 / 0")
        self._orig_page_label.setAlignment(Qt.AlignCenter)
        orig_nav.addWidget(self._orig_prev_btn)
        orig_nav.addWidget(self._orig_page_label)
        orig_nav.addWidget(self._orig_next_btn)
        orig_layout.addLayout(orig_nav)

        self._orig_scroll = QScrollArea()
        self._orig_scroll.setWidgetResizable(True)
        self._orig_container = QWidget()
        self._orig_layout = QVBoxLayout(self._orig_container)
        self._orig_layout.setAlignment(Qt.AlignTop)
        self._orig_scroll.setWidget(self._orig_container)
        orig_layout.addWidget(self._orig_scroll)
        self._tabs.addTab(orig_box, "Documento Original")

        # Preview tab — page viewer
        prev_box = QWidget()
        prev_layout = QVBoxLayout(prev_box)
        prev_layout.setContentsMargins(0, 0, 0, 0)
        prev_nav = QHBoxLayout()
        self._prev_prev_btn = QPushButton("< Anterior")
        self._prev_prev_btn.clicked.connect(self._on_prev_prev)
        self._prev_next_btn = QPushButton("Siguiente >")
        self._prev_next_btn.clicked.connect(self._on_prev_next)
        self._prev_page_label = QLabel("Página 0 / 0")
        self._prev_page_label.setAlignment(Qt.AlignCenter)
        prev_nav.addWidget(self._prev_prev_btn)
        prev_nav.addWidget(self._prev_page_label)
        prev_nav.addWidget(self._prev_next_btn)
        prev_layout.addLayout(prev_nav)

        self._prev_scroll = QScrollArea()
        self._prev_scroll.setWidgetResizable(True)
        self._prev_container = QWidget()
        self._prev_layout = QVBoxLayout(self._prev_container)
        self._prev_layout.setAlignment(Qt.AlignTop)
        self._prev_scroll.setWidget(self._prev_container)
        prev_layout.addWidget(self._prev_scroll)
        self._tabs.addTab(prev_box, "Vista Previa")

        self._tabs.currentChanged.connect(self._on_tab_changed)

        splitter.addWidget(self._tabs)

        # Right: PII panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(4, 4, 4, 4)

        group = QGroupBox("Datos Personales Detectados")
        group_layout = QVBoxLayout(group)

        self._pii_list = QListWidget()
        self._pii_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        group_layout.addWidget(self._pii_list)

        btn_row = QHBoxLayout()
        self._btn_select_all = QPushButton("Seleccionar Todo")
        self._btn_select_all.clicked.connect(self._on_select_all)
        btn_row.addWidget(self._btn_select_all)

        self._btn_clear_sel = QPushButton("Deseleccionar Todo")
        self._btn_clear_sel.clicked.connect(self._on_clear_selection)
        btn_row.addWidget(self._btn_clear_sel)
        group_layout.addLayout(btn_row)

        self._btn_redact = QPushButton("Aplicar Redacción")
        self._btn_redact.clicked.connect(self._on_redact)
        group_layout.addWidget(self._btn_redact)

        right_layout.addWidget(group)

        # Summary
        sum_group = QGroupBox("Resumen")
        sum_layout = QVBoxLayout(sum_group)
        self._lbl_total = QLabel("Total detectados: 0")
        sum_layout.addWidget(self._lbl_total)
        self._lbl_file = QLabel("Archivo: (ninguno)")
        sum_layout.addWidget(self._lbl_file)
        right_layout.addWidget(sum_group)

        right_layout.addStretch()

        splitter.addWidget(right_panel)
        splitter.setSizes([800, 320])

        self.setCentralWidget(splitter)

    def _build_statusbar(self):
        self._status = QStatusBar(self)
        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        self._status.showMessage(
            f"Usuario: {self._user['nombre']} | "
            f"Depto: {self._user['departamento']} | "
            f"Sesión: {now}"
        )
        self.setStatusBar(self._status)

    # ── Actions ──────────────────────────────────────────────────

    def _on_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir PDF", "", "PDF (*.pdf)"
        )
        if not path:
            return

        self._close_doc()
        self._current_path = path
        self._status.showMessage(f"Cargando: {os.path.basename(path)}...")

        try:
            self._pages, self._doc = load_pdf(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el PDF:\n{e}")
            self._status.showMessage("Error al abrir")
            return

        self._render_original()
        self._render_preview_clear()
        self._lbl_file.setText(f"Archivo: {os.path.basename(path)}")
        self._status.showMessage(
            f"Cargado: {os.path.basename(path)} — {len(self._pages)} página(s)"
        )
        self._update_ui_state()
        self._log("abrir_pdf", os.path.basename(path))

        QTimer.singleShot(100, self._on_detect)

    def _on_detect(self):
        if not self._pages:
            return

        self._status.showMessage("Detectando datos personales...")
        self._pii_list.clear()

        self._page_matches = find_pii_in_pages(self._pages)
        total = 0
        for page_num in sorted(self._page_matches):
            for m in self._page_matches[page_num]:
                item = QListWidgetItem(
                    f"[Pág.{page_num}] {m['label']}: {m['text']}"
                )
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)
                item.setData(Qt.UserRole, (page_num, m))
                self._pii_list.addItem(item)
                total += 1

        self._lbl_total.setText(f"Total detectados: {total}")
        self._status.showMessage(
            f"Detección completada — {total} dato(s) sensible(s) encontrado(s)"
        )
        self._update_ui_state()
        self._log("detectar_pii", f"{total} dato(s) encontrado(s)")

    def _on_redact(self):
        if not self._doc:
            return

        self._redacted_doc = None
        self._redacted_items = []
        items = []
        for i in range(self._pii_list.count()):
            item = self._pii_list.item(i)
            if item.checkState() == Qt.Checked:
                items.append(item)

        if not items:
            QMessageBox.information(
                self, "Sin selección",
                "No hay elementos seleccionados para redactar."
            )
            return

        buffer = BytesIO()
        self._doc.save(buffer)
        buffer.seek(0)
        self._redacted_doc = fitz.open(stream=buffer, filetype="pdf")

        progress = QProgressDialog(
            "Aplicando redacción...", None, 0, len(items), self
        )
        progress.setWindowTitle("Redactando")
        progress.setWindowModality(Qt.WindowModal)

        per_page = {}
        for idx, item in enumerate(items):
            page_num, m = item.data(Qt.UserRole)
            page_obj = self._redacted_doc[page_num - 1]
            info = apply_redaction(page_obj, [m])
            per_page.setdefault(page_num, []).extend(info)
            self._redacted_items.append(
                (page_num, m["label"], m["text"], m["type"])
            )
            progress.setValue(idx + 1)

        progress.close()

        post_process(self._redacted_doc, per_page)

        self._render_preview()
        self._tabs.setCurrentIndex(1)
        self._act_report.setEnabled(True)
        self._btn_report.setEnabled(True)
        self._status.showMessage(
            f"Redacción aplicada — {len(items)} dato(s) procesado(s)"
        )
        tipos = set(m["type"] for _, m in [item.data(Qt.UserRole) for item in items])
        self._log("redactar", f"{len(items)} elemento(s), tipos: {', '.join(tipos)}")

    def _on_save(self):
        target = self._redacted_doc if self._redacted_doc else self._doc
        if target is None:
            QMessageBox.warning(
                self, "Sin documento",
                "No hay ningún documento abierto."
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Versión Pública", "", "PDF (*.pdf)"
        )
        if not path:
            return

        try:
            save_public_version(target, path)
            self._status.showMessage(f"Guardado: {path}")
            self._log("guardar_vp", os.path.basename(path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")

    def _on_generate_report(self):
        if not self._redacted_items:
            QMessageBox.warning(
                self, "Sin datos",
                "No hay elementos redactados. Aplica la redacción primero."
            )
            return
        if not self._current_path:
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Oficio de Protección", "", "Documento Word (*.docx)"
        )
        if not path:
            return

        try:
            generate_oficio(
                self._redacted_items, self._current_path, path, self._user
            )
            self._status.showMessage(f"Oficio guardado: {path}")
            self._log("generar_oficio", os.path.basename(path))
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"No se pudo generar el oficio:\n{e}"
            )

    def _on_select_all(self):
        for i in range(self._pii_list.count()):
            self._pii_list.item(i).setCheckState(Qt.Checked)

    def _on_clear_selection(self):
        for i in range(self._pii_list.count()):
            self._pii_list.item(i).setCheckState(Qt.Unchecked)

    def _on_about(self):
        QMessageBox.about(
            self,
            "Acerca de",
            "Sistema Institucional de Transparencia v1.0\n\n"
            "Auditoría y testado automático de contratos\n"
            "conforme a la LGTAIP (México)\n\n"
            "Tecnologías: Python · PyQt5 · PyMuPDF\n"
            "Detección de datos personales vía regex"
        )

    # ── Rendering ────────────────────────────────────────────────

    def _render_page(self, layout, doc_pages, page_num, page_label,
                     prev_btn, next_btn):
        self._clear_layout(layout)
        total = len(doc_pages)
        page_label.setText(f"Página {page_num} / {total}")
        prev_btn.setEnabled(page_num > 1)
        next_btn.setEnabled(page_num < total)
        if not doc_pages:
            return
        p = doc_pages[page_num - 1]
        if isinstance(p, dict):
            page_obj = p["page"]
        else:
            page_obj = p
        pixmap = _pixmap_from_page(page_obj, zoom=1.0)
        lbl = QLabel()
        lbl.setPixmap(pixmap)
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

    def _render_original(self):
        self._current_orig_page = 1
        if not self._pages:
            return
        self._render_page(self._orig_layout, self._pages, 1,
                          self._orig_page_label,
                          self._orig_prev_btn, self._orig_next_btn)

    def _render_preview_clear(self):
        self._clear_layout(self._prev_layout)
        lbl = QLabel("Aplica la redacción para ver la vista previa.")
        lbl.setAlignment(Qt.AlignCenter)
        self._prev_layout.addWidget(lbl)

    def _render_preview(self):
        self._current_prev_page = 1
        if not self._redacted_doc:
            return
        prev_pages = [self._redacted_doc[i] for i in range(len(self._redacted_doc))]
        self._render_page(self._prev_layout, prev_pages, 1,
                          self._prev_page_label,
                          self._prev_prev_btn, self._prev_next_btn)

    def _on_orig_prev(self):
        if self._current_orig_page > 1:
            self._current_orig_page -= 1
            self._render_page(self._orig_layout, self._pages,
                              self._current_orig_page,
                              self._orig_page_label,
                              self._orig_prev_btn, self._orig_next_btn)

    def _on_orig_next(self):
        if self._pages and self._current_orig_page < len(self._pages):
            self._current_orig_page += 1
            self._render_page(self._orig_layout, self._pages,
                              self._current_orig_page,
                              self._orig_page_label,
                              self._orig_prev_btn, self._orig_next_btn)

    def _on_prev_prev(self):
        if self._current_prev_page > 1:
            self._current_prev_page -= 1
            prev_pages = [self._redacted_doc[i]
                          for i in range(len(self._redacted_doc))]
            self._render_page(self._prev_layout, prev_pages,
                              self._current_prev_page,
                              self._prev_page_label,
                              self._prev_prev_btn, self._prev_next_btn)

    def _on_prev_next(self):
        if not self._redacted_doc:
            return
        if self._current_prev_page < len(self._redacted_doc):
            self._current_prev_page += 1
            prev_pages = [self._redacted_doc[i]
                          for i in range(len(self._redacted_doc))]
            self._render_page(self._prev_layout, prev_pages,
                              self._current_prev_page,
                              self._prev_page_label,
                              self._prev_prev_btn, self._prev_next_btn)

    def _on_tab_changed(self, index):
        if index == 0:
            self._render_page(self._orig_layout, self._pages or [],
                              self._current_orig_page,
                              self._orig_page_label,
                              self._orig_prev_btn, self._orig_next_btn)
        elif index == 1:
            if self._redacted_doc:
                prev_pages = [self._redacted_doc[i]
                              for i in range(len(self._redacted_doc))]
                self._render_page(self._prev_layout, prev_pages,
                                  self._current_prev_page,
                                  self._prev_page_label,
                                  self._prev_prev_btn, self._prev_next_btn)

    # ── Helpers ──────────────────────────────────────────────────

    def _close_doc(self):
        if self._doc:
            unload_pdf(self._doc)
        self._doc = None
        self._pages = None
        self._redacted_doc = None
        self._redacted_items = []
        self._page_matches = {}
        self._pii_list.clear()
        self._clear_layout(self._orig_layout)
        self._clear_layout(self._prev_layout)
        self._lbl_total.setText("Total detectados: 0")
        self._lbl_file.setText("Archivo: (ninguno)")

    def _update_ui_state(self):
        has_doc = self._doc is not None
        has_pii = self._pii_list.count() > 0
        has_report = len(self._redacted_items) > 0
        self._act_save.setEnabled(has_doc)
        self._btn_save.setEnabled(has_doc)
        self._act_detect.setEnabled(has_doc)
        self._btn_detect.setEnabled(has_doc)
        self._act_report.setEnabled(has_report)
        self._btn_report.setEnabled(has_report)
        self._btn_redact.setEnabled(has_pii)
        self._btn_select_all.setEnabled(has_pii)
        self._btn_clear_sel.setEnabled(has_pii)

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def closeEvent(self, event):
        self._log("cierre_sesion", "Cierre de sesión")
        self._close_doc()
        super().closeEvent(event)

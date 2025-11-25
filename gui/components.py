"""Wiederverwendbare GUI-Komponenten."""

from PySide6.QtWidgets import (
    QWidget, QLabel, QTextEdit, QPushButton, QProgressBar,
    QVBoxLayout, QHBoxLayout, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QPainter, QColor, QLinearGradient
from pathlib import Path


class AnimatedProgressBar(QWidget):
    """Animierter Progress-Bar mit coolem Design."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(30)
        self.setMaximumHeight(30)
        self.progress = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_offset = 0
        self.is_animating = False
        
    def start_animation(self):
        """Startet die Animation."""
        self.is_animating = True
        self.animation_timer.start(50)  # Update alle 50ms
        
    def stop_animation(self):
        """Stoppt die Animation."""
        self.is_animating = False
        self.animation_timer.stop()
        self.progress = 100
        self.update()
        
    def set_progress(self, value: int):
        """Setzt den Progress-Wert (0-100)."""
        self.progress = max(0, min(100, value))
        self.update()
        
    def update_animation(self):
        """Aktualisiert die Animation."""
        self.animation_offset = (self.animation_offset + 2) % 100
        self.update()
        
    def paintEvent(self, event):
        """Zeichnet den animierten Progress-Bar."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Hintergrund
        bg_color = QColor(30, 30, 30)
        painter.fillRect(self.rect(), bg_color)
        
        # Progress-Bar mit Gradient
        if self.progress > 0:
            bar_width = int(self.rect().width() * self.progress / 100)
            bar_rect = self.rect()
            bar_rect.setWidth(bar_width)
            
            # Gradient von Lila zu Blau
            gradient = QLinearGradient(0, 0, bar_width, 0)
            gradient.setColorAt(0, QColor(124, 58, 237))  # Lila
            gradient.setColorAt(0.5, QColor(139, 92, 246))  # Hell-Lila
            gradient.setColorAt(1, QColor(59, 130, 246))  # Blau
            
            painter.fillRect(bar_rect, gradient)
            
            # Animierter Shine-Effekt
            if self.is_animating:
                shine_width = 50
                shine_x = int(self.animation_offset * self.rect().width() / 100)
                shine_gradient = QLinearGradient(shine_x, 0, shine_x + shine_width, 0)
                shine_gradient.setColorAt(0, QColor(255, 255, 255, 0))
                shine_gradient.setColorAt(0.5, QColor(255, 255, 255, 100))
                shine_gradient.setColorAt(1, QColor(255, 255, 255, 0))
                painter.fillRect(shine_x, 0, shine_width, self.rect().height(), shine_gradient)
        
        # Text
        painter.setPen(QColor(255, 255, 255))
        font = painter.font()
        font.setBold(True)
        font.setPointSize(9)
        painter.setFont(font)
        
        if self.is_animating:
            text = f"🔄 Analysiere Bild... {self.progress}%"
        else:
            text = f"✅ Fertig! {self.progress}%"
            
        painter.drawText(self.rect(), Qt.AlignCenter, text)


class DragDropArea(QFrame):
    """Drag & Drop Bereich für Bilder."""
    
    files_dropped = Signal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(2)
        self.setup_ui()
    
    def setup_ui(self):
        """Erstellt die UI des Drag & Drop Bereichs."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        self.label = QLabel("🖼️ Bilder hier hineinziehen\noder klicken zum Auswählen")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 500;
                color: #d0d0d0;
                padding: 50px;
                background: transparent;
            }
        """)
        
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # Initiales Styling
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #505050;
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #252525, stop:1 #1e1e1e);
            }
        """)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Wird aufgerufen wenn etwas in den Bereich gezogen wird."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame {
                    border: 2px dashed #7c3aed;
                    border-radius: 12px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3a2a4a, stop:1 #2a1e3a);
                }
            """)
            self.label.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: 500;
                    color: #a78bfa;
                    padding: 50px;
                    background: transparent;
                }
            """)
    
    def dragLeaveEvent(self, event):
        """Wird aufgerufen wenn der Drag-Vorgang den Bereich verlässt."""
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #505050;
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #252525, stop:1 #1e1e1e);
            }
        """)
        self.label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 500;
                color: #d0d0d0;
                padding: 50px;
                background: transparent;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        """Wird aufgerufen wenn etwas fallen gelassen wird."""
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #505050;
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #252525, stop:1 #1e1e1e);
            }
        """)
        self.label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 500;
                color: #d0d0d0;
                padding: 50px;
                background: transparent;
            }
        """)
        
        files = []
        for url in event.mimeData().urls():
            # Filtere "data:" URLs und andere nicht-lokale Schemas heraus
            # Das verhindert die Qt-Warnung "Unhandled scheme: data"
            if url.scheme() in ('file', ''):  # Nur lokale Dateien akzeptieren
                try:
                    file_path = url.toLocalFile()
                    if file_path and file_path.strip():
                        files.append(file_path)
                except Exception:
                    # Ignoriere URLs die nicht zu lokalen Dateien konvertiert werden können
                    continue
        
        if files:
            self.files_dropped.emit(files)
    
    def mousePressEvent(self, event):
        """Öffnet Dateiauswahl-Dialog beim Klicken."""
        from PySide6.QtWidgets import QFileDialog
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Bilder auswählen",
            "",
            "Bilder (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tiff)"
        )
        if files:
            self.files_dropped.emit(files)


class ImagePreview(QLabel):
    """Vorschau für ein einzelnes Bild."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(200, 200)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1f1f1f, stop:1 #151515);
                color: #888888;
                font-size: 14px;
            }
        """)
        self.setText("Kein Bild")
    
    def set_image(self, image_path: str):
        """Setzt das anzuzeigende Bild."""
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Skaliere Bild falls zu groß
                scaled_pixmap = pixmap.scaled(
                    300, 300,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.setPixmap(scaled_pixmap)
            else:
                self.setText("Bild konnte nicht geladen werden")
        except Exception as e:
            self.setText(f"Fehler: {str(e)}")


class TagDisplay(QTextEdit):
    """Anzeige für generierte Tags."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("Tags werden hier angezeigt...")
        self.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1f1f1f, stop:1 #151515);
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                padding: 12px;
                selection-background-color: #7c3aed;
                selection-color: #ffffff;
            }
        """)
    
    def display_tags(self, tags: list, include_confidence: bool = True, max_tags: int = 25, rating_tags: dict = None):
        """
        Zeigt Tags an.
        
        Args:
            tags: Liste von (tag, confidence) Tupeln
            include_confidence: Ob Konfidenz angezeigt werden soll
            max_tags: Maximale Anzahl von Tags (Standard: 25)
            rating_tags: Dictionary mit Rating-Tags (general, sensitive, questionable, explicit)
        """
        if not tags and not rating_tags:
            self.setText("Keine Tags gefunden.")
            return
        
        # Begrenze auf max_tags (Tags sind bereits nach Konfidenz sortiert)
        display_tags = tags[:max_tags] if max_tags else tags
        
        # Verwende HTML für schöne Formatierung
        text = "<div style='padding: 5px;'>"
        
        # Rating-Tags anzeigen (falls vorhanden)
        if rating_tags:
            text += "<h3 style='color: #a78bfa; margin: 8px 0; font-size: 16px; font-weight: 600;'>📊 Rating</h3>"
            text += "<div style='margin: 8px 0; padding: 8px; background: rgba(124, 58, 237, 0.1); border-radius: 6px;'>"
            
            rating_names = {
                'general': 'General',
                'sensitive': 'Sensitive',
                'questionable': 'Questionable',
                'explicit': 'Explicit'
            }
            
            for rating_key, rating_name in rating_names.items():
                if rating_key in rating_tags:
                    conf = rating_tags[rating_key]
                    # Farbcodierung für Ratings
                    if conf >= 0.7:
                        color = "#34d399"  # Grün
                    elif conf >= 0.5:
                        color = "#60a5fa"  # Blau
                    elif conf >= 0.3:
                        color = "#fbbf24"  # Gelb
                    else:
                        color = "#f87171"  # Rot
                    
                    percentage = int(conf * 100)
                    text += f"<div style='margin: 4px 0;'><span style='color: {color}; font-weight: 600;'>{rating_name}:</span> <span style='color: #888;'>{percentage}%</span></div>"
            
            text += "</div>"
            text += "<hr style='border: 1px solid #3a3a3a; margin: 15px 0;'>"
        
        text += "<h3 style='color: #a78bfa; margin: 8px 0; font-size: 16px; font-weight: 600;'>✨ Generierte Tags</h3>"
        text += "<div style='margin: 10px 0; line-height: 1.8;'>"
        
        for i, (tag, conf) in enumerate(display_tags, 1):
            # Farbcodierung basierend auf Konfidenz
            if conf >= 0.7:
                color = "#34d399"  # Grün für hohe Konfidenz
            elif conf >= 0.5:
                color = "#60a5fa"  # Blau für mittlere Konfidenz
            elif conf >= 0.35:
                color = "#fbbf24"  # Gelb für niedrige Konfidenz
            else:
                color = "#f87171"  # Rot für sehr niedrige Konfidenz
            
            if include_confidence:
                text += f"<div style='margin: 4px 0;'><span style='color: #666; font-size: 11px;'>{i:3d}.</span> <span style='color: {color}; font-weight: 500; font-size: 13px;'>{tag}</span> <span style='color: #555; font-size: 10px;'>[{conf:.4f}]</span></div>"
            else:
                text += f"<div style='margin: 4px 0;'><span style='color: #666; font-size: 11px;'>{i:3d}.</span> <span style='color: {color}; font-weight: 500; font-size: 13px;'>{tag}</span></div>"
        
        text += "</div>"
        text += "<hr style='border: 1px solid #3a3a3a; margin: 15px 0;'>"
        text += "<h3 style='color: #a78bfa; margin: 8px 0; font-size: 16px; font-weight: 600;'>📝 Als Prompt</h3>"
        tag_strings = [tag for tag, _ in display_tags]
        text += f"<div style='color: #d0d0d0; line-height: 1.8; margin-top: 8px; padding: 8px; background: rgba(124, 58, 237, 0.1); border-radius: 6px;'>{', '.join(tag_strings)}</div>"
        text += "</div>"
        
        self.setHtml(text)
    
    def get_prompt_text(self) -> str:
        """Gibt den Prompt-Text zurück (ohne Konfidenz) - maximal 25 Tags."""
        # Extrahiere Tags aus dem HTML
        html_text = self.toHtml()
        
        # Versuche den Prompt-Bereich aus dem HTML zu extrahieren
        if "Als Prompt" in html_text:
            import re
            from html import unescape
            # Suche nach dem div mit dem Prompt-Text
            match = re.search(r'Als Prompt.*?<div[^>]*>(.*?)</div>', html_text, re.DOTALL)
            if match:
                prompt_html = match.group(1)
                # Entferne HTML-Tags
                prompt_text = re.sub(r'<[^>]+>', '', prompt_html)
                prompt_text = unescape(prompt_text).strip()
                
                # Stelle sicher, dass wir maximal 25 Tags haben
                tags = [tag.strip() for tag in prompt_text.split(',') if tag.strip()]
                tags = tags[:25]  # Begrenze auf 25 Tags
                return ', '.join(tags)
        
        # Fallback: Extrahiere aus Plain Text
        text = self.toPlainText()
        if "Als Prompt" in text:
            lines = text.split("\n")
            prompt_started = False
            prompt_lines = []
            for line in lines:
                if "Als Prompt" in line:
                    prompt_started = True
                    continue
                if prompt_started and line.strip():
                    prompt_lines.append(line.strip())
            if prompt_lines:
                prompt_text = " ".join(prompt_lines)
                tags = [tag.strip() for tag in prompt_text.split(',') if tag.strip()]
                tags = tags[:25]  # Begrenze auf 25 Tags
                return ', '.join(tags)
        
        return ""


class ActionButtons(QWidget):
    """Container für Aktions-Buttons."""
    
    copy_clicked = Signal()
    export_clicked = Signal()
    clear_clicked = Signal()
    refresh_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Erstellt die Buttons."""
        layout = QHBoxLayout()
        layout.setSpacing(12)
        
        self.copy_btn = QPushButton("📋 Tags kopieren")
        self.copy_btn.clicked.connect(self.copy_clicked.emit)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7c3aed, stop:1 #6d28d9);
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                color: #ffffff;
                font-size: 12px;
                font-weight: 600;
                min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8b5cf6, stop:1 #7c3aed);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6d28d9, stop:1 #5b21b6);
            }
        """)
        
        self.export_btn = QPushButton("💾 Als Datei speichern")
        self.export_btn.clicked.connect(self.export_clicked.emit)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b82f6, stop:1 #2563eb);
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                color: #ffffff;
                font-size: 12px;
                font-weight: 600;
                min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #60a5fa, stop:1 #3b82f6);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2563eb, stop:1 #1d4ed8);
            }
        """)
        
        self.refresh_btn = QPushButton("🔄 Aktualisieren")
        self.refresh_btn.clicked.connect(self.refresh_clicked.emit)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10b981, stop:1 #059669);
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                color: #ffffff;
                font-size: 12px;
                font-weight: 600;
                min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34d399, stop:1 #10b981);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #059669, stop:1 #047857);
            }
        """)
        
        self.clear_btn = QPushButton("🗑️ Zurücksetzen")
        self.clear_btn.clicked.connect(self.clear_clicked.emit)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4b5563, stop:1 #374151);
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                color: #ffffff;
                font-size: 12px;
                font-weight: 600;
                min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6b7280, stop:1 #4b5563);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #374151, stop:1 #1f2937);
            }
        """)
        
        layout.addWidget(self.copy_btn)
        layout.addWidget(self.export_btn)
        layout.addWidget(self.refresh_btn)
        layout.addWidget(self.clear_btn)
        layout.addStretch()
        self.setLayout(layout)

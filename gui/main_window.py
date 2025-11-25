"""Hauptfenster der Shila-Vision Anwendung."""

import os
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QFileDialog, QMessageBox, QApplication, QLabel, QDoubleSpinBox,
    QCheckBox, QLineEdit
)
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer
import time
from PySide6.QtGui import QClipboard

from gui.components import DragDropArea, ImagePreview, TagDisplay, ActionButtons, AnimatedProgressBar
from tagger.wd14_tagger import WD14Tagger
from utils.file_handler import FileHandler


class TaggingWorker(QObject):
    """Worker-Thread für asynchrones Tagging."""
    
    finished = Signal(str, list, str)  # image_path, tags, tagger_name
    error = Signal(str, str)  # image_path, error_message
    progress = Signal(str, int)  # status message, progress (0-100)
    
    def __init__(self, tagger1: WD14Tagger, tagger2: WD14Tagger, image_path: str):
        super().__init__()
        self.tagger1 = tagger1
        self.tagger2 = tagger2
        self.image_path = image_path
    
    def analyze_image_preview(self, image_path: str) -> dict:
        """Analysiert das Bild intensiv für bessere Erkenntnisse (Thinking Mode)."""
        from PIL import Image
        try:
            import numpy as np
        except ImportError:
            # Fallback falls numpy nicht verfügbar
            return {'size': (0, 0), 'mode': 'RGB', 'format': None}
        
        analysis = {}
        try:
            image = Image.open(image_path)
            analysis['size'] = image.size
            analysis['mode'] = image.mode
            analysis['format'] = image.format
            analysis['aspect_ratio'] = image.size[0] / image.size[1] if image.size[1] > 0 else 1.0
            
            # Konvertiere zu RGB für Farbanalyse
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Detaillierte Farbanalyse
            img_array = np.array(image)
            analysis['dominant_colors'] = self._get_dominant_colors(img_array)
            analysis['brightness'] = float(np.mean(img_array))
            analysis['contrast'] = float(np.std(img_array))
            
            # Erweiterte Bildmerkmale
            analysis['is_dark'] = analysis['brightness'] < 100
            analysis['is_bright'] = analysis['brightness'] > 150
            analysis['has_high_contrast'] = analysis['contrast'] > 50
            analysis['is_colorful'] = analysis['contrast'] > 40
            
            # Farbanalyse - erkenne dominante Farben
            r_mean = float(np.mean(img_array[:, :, 0]))
            g_mean = float(np.mean(img_array[:, :, 1]))
            b_mean = float(np.mean(img_array[:, :, 2]))
            
            analysis['is_reddish'] = r_mean > g_mean + 20 and r_mean > b_mean + 20
            analysis['is_greenish'] = g_mean > r_mean + 20 and g_mean > b_mean + 20
            analysis['is_blueish'] = b_mean > r_mean + 20 and b_mean > g_mean + 20
            analysis['is_pinkish'] = r_mean > 150 and g_mean > 100 and b_mean > 100 and abs(r_mean - g_mean) < 30
            
            # Erkenne Bildtyp
            analysis['is_photo'] = analysis['format'] in ['JPEG', 'JPG', 'PNG'] and analysis['contrast'] > 20
            analysis['is_illustration'] = analysis['contrast'] < 30 or analysis['format'] in ['GIF', 'WEBP']
            
            # Erkenne Nahaufnahme (hoher Kontrast, fokussiertes Objekt)
            analysis['is_closeup'] = analysis['has_high_contrast'] and analysis['contrast'] > 40
            
            # Erkenne Hintergrund
            # Analysiere Ränder des Bildes für Hintergrund-Erkennung
            h, w = img_array.shape[:2]
            edge_pixels = np.concatenate([
                img_array[0, :].reshape(-1, 3),  # Oben
                img_array[-1, :].reshape(-1, 3),  # Unten
                img_array[:, 0].reshape(-1, 3),  # Links
                img_array[:, -1].reshape(-1, 3)   # Rechts
            ])
            edge_brightness = float(np.mean(edge_pixels))
            analysis['has_dark_background'] = edge_brightness < 80
            analysis['has_bright_background'] = edge_brightness > 180
            analysis['has_neutral_background'] = 100 <= edge_brightness <= 150
            
            # Erkenne mögliche Objekte basierend auf Farbverteilung
            # Wenn ein Bereich sehr unterschiedlich ist, könnte es ein Objekt sein
            color_variance = float(np.std([r_mean, g_mean, b_mean]))
            analysis['has_distinct_object'] = color_variance > 30
            
        except Exception as e:
            print(f"Fehler bei Bild-Analyse: {e}")
        
        return analysis
    
    def _get_dominant_colors(self, img_array, k=3):
        """Ermittelt dominante Farben im Bild."""
        try:
            # Vereinfachte Methode: Sample einige Pixel
            h, w = img_array.shape[:2]
            sample_size = min(1000, h * w)
            indices = np.random.choice(h * w, sample_size, replace=False)
            pixels = img_array.reshape(-1, 3)[indices]
            return pixels.mean(axis=0).astype(int).tolist()
        except:
            return [128, 128, 128]  # Fallback: Grau
    
    def evaluate_tags(self, tags: list) -> float:
        """Bewertet Tags basierend auf Qualität (höhere Konfidenz = besser)."""
        if not tags:
            return 0.0
        # Berechne durchschnittliche Konfidenz der Top 25 Tags
        top_tags = tags[:25]
        if not top_tags:
            return 0.0
        avg_confidence = sum(conf for _, conf in top_tags) / len(top_tags)
        # Bonus für mehr relevante Tags (über Threshold)
        high_confidence_count = sum(1 for _, conf in top_tags if conf >= 0.5)
        score = avg_confidence * 0.7 + (high_confidence_count / 25.0) * 0.3
        return score
    
    def run(self):
        """Thinking Mode Engine: Intensives Scannen, tiefe Analyse, dann Tag-Berechnung."""
        try:
            # Phase 1: Intensives Bild-Scannen
            self.progress.emit(f"🔍 Scanne Bild-Details...", 3)
            analysis = self.analyze_image_preview(self.image_path)
            time.sleep(0.3)
            
            # Phase 2: Detaillierte Bildanalyse
            self.progress.emit(f"🔬 Analysiere Bildstruktur...", 8)
            time.sleep(0.4)
            
            # Phase 3: Farb- und Kompositionsanalyse
            self.progress.emit(f"🎨 Analysiere Farben und Komposition...", 12)
            time.sleep(0.5)
            
            # Phase 4: "Wait minute" - Tiefe Denkzeit mit detaillierten Erkenntnissen
            self.progress.emit(f"⏳ Tiefe Bildanalyse...", 18)
            time.sleep(0.6)
            
            # Detaillierte Erkenntnisse sammeln
            insights = []
            image_type = []
            color_info = []
            composition_info = []
            
            # Bildtyp
            if analysis.get('is_photo'):
                image_type.append("Fotografie")
            if analysis.get('is_illustration'):
                image_type.append("Illustration")
            if analysis.get('is_closeup'):
                composition_info.append("Nahaufnahme")
            
            # Farben
            if analysis.get('is_pinkish'):
                color_info.append("rosa/rötlich")
            elif analysis.get('is_reddish'):
                color_info.append("rötlich")
            elif analysis.get('is_greenish'):
                color_info.append("grünlich")
            elif analysis.get('is_blueish'):
                color_info.append("bläulich")
            
            if analysis.get('is_bright'):
                color_info.append("hell")
            elif analysis.get('is_dark'):
                color_info.append("dunkel")
            
            # Komposition
            if analysis.get('has_dark_background'):
                composition_info.append("dunkler Hintergrund")
            elif analysis.get('has_bright_background'):
                composition_info.append("heller Hintergrund")
            
            if analysis.get('has_high_contrast'):
                composition_info.append("hoher Kontrast")
            
            if analysis.get('has_distinct_object'):
                composition_info.append("deutliches Objekt")
            
            # Zeige detaillierte Erkenntnisse
            all_insights = []
            if image_type:
                all_insights.append(f"Typ: {', '.join(image_type)}")
            if color_info:
                all_insights.append(f"Farben: {', '.join(color_info)}")
            if composition_info:
                all_insights.append(f"Komposition: {', '.join(composition_info)}")
            
            if all_insights:
                insight_text = " | ".join(all_insights)
                self.progress.emit(f"💭 {insight_text}...", 25)
                time.sleep(0.5)
            else:
                self.progress.emit(f"💭 Analysiere Bildmerkmale...", 25)
                time.sleep(0.4)
            
            # Phase 5: Berechne Tags mit Tagger 1 (mit Kontext)
            self.progress.emit(f"🧠 Berechne Tags mit Tagger 1 (WD14)...", 30)
            tags1 = self.tagger1.tag_image(self.image_path)
            score1 = self.evaluate_tags(tags1)
            
            # Phase 6: Berechne Tags mit Tagger 2 (mit Kontext)
            self.progress.emit(f"🧠 Berechne Tags mit Tagger 2 (SwinV2)...", 65)
            tags2 = self.tagger2.tag_image(self.image_path)
            score2 = self.evaluate_tags(tags2)
            
            # Phase 7: Vergleiche und wähle besten Tagger
            self.progress.emit(f"🎯 Vergleiche Ergebnisse...", 85)
            time.sleep(0.3)
            
            # Phase 8: Finale Auswahl
            self.progress.emit(f"✨ Wähle besten Tagger...", 90)
            time.sleep(0.2)
            
            # Wähle den besseren Tagger
            if score1 >= score2:
                best_tags = tags1
                tagger_name = "Tagger 1 (WD14)"
            else:
                best_tags = tags2
                tagger_name = "Tagger 2 (WD14-SwinV2)"
            
            self.progress.emit(f"✅ Fertig! ({tagger_name})", 100)
            self.finished.emit(self.image_path, best_tags, tagger_name)
        except Exception as e:
            self.error.emit(self.image_path, str(e))


class MainWindow(QMainWindow):
    """Hauptfenster der Anwendung."""
    
    def __init__(self):
        super().__init__()
        # Alte Variable entfernt - verwende jetzt tagger1 und tagger2
        self.current_image_path = None
        self.current_tags = []
        self.raw_tags = []  # Speichere ursprüngliche Tags (vor Verarbeitung)
        self.worker_thread = None
        self.worker = None
        self.rating_tags = {}  # Für Rating-Tags (sensitive, general, etc.)
        
        # Kaomoji-Liste (Tags die Unterstriche behalten sollen)
        # Basierend auf WD14 Tagger CSV
        self.kaomojis = {
            '0_0', '(o)_(o)', '+_+', '+_-', '._.', '<o>_<o>', '<|>_<|>', 
            '=_=', '>_<', '3_3', '6_9', '>_o', '@_@', '^_^', 'o_o', 
            'u_u', 'x_x', '|_|', '||_||'
        }
        
        # Standard-Ausschluss-Tags (werden beim Start gesetzt)
        self.default_exclude = ["monochrome", "greyscale", "dark", "simple background"]
        
        self.setup_ui()
        self.setup_tagger()
        self.apply_dark_theme()
        
        # Setze Standard-Ausschluss-Tags nach UI-Init
        if hasattr(self, 'exclude_tags_input'):
            self.exclude_tags_input.setText(", ".join(self.default_exclude))
    
    def setup_ui(self):
        """Erstellt die Benutzeroberfläche."""
        self.setWindowTitle("Shila-Vision - Bild-Tagging Tool")
        self.setMinimumSize(1000, 700)
        
        # Zentrales Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Hauptlayout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Drag & Drop Bereich
        self.drag_drop_area = DragDropArea()
        self.drag_drop_area.files_dropped.connect(self.on_files_dropped)
        main_layout.addWidget(self.drag_drop_area, stretch=1)
        
        # Splitter für Bildvorschau und Tags
        splitter = QSplitter(Qt.Horizontal)
        
        # Linke Seite: Bildvorschau
        preview_widget = QWidget()
        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        preview_label = QWidget()
        preview_label_layout = QVBoxLayout()
        preview_label_layout.setContentsMargins(8, 8, 8, 8)
        preview_label_widget = QLabel("🖼️ Bildvorschau")
        preview_label_widget.setStyleSheet("""
            QLabel {
                color: #a78bfa;
                font-size: 14px;
                font-weight: 600;
                padding: 4px;
            }
        """)
        preview_label_layout.addWidget(preview_label_widget)
        preview_label.setLayout(preview_label_layout)
        preview_layout.addWidget(preview_label)
        
        self.image_preview = ImagePreview()
        preview_layout.addWidget(self.image_preview, stretch=1)
        
        preview_widget.setLayout(preview_layout)
        splitter.addWidget(preview_widget)
        
        # Rechte Seite: Tags
        tags_widget = QWidget()
        tags_layout = QVBoxLayout()
        tags_layout.setContentsMargins(0, 0, 0, 0)
        
        tags_label = QWidget()
        tags_label_layout = QHBoxLayout()
        tags_label_layout.setContentsMargins(8, 8, 8, 8)
        tags_label_widget = QLabel("🏷️ Generierte Tags")
        tags_label_widget.setStyleSheet("""
            QLabel {
                color: #a78bfa;
                font-size: 14px;
                font-weight: 600;
                padding: 4px;
            }
        """)
        tags_label_layout.addWidget(tags_label_widget)
        tags_label_layout.addStretch()
        
        # Threshold-Einstellung
        threshold_label = QLabel("Threshold:")
        threshold_label.setStyleSheet("color: #888; font-size: 11px;")
        tags_label_layout.addWidget(threshold_label)
        
        self.threshold_spinbox = QDoubleSpinBox()
        self.threshold_spinbox.setMinimum(0.1)
        self.threshold_spinbox.setMaximum(0.9)
        self.threshold_spinbox.setSingleStep(0.05)
        self.threshold_spinbox.setValue(0.20)
        self.threshold_spinbox.setDecimals(2)
        self.threshold_spinbox.setStyleSheet("""
            QDoubleSpinBox {
                background: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 4px 8px;
                color: #e0e0e0;
                font-size: 11px;
                min-width: 60px;
            }
            QDoubleSpinBox:hover {
                border: 1px solid #4a4a4a;
            }
        """)
        self.threshold_spinbox.valueChanged.connect(self.on_threshold_changed)
        tags_label_layout.addWidget(self.threshold_spinbox)
        
        tags_label.setLayout(tags_label_layout)
        tags_layout.addWidget(tags_label)
        
        # Optionen für Tag-Verarbeitung
        options_widget = QWidget()
        options_layout = QVBoxLayout()
        options_layout.setContentsMargins(8, 8, 8, 8)
        options_layout.setSpacing(8)
        
        # Checkbox: Unterstriche durch Leerzeichen ersetzen
        self.use_spaces_checkbox = QCheckBox("Unterstriche durch Leerzeichen ersetzen")
        self.use_spaces_checkbox.setChecked(True)
        self.use_spaces_checkbox.setStyleSheet("""
            QCheckBox {
                color: #d0d0d0;
                font-size: 11px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
        """)
        self.use_spaces_checkbox.stateChanged.connect(self.on_options_changed)
        options_layout.addWidget(self.use_spaces_checkbox)
        
        # Checkbox: Alphabetisch sortieren
        self.sort_alphabetical_checkbox = QCheckBox("Alphabetisch sortieren")
        self.sort_alphabetical_checkbox.setChecked(False)
        self.sort_alphabetical_checkbox.setStyleSheet("""
            QCheckBox {
                color: #d0d0d0;
                font-size: 11px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
        """)
        self.sort_alphabetical_checkbox.stateChanged.connect(self.on_options_changed)
        options_layout.addWidget(self.sort_alphabetical_checkbox)
        
        # Exclude Tags Input
        exclude_layout = QHBoxLayout()
        exclude_label = QLabel("Tags ausschließen:")
        exclude_label.setStyleSheet("color: #888; font-size: 11px;")
        exclude_label.setMinimumWidth(120)
        exclude_layout.addWidget(exclude_label)
        
        self.exclude_tags_input = QLineEdit()
        self.exclude_tags_input.setPlaceholderText("z.B. monochrome, greyscale (kommagetrennt)")
        self.exclude_tags_input.setStyleSheet("""
            QLineEdit {
                background: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 4px 8px;
                color: #e0e0e0;
                font-size: 11px;
            }
            QLineEdit:hover {
                border: 1px solid #4a4a4a;
            }
        """)
        self.exclude_tags_input.textChanged.connect(self.on_options_changed)
        exclude_layout.addWidget(self.exclude_tags_input)
        options_layout.addLayout(exclude_layout)
        
        options_widget.setLayout(options_layout)
        tags_layout.addWidget(options_widget)
        
        # Progress-Animation
        self.progress_bar = AnimatedProgressBar()
        self.progress_bar.setVisible(False)
        tags_layout.addWidget(self.progress_bar)
        
        self.tag_display = TagDisplay()
        tags_layout.addWidget(self.tag_display, stretch=1)
        
        # Aktions-Buttons
        self.action_buttons = ActionButtons()
        self.action_buttons.copy_clicked.connect(self.copy_tags)
        self.action_buttons.export_clicked.connect(self.export_tags)
        self.action_buttons.refresh_clicked.connect(self.refresh_tags)
        self.action_buttons.clear_clicked.connect(self.clear_all)
        tags_layout.addWidget(self.action_buttons)
        
        tags_widget.setLayout(tags_layout)
        splitter.addWidget(tags_widget)
        
        # Splitter-Verhältnis
        splitter.setSizes([300, 700])
        main_layout.addWidget(splitter, stretch=3)
        
        # Status-Bar
        self.statusBar().showMessage("Bereit - Ziehen Sie Bilder in den Bereich oben")
        
        central_widget.setLayout(main_layout)
    
    def setup_tagger(self):
        """Initialisiert beide Tagger."""
        try:
            # Threshold: Höherer Wert = nur relevantere Tags (Standard: 0.20)
            # Empfohlen: 0.20-0.35 für mehr Tags, 0.35-0.45 für bessere Qualität
            threshold = self.threshold_spinbox.value() if hasattr(self, 'threshold_spinbox') else 0.20
            self.statusBar().showMessage("Lade Tagger 1...")
            QApplication.processEvents()  # UI aktualisieren
            
            # Tagger 1: Standard WD14 (lokales Modell oder wdtagger Standard)
            self.tagger1 = WD14Tagger(threshold=threshold, use_local=True)
            
            self.statusBar().showMessage("Lade Tagger 2...")
            QApplication.processEvents()
            
            # Tagger 2: SwinV2-Variante (falls verfügbar, sonst auch Standard)
            try:
                # Versuche SwinV2-Modell zu verwenden (falls wdtagger verfügbar)
                from wdtagger import Tagger as WDTaggerClass
                self.tagger2 = WD14Tagger(threshold=threshold, use_local=False)
                # Falls lokales Modell verwendet wurde, versuche trotzdem einen zweiten Tagger
                if self.tagger1.local_loader is not None:
                    # Erstelle zweiten Tagger mit wdtagger (SwinV2)
                    self.tagger2.wdtagger = WDTaggerClass(model_repo="SmilingWolf/wd-swinv2-tagger-v3")
                    self.tagger2.local_loader = None
            except:
                # Fallback: Verwende denselben Tagger zweimal (besser als nichts)
                self.tagger2 = WD14Tagger(threshold=threshold, use_local=True)
            
            self.statusBar().showMessage("Beide Tagger geladen - Bereit zum Taggen")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Fehler beim Laden der Tagger:\n{str(e)}\n\n"
                "Stellen Sie sicher, dass alle Dependencies installiert sind."
            )
            self.statusBar().showMessage("Fehler beim Laden der Tagger")
    
    def on_files_dropped(self, file_paths: list):
        """Wird aufgerufen wenn Dateien per Drag & Drop hinzugefügt werden."""
        # Filtere nur Bilder
        image_files = FileHandler.filter_image_files(file_paths)
        
        if not image_files:
            QMessageBox.warning(
                self,
                "Keine Bilder",
                "Bitte wählen Sie gültige Bilddateien aus."
            )
            return
        
        # Verwende das erste Bild
        image_path = image_files[0]
        self.process_image(image_path)
    
    def process_image(self, image_path: str):
        """Verarbeitet ein Bild und generiert Tags."""
        if not self.tagger1 or not self.tagger2:
            QMessageBox.warning(
                self,
                "Modell nicht geladen",
                "Die Tagger-Modelle konnten nicht geladen werden."
            )
            return
        
        # Validiere Bild
        if not FileHandler.validate_image(image_path):
            QMessageBox.warning(
                self,
                "Ungültiges Bild",
                "Die ausgewählte Datei ist kein gültiges Bild."
            )
            return
        
        self.current_image_path = image_path
        
        # Zeige Bildvorschau
        self.image_preview.set_image(image_path)
        
        # Starte Tagging im Hintergrund
        self.start_tagging(image_path)
    
    def on_threshold_changed(self, value: float):
        """Wird aufgerufen wenn der Threshold geändert wird."""
        # Aktualisiere Threshold für beide Tagger
        try:
            if self.tagger1:
                self.tagger1.threshold = value
            if self.tagger2:
                self.tagger2.threshold = value
            self.statusBar().showMessage(f"Threshold auf {value:.2f} gesetzt")
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Konnte Threshold nicht aktualisieren:\n{str(e)}")
    
    def start_tagging(self, image_path: str):
        """Startet das Tagging mit beiden Taggern in einem separaten Thread."""
        if not self.tagger1 or not self.tagger2:
            QMessageBox.warning(self, "Fehler", "Tagger nicht initialisiert!")
            return
        
        # Stelle sicher, dass beide Tagger den aktuellen Threshold verwenden
        current_threshold = self.threshold_spinbox.value() if hasattr(self, 'threshold_spinbox') else 0.20
        if self.tagger1.threshold != current_threshold:
            self.tagger1.threshold = current_threshold
        if self.tagger2.threshold != current_threshold:
            self.tagger2.threshold = current_threshold
        
        # Stoppe vorherigen Worker falls vorhanden
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()
        
        # Zeige Progress-Animation
        self.progress_bar.setVisible(True)
        self.progress_bar.start_animation()
        self.progress_bar.set_progress(0)
        
        # Erstelle neuen Worker mit beiden Taggern
        self.worker = TaggingWorker(self.tagger1, self.tagger2, image_path)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        
        # Verbinde Signale
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_tagging_finished)
        self.worker.error.connect(self.on_tagging_error)
        self.worker.progress.connect(self.on_progress_update)
        
        # Starte Thread
        self.worker_thread.start()
        self.statusBar().showMessage(f"🔄 Analysiere {Path(image_path).name} mit beiden Taggern...")
    
    def on_progress_update(self, message: str, progress: int):
        """Wird aufgerufen wenn Progress aktualisiert wird."""
        self.progress_bar.set_progress(progress)
        self.statusBar().showMessage(message)
    
    def process_tags(self, tags: list) -> list:
        """Verarbeitet Tags basierend auf den Optionen."""
        processed_tags = tags.copy()
        
        # 1. Tags ausschließen (vor dem Ersetzen von Unterstrichen)
        exclude_text = self.exclude_tags_input.text().strip()
        if exclude_text:
            # Filtere leere Einträge heraus
            exclude_list = [t.strip().lower() for t in exclude_text.split(',') if t.strip()]
            if exclude_list:  # Nur filtern, wenn tatsächlich Tags zum Ausschließen vorhanden sind
                # Vergleiche sowohl mit Unterstrichen als auch ohne (für Flexibilität)
                processed_tags = [
                    (tag, conf) for tag, conf in processed_tags
                    if tag.lower() not in exclude_list and tag.lower().replace('_', ' ') not in exclude_list
                ]
        
        # 2. Unterstriche durch Leerzeichen ersetzen (wenn aktiviert)
        # WICHTIG: Kaomojis behalten ihre Unterstriche!
        if self.use_spaces_checkbox.isChecked():
            processed_tags = [
                (tag if tag in self.kaomojis else tag.replace('_', ' '), conf) 
                for tag, conf in processed_tags
            ]
        
        # 3. Alphabetisch sortieren (wenn aktiviert), sonst nach Konfidenz
        if self.sort_alphabetical_checkbox.isChecked():
            processed_tags.sort(key=lambda x: x[0].lower())
        else:
            processed_tags.sort(key=lambda x: x[1], reverse=True)
        
        return processed_tags
    
    def on_tagging_finished(self, image_path: str, tags: list, tagger_name: str = ""):
        """Wird aufgerufen wenn Tagging abgeschlossen ist."""
        # Stoppe Progress-Animation
        if hasattr(self, 'progress_bar'):
            self.progress_bar.stop_animation()
            self.progress_bar.setVisible(False)
        
        # Speichere ursprüngliche Tags
        self.raw_tags = tags.copy()
        self.selected_tagger_name = tagger_name
        
        # Hole Rating-Tags vom Tagger
        if self.tagger1 and hasattr(self.tagger1, 'rating_tags'):
            self.rating_tags = self.tagger1.rating_tags.copy()
        elif self.tagger2 and hasattr(self.tagger2, 'rating_tags'):
            self.rating_tags = self.tagger2.rating_tags.copy()
        
        # Verarbeite Tags basierend auf Optionen
        processed_tags = self.process_tags(tags)
        
        # Begrenze auf maximal 25 Tags
        max_tags = 25
        self.current_tags = processed_tags[:max_tags] if len(processed_tags) > max_tags else processed_tags
        
        # Zeige Tags mit Rating-Tags an
        self.tag_display.display_tags(
            self.current_tags, 
            include_confidence=True, 
            max_tags=max_tags,
            rating_tags=self.rating_tags
        )
        
        displayed_count = len(self.current_tags)
        tagger_info = f" ({tagger_name})" if tagger_name else ""
        self.statusBar().showMessage(
            f"✅ Fertig - {displayed_count} Tags generiert{tagger_info} für {Path(image_path).name}"
        )
        
        # Stoppe Worker-Thread
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
    
    def on_tagging_error(self, image_path: str, error_message: str):
        """Wird aufgerufen wenn ein Fehler beim Tagging auftritt."""
        # Stoppe Progress-Animation
        self.progress_bar.stop_animation()
        self.progress_bar.setVisible(False)
        
        QMessageBox.critical(
            self,
            "Tagging-Fehler",
            f"Fehler beim Verarbeiten von {Path(image_path).name}:\n{error_message}"
        )
        self.statusBar().showMessage("Fehler beim Tagging")
        
        # Stoppe Worker-Thread
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
    
    def copy_tags(self):
        """Kopiert die Tags in die Zwischenablage (maximal 25 Tags)."""
        if not self.current_tags:
            QMessageBox.information(self, "Keine Tags", "Es sind keine Tags zum Kopieren vorhanden.")
            return
        
        # Stelle sicher, dass wir maximal 25 Tags kopieren
        tags_to_copy = self.current_tags[:25]
        tag_strings = [tag for tag, _ in tags_to_copy]
        prompt_text = ', '.join(tag_strings)
        
        clipboard = QApplication.clipboard()
        clipboard.setText(prompt_text)
        
        tag_count = len(tags_to_copy)
        self.statusBar().showMessage(f"{tag_count} Tags in Zwischenablage kopiert!")
        QMessageBox.information(self, "Kopiert", f"{tag_count} Tags wurden in die Zwischenablage kopiert.")
    
    def export_tags(self):
        """Exportiert die Tags in eine Datei (maximal 25 Tags)."""
        if not self.current_tags:
            QMessageBox.information(self, "Keine Tags", "Es sind keine Tags zum Exportieren vorhanden.")
            return
        
        # Stelle sicher, dass wir maximal 25 Tags exportieren
        tags_to_export = self.current_tags[:25]
        
        # Wähle Speicherort
        default_name = ""
        if self.current_image_path:
            default_name = Path(self.current_image_path).stem + "_tags.txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Tags speichern",
            default_name,
            "Textdateien (*.txt);;Alle Dateien (*)"
        )
        
        if file_path:
            try:
                image_name = Path(self.current_image_path).name if self.current_image_path else ""
                FileHandler.save_tags_to_file(file_path, tags_to_export, image_name)
                tag_count = len(tags_to_export)
                self.statusBar().showMessage(f"{tag_count} Tags gespeichert: {file_path}")
                QMessageBox.information(self, "Gespeichert", f"{tag_count} Tags wurden gespeichert:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern:\n{str(e)}")
    
    def on_options_changed(self):
        """Wird aufgerufen wenn Tag-Optionen geändert werden."""
        # Wenn ursprüngliche Tags vorhanden sind, verarbeite sie neu
        if hasattr(self, 'raw_tags') and self.raw_tags:
            processed_tags = self.process_tags(self.raw_tags)
            max_tags = 25
            self.current_tags = processed_tags[:max_tags] if len(processed_tags) > max_tags else processed_tags
            self.tag_display.display_tags(
                self.current_tags, 
                include_confidence=True, 
                max_tags=max_tags,
                rating_tags=self.rating_tags if hasattr(self, 'rating_tags') else None
            )
    
    def refresh_tags(self):
        """Aktualisiert die Tags für das aktuelle Bild."""
        if not self.current_image_path:
            QMessageBox.information(
                self,
                "Kein Bild",
                "Es ist kein Bild geladen. Bitte laden Sie zuerst ein Bild."
            )
            return
        
        if not self.tagger1 or not self.tagger2:
            QMessageBox.warning(self, "Fehler", "Tagger nicht initialisiert!")
            return
        
        # Stelle sicher, dass beide Tagger den aktuellen Threshold verwenden
        current_threshold = self.threshold_spinbox.value() if hasattr(self, 'threshold_spinbox') else 0.20
        if self.tagger1.threshold != current_threshold:
            self.tagger1.threshold = current_threshold
        if self.tagger2.threshold != current_threshold:
            self.tagger2.threshold = current_threshold
        
        # Starte Tagging erneut
        self.statusBar().showMessage(f"Aktualisiere Tags für {Path(self.current_image_path).name}...")
        self.start_tagging(self.current_image_path)
    
    def clear_all(self):
        """Setzt alles zurück."""
        self.current_image_path = None
        self.current_tags = []
        self.image_preview.setText("Kein Bild")
        self.tag_display.clear()
        self.statusBar().showMessage("Zurückgesetzt - Bereit für neues Bild")
    
    def apply_dark_theme(self):
        """Wendet das elegante Dark Theme an."""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a1a, stop:1 #0f0f0f);
                color: #e0e0e0;
            }
            QWidget {
                background: transparent;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 13px;
            }
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #252525, stop:1 #1a1a1a);
                color: #a78bfa;
                border-top: 1px solid #3a3a3a;
                font-size: 11px;
                font-weight: 500;
            }
            QSplitter::handle {
                background: #2a2a2a;
                border: 1px solid #3a3a3a;
            }
            QSplitter::handle:horizontal {
                width: 3px;
            }
            QSplitter::handle:hover {
                background: #3a3a3a;
            }
        """)
    
    def closeEvent(self, event):
        """Wird aufgerufen wenn das Fenster geschlossen wird."""
        # Stoppe Worker-Thread falls aktiv
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()
        event.accept()


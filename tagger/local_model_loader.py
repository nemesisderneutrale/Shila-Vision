"""Lokaler Modell-Lader für WD 1.4 Tagger mit ONNX."""

import os
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import csv

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False


class LocalWD14ModelLoader:
    """Lädt und verwaltet das lokale WD 1.4 Tagger Modell mit ONNX."""
    
    def __init__(self, model_dir: str = "Modeltagger"):
        """
        Initialisiert den lokalen Modell-Lader.
        
        Args:
            model_dir: Pfad zum Modell-Verzeichnis
        """
        self.model_dir = Path(model_dir)
        self.session: Optional[ort.InferenceSession] = None
        self.tags: Dict[int, str] = {}
        self.device = "cpu"  # Für i5 11600k verwenden wir CPU
        self.loaded = False
        
        # Prüfe ob CUDA verfügbar ist (optional, für spätere GPU-Nutzung)
        if ONNX_AVAILABLE:
            try:
                providers = ort.get_available_providers()
                if 'CUDAExecutionProvider' in providers:
                    # CUDA ist verfügbar, aber für i5 11600k (keine dedizierte GPU) verwenden wir CPU
                    self.device = "cpu"
                else:
                    self.device = "cpu"
            except:
                self.device = "cpu"
    
    def load_tags(self) -> Dict[int, str]:
        """Lädt die Tags aus selected_tags.csv."""
        tags_file = self.model_dir / "selected_tags.csv"
        
        if not tags_file.exists():
            raise FileNotFoundError(f"Tags-Datei nicht gefunden: {tags_file}")
        
        tags = {}
        try:
            with open(tags_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                # Verwende Zeilen-Index als Key (0-basiert), da das Modell-Output
                # wahrscheinlich nach Reihenfolge in der CSV indiziert ist
                for idx, row in enumerate(reader):
                    tag_name = row['name']
                    tags[idx] = tag_name
        except Exception as e:
            raise Exception(f"Fehler beim Laden der Tags: {e}")
        
        return tags
    
    def load_model(self):
        """
        Lädt das lokale ONNX-Modell.
        
        Returns:
            ONNX Inference Session
        """
        if self.loaded and self.session is not None:
            return self.session
        
        if not ONNX_AVAILABLE:
            raise ImportError(
                "onnxruntime ist nicht installiert. Bitte installieren Sie es mit:\n"
                "pip install onnxruntime"
            )
        
        model_file = self.model_dir / "model.onnx"
        
        if not model_file.exists():
            raise FileNotFoundError(f"ONNX-Modell nicht gefunden: {model_file}")
        
        print(f"Lade lokales WD 1.4 Tagger Modell: {model_file}")
        print(f"Verwende Device: {self.device}")
        
        try:
            # Erstelle ONNX Runtime Session
            # Für CPU verwenden wir nur CPUExecutionProvider
            providers = ['CPUExecutionProvider']
            
            # Optionale CUDA-Unterstützung (falls GPU verfügbar)
            # Für i5 11600k (keine dedizierte GPU) bleibt es bei CPU
            try:
                available_providers = ort.get_available_providers()
                if 'CUDAExecutionProvider' in available_providers:
                    # CUDA ist verfügbar, aber wir verwenden CPU für bessere Kompatibilität
                    # providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
                    pass
            except:
                pass
            
            self.session = ort.InferenceSession(
                str(model_file),
                providers=providers
            )
            
            # Lade Tags
            self.tags = self.load_tags()
            
            self.loaded = True
            print(f"Modell erfolgreich geladen! ({len(self.tags)} Tags)")
            
            return self.session
            
        except Exception as e:
            print(f"Fehler beim Laden des Modells: {e}")
            raise
    
    def get_model(self):
        """Gibt die ONNX Session zurück."""
        if not self.loaded:
            self.load_model()
        return self.session
    
    def get_tags(self) -> Dict[int, str]:
        """Gibt die Tag-Liste zurück."""
        if not self.loaded:
            self.load_model()
        return self.tags
    
    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """
        Verarbeitet ein Bild für das ONNX-Modell mit verbesserter Bildverarbeitung.
        
        Args:
            image: PIL Image
            
        Returns:
            Preprocessed image as numpy array (BGR, float32, shape: (1, H, W, 3))
        """
        try:
            from utils.image_processing import preprocess_for_wd14
            # Verwende verbesserte Bildverarbeitung
            # Das Modell erwartet [0, 255] Werte in float32, KEINE Normalisierung!
            img_bgr = preprocess_for_wd14(image, target_size=448)
            return img_bgr
            
        except ImportError:
            # Fallback auf alte Methode falls opencv nicht verfügbar
            # Resize auf 448x448 (Standard für WD14 ViT Tagger V2)
            image = image.resize((448, 448), Image.Resampling.LANCZOS)
            
            # Konvertiere zu RGB falls nötig
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Konvertiere zu numpy array
            # Format: (H, W, C) = (448, 448, 3)
            img_array = np.array(image, dtype=np.float32)
            
            # Normalisiere auf [0, 1]
            img_array = img_array / 255.0
            
            # ImageNet Normalisierung (Standard für Vision Transformer)
            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
            std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
            
            # Normalisiere: (pixel - mean) / std
            img_array = (img_array - mean) / std
            
            # Füge Batch-Dimension hinzu: (1, H, W, C) = (1, 448, 448, 3)
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
    
    def is_loaded(self) -> bool:
        """Prüft ob das Modell geladen ist."""
        return self.loaded


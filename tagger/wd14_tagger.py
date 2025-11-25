"""WD 1.4 Tagger Implementation."""

import os
import sys
from pathlib import Path
from PIL import Image
from typing import List, Dict, Tuple
import numpy as np

# Versuche lokales Modell zu verwenden
try:
    from tagger.local_model_loader import LocalWD14ModelLoader
    LOCAL_MODEL_AVAILABLE = True
except ImportError:
    LOCAL_MODEL_AVAILABLE = False

# wdtagger wird nur bei Bedarf importiert (lazy import)
WDTAGGER_AVAILABLE = None  # None = noch nicht geprüft
WDTagger = None


class WD14Tagger:
    """Hauptklasse für das Tagging von Bildern mit WD 1.4."""
    
    def __init__(self, model_name: str = None, threshold: float = 0.20, use_local: bool = True):
        """
        Initialisiert den Tagger.
        
        Args:
            model_name: HuggingFace Modell-Name (optional, nur wenn use_local=False)
            threshold: Schwellenwert für Tag-Konfidenz (0.0-1.0)
            use_local: Ob lokales Modell verwendet werden soll (Standard: True)
        """
        self.threshold = threshold
        self.use_local = use_local
        self.local_loader = None
        self.wdtagger = None
        self.rating_tags = {}  # Rating-Tags (general, sensitive, questionable, explicit)
        
        # Versuche zuerst lokales Modell zu verwenden
        if use_local and LOCAL_MODEL_AVAILABLE:
            # Prüfe verschiedene mögliche Pfade (für .exe und normale Ausführung)
            possible_paths = [
                Path("Modeltagger"),  # Relativer Pfad
                Path(__file__).parent.parent / "Modeltagger",  # Relativ zum Code
                Path(sys.executable).parent / "Modeltagger" if hasattr(sys, 'frozen') else None,  # Bei .exe
                Path(sys._MEIPASS) / "Modeltagger" if hasattr(sys, '_MEIPASS') else None,  # PyInstaller temp dir
            ]
            
            model_dir = None
            for path in possible_paths:
                if path and path.exists() and (path / "model.onnx").exists():
                    model_dir = path
                    break
            
            if model_dir:
                try:
                    print(f"Verwende lokales Modell aus {model_dir}")
                    self.local_loader = LocalWD14ModelLoader(str(model_dir))
                    self.local_loader.load_model()
                    return
                except Exception as e:
                    print(f"Fehler beim Laden des lokalen Modells: {e}")
                    print("Falle zurück auf wdtagger...")
        
        # Fallback: wdtagger (nur wenn lokales Modell nicht funktioniert hat)
        # Importiere wdtagger nur hier, nicht auf Modul-Ebene
        try:
            from wdtagger import Tagger as WDTaggerClass
            print("Verwende wdtagger (HuggingFace Modell)")
            if model_name is None:
                self.wdtagger = WDTaggerClass()  # Verwendet Standard-Modell
            else:
                self.wdtagger = WDTaggerClass(model_repo=model_name)
        except ImportError as e:
            raise ImportError(
                f"Weder lokales Modell noch wdtagger verfügbar.\n"
                f"Fehler: {e}\n\n"
                f"Bitte stellen Sie sicher, dass Modeltagger/model.onnx existiert,\n"
                f"oder installieren Sie wdtagger mit: pip install wdtagger"
            )
    
    
    def tag_image(self, image_path: str) -> List[Tuple[str, float]]:
        """
        Taggt ein einzelnes Bild.
        
        Args:
            image_path: Pfad zum Bild
            
        Returns:
            Liste von (tag, confidence) Tupeln, sortiert nach Konfidenz
        """
        try:
            # Lade Bild
            image = Image.open(image_path).convert("RGB")
            
            # Verwende lokales Modell falls verfügbar
            if self.local_loader is not None:
                return self._tag_with_local_model(image)
            
            # Fallback: wdtagger
            if self.wdtagger is not None:
                # wdtagger verwendet .tag() nicht .predict()
                result = self.wdtagger.tag(image, general_threshold=self.threshold)
                # Result hat general_tag, character_tag, rating_data
                tag_results = []
                
                # Extrahiere Rating-Tags
                if hasattr(result, 'rating_data'):
                    self.rating_tags = {k: float(v) for k, v in result.rating_data.items()}
                
                # Kombiniere general und character tags
                if hasattr(result, 'general_tag'):
                    tag_results.extend([(tag, float(conf)) for tag, conf in result.general_tag.items()])
                if hasattr(result, 'character_tag'):
                    tag_results.extend([(tag, float(conf)) for tag, conf in result.character_tag.items()])
                tag_results.sort(key=lambda x: x[1], reverse=True)
                return tag_results
            
            return []
            
        except Exception as e:
            print(f"Fehler beim Taggen des Bildes {image_path}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _tag_with_local_model(self, image: Image.Image) -> List[Tuple[str, float]]:
        """
        Taggt ein Bild mit dem lokalen ONNX-Modell.
        
        Args:
            image: PIL Image
            
        Returns:
            Liste von (tag, confidence) Tupeln, sortiert nach Konfidenz
        """
        import onnxruntime as ort
        
        # Preprocess Bild
        input_array = self.local_loader.preprocess_image(image)
        
        # Führe Inference durch
        session = self.local_loader.get_model()
        input_name = session.get_inputs()[0].name
        
        outputs = session.run(None, {input_name: input_array})
        
        # Output ist normalerweise ein Array mit Wahrscheinlichkeiten
        probabilities = outputs[0][0]  # Entferne Batch-Dimension
        
        # Wende Sigmoid an (falls noch nicht angewendet)
        # ONNX-Modelle geben oft bereits Sigmoid-Werte zurück
        if probabilities.max() > 1.0 or probabilities.min() < 0.0:
            # Falls nicht normalisiert, wende Sigmoid an
            try:
                from scipy.special import expit
                probabilities = expit(probabilities)
            except ImportError:
                # Fallback: Manuelle Sigmoid-Implementierung
                probabilities = 1.0 / (1.0 + np.exp(-np.clip(probabilities, -500, 500)))
        
        # Extrahiere Tags über Schwellenwert
        tags = self.local_loader.get_tags()
        tag_results = []
        rating_tags = {}  # Rating-Tags (erste 4: general, sensitive, questionable, explicit)
        
        for idx, prob in enumerate(probabilities):
            tag_name = tags.get(idx, f"tag_{idx}")
            
            # Die ersten 4 Tags sind Rating-Tags (general, sensitive, questionable, explicit)
            if idx < 4:
                rating_tags[tag_name] = float(prob)
            else:
                # Normale Tags nur wenn über Threshold
                if prob >= self.threshold:
                    tag_results.append((tag_name, float(prob)))
        
        # Sortiere nach Konfidenz (absteigend)
        tag_results.sort(key=lambda x: x[1], reverse=True)
        
        # Speichere Rating-Tags für spätere Verwendung
        self.rating_tags = rating_tags
        
        return tag_results
    
    def tag_images(self, image_paths: List[str]) -> Dict[str, List[Tuple[str, float]]]:
        """
        Taggt mehrere Bilder.
        
        Args:
            image_paths: Liste von Bildpfaden
            
        Returns:
            Dictionary mit Bildpfad als Key und Tag-Liste als Value
        """
        results = {}
        for image_path in image_paths:
            results[image_path] = self.tag_image(image_path)
        return results
    
    def format_tags_as_prompt(self, tags: List[Tuple[str, float]], 
                             include_confidence: bool = False,
                             max_tags: int = None) -> str:
        """
        Formatiert Tags als Prompt-String.
        
        Args:
            tags: Liste von (tag, confidence) Tupeln
            include_confidence: Ob Konfidenz-Werte angezeigt werden sollen
            max_tags: Maximale Anzahl von Tags (None = alle)
            
        Returns:
            Formatierter Prompt-String
        """
        if max_tags:
            tags = tags[:max_tags]
        
        if include_confidence:
            tag_strings = [f"{tag} ({conf:.2f})" for tag, conf in tags]
        else:
            tag_strings = [tag for tag, _ in tags]
        
        return ", ".join(tag_strings)
    
    def set_threshold(self, threshold: float):
        """Setzt den Schwellenwert für Tag-Konfidenz."""
        self.threshold = max(0.0, min(1.0, threshold))


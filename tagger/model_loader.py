"""Modell-Lader für WD 1.4 Tagger."""

import os
import torch
import torchvision.transforms as transforms
from PIL import Image
from typing import Optional, Tuple
import numpy as np


class WD14ModelLoader:
    """Lädt und verwaltet das WD 1.4 Tagger Modell."""
    
    def __init__(self, model_name: str = "SmilingWolf/wd-v1-4-vit-tagger-v2"):
        """
        Initialisiert den Modell-Lader.
        
        Args:
            model_name: HuggingFace Modell-Name oder lokaler Pfad
        """
        self.model_name = model_name
        self.model: Optional[torch.nn.Module] = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.loaded = False
    
    def load_model(self):
        """
        Lädt das Modell und den Image Processor.
        
        Returns:
            Tuple von (model, processor)
        """
        if self.loaded and self.model is not None:
            return self.model, self.processor
        
        print(f"Lade WD 1.4 Tagger Modell: {self.model_name}")
        print(f"Verwende Device: {self.device}")
        
        try:
            from transformers import AutoImageProcessor, AutoModelForImageClassification
            
            # Versuche das Modell zu laden
            print("Versuche Modell von HuggingFace zu laden...")
            
            # Das WD14 Tagger Modell verwendet möglicherweise eine spezielle Konfiguration
            # Versuche zuerst mit AutoImageProcessor und AutoModelForImageClassification
            try:
                # Lade Image Processor
                self.processor = AutoImageProcessor.from_pretrained(
                    self.model_name,
                    trust_remote_code=True,
                    local_files_only=False
                )
                
                # Lade Modell
                self.model = AutoModelForImageClassification.from_pretrained(
                    self.model_name,
                    trust_remote_code=True,
                    local_files_only=False
                )
            except Exception as e1:
                print(f"Fehler mit AutoImageProcessor/AutoModelForImageClassification: {e1}")
                # Fallback: Versuche mit CLIP-basiertem Processor
                try:
                    from transformers import CLIPImageProcessor, CLIPModel
                    self.processor = CLIPImageProcessor.from_pretrained(
                        self.model_name,
                        trust_remote_code=True,
                        local_files_only=False
                    )
                    self.model = CLIPModel.from_pretrained(
                        self.model_name,
                        trust_remote_code=True,
                        local_files_only=False
                    )
                except Exception as e2:
                    print(f"Fehler mit CLIP-Klassen: {e2}")
                    # Letzter Fallback: Versuche mit AutoModel
                    try:
                        from transformers import AutoModel
                        self.processor = AutoImageProcessor.from_pretrained(
                            "google/vit-base-patch16-224",
                            trust_remote_code=True
                        )
                        self.model = AutoModel.from_pretrained(
                            self.model_name,
                            trust_remote_code=True,
                            local_files_only=False
                        )
                    except Exception as e3:
                        print(f"Fehler mit AutoModel: {e3}")
                        raise Exception(f"Konnte Modell nicht laden. Bitte überprüfe, ob das Modell auf HuggingFace existiert: https://huggingface.co/{self.model_name}")
            
            # Verschiebe Modell auf GPU falls verfügbar
            self.model = self.model.to(self.device)
            self.model.eval()
            
            self.loaded = True
            print("Modell erfolgreich geladen!")
            
            return self.model, self.processor
            
        except Exception as e:
            error_msg = f"Fehler beim Laden des Modells: {e}"
            print(error_msg)
            print("\nHinweis: Das Modell könnte nicht direkt verfügbar sein.")
            print("Bitte überprüfe, ob das Modell auf HuggingFace existiert:")
            print(f"https://huggingface.co/{self.model_name}")
            raise Exception(error_msg)
    
    def _create_simple_processor(self):
        """Erstellt einen einfachen Image Processor als Fallback."""
        from transformers import CLIPImageProcessor
        
        # Standard CLIP Processor als Fallback
        return CLIPImageProcessor.from_pretrained(
            "openai/clip-vit-base-patch32",
            trust_remote_code=True
        )
    
    def get_model(self):
        """Gibt das geladene Modell zurück."""
        if not self.loaded:
            self.load_model()
        return self.model
    
    def get_processor(self):
        """Gibt den Image Processor zurück."""
        if not self.loaded:
            self.load_model()
        return self.processor
    
    def is_loaded(self) -> bool:
        """Prüft ob das Modell geladen ist."""
        return self.loaded


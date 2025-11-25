"""Alternative Modell-Lader für WD 1.4 Tagger mit ONNX-Unterstützung."""

import os
import torch
import numpy as np
from PIL import Image
from typing import Optional, Tuple
from pathlib import Path

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False


class WD14ModelLoaderONNX:
    """Lädt und verwaltet das WD 1.4 Tagger Modell mit ONNX."""
    
    def __init__(self, model_name: str = "SmilingWolf/wd-v1-4-vit-tagger-v2"):
        """
        Initialisiert den Modell-Lader.
        
        Args:
            model_name: HuggingFace Modell-Name oder lokaler Pfad
        """
        self.model_name = model_name
        self.session: Optional[ort.InferenceSession] = None
        self.device = "cuda" if torch.cuda.is_available() and ONNX_AVAILABLE else "cpu"
        self.loaded = False
    
    def load_model(self):
        """
        Lädt das ONNX-Modell.
        
        Returns:
            ONNX Inference Session
        """
        if self.loaded and self.session is not None:
            return self.session
        
        if not ONNX_AVAILABLE:
            raise ImportError("onnxruntime ist nicht installiert. Bitte installieren Sie es mit: pip install onnxruntime")
        
        print(f"Lade WD 1.4 Tagger Modell (ONNX): {self.model_name}")
        print(f"Verwende Device: {self.device}")
        
        try:
            from huggingface_hub import hf_hub_download
            
            # Lade ONNX-Modell
            model_path = hf_hub_download(
                repo_id=self.model_name,
                filename="model.onnx"
            )
            
            # Erstelle ONNX Runtime Session
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if self.device == "cuda" else ['CPUExecutionProvider']
            self.session = ort.InferenceSession(
                model_path,
                providers=providers
            )
            
            self.loaded = True
            print("ONNX-Modell erfolgreich geladen!")
            
            return self.session
            
        except Exception as e:
            print(f"Fehler beim Laden des ONNX-Modells: {e}")
            raise
    
    def get_model(self):
        """Gibt die ONNX Session zurück."""
        if not self.loaded:
            self.load_model()
        return self.session
    
    def is_loaded(self) -> bool:
        """Prüft ob das Modell geladen ist."""
        return self.loaded




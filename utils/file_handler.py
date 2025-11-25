"""Datei-Handler für Bild-Verarbeitung."""

import os
from pathlib import Path
from typing import List, Set
from PIL import Image


class FileHandler:
    """Verwaltet Datei-Operationen für Bilder."""
    
    # Unterstützte Bildformate
    SUPPORTED_FORMATS: Set[str] = {
        '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff', '.tif'
    }
    
    @staticmethod
    def is_image_file(file_path: str) -> bool:
        """
        Prüft ob eine Datei ein unterstütztes Bildformat ist.
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            True wenn unterstütztes Format
        """
        ext = Path(file_path).suffix.lower()
        return ext in FileHandler.SUPPORTED_FORMATS
    
    @staticmethod
    def filter_image_files(file_paths: List[str]) -> List[str]:
        """
        Filtert eine Liste von Dateipfaden und gibt nur Bilder zurück.
        
        Args:
            file_paths: Liste von Dateipfaden
            
        Returns:
            Liste von Bildpfaden
        """
        return [fp for fp in file_paths if FileHandler.is_image_file(fp)]
    
    @staticmethod
    def validate_image(file_path: str) -> bool:
        """
        Validiert ob eine Datei ein gültiges Bild ist.
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            True wenn gültiges Bild
        """
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_image_info(file_path: str) -> dict:
        """
        Gibt Informationen über ein Bild zurück.
        
        Args:
            file_path: Pfad zum Bild
            
        Returns:
            Dictionary mit Bildinformationen
        """
        try:
            with Image.open(file_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size_mb': os.path.getsize(file_path) / (1024 * 1024)
                }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def save_tags_to_file(file_path: str, tags: List[tuple], image_name: str = ""):
        """
        Speichert Tags in eine Textdatei.
        
        Args:
            file_path: Pfad zur Ausgabedatei
            tags: Liste von (tag, confidence) Tupeln
            image_name: Name des Bildes (optional)
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if image_name:
                    f.write(f"Tags für: {image_name}\n")
                    f.write("=" * 50 + "\n\n")
                
                for tag, conf in tags:
                    f.write(f"{tag}: {conf:.4f}\n")
                
                f.write("\n" + "=" * 50 + "\n")
                f.write("Als Prompt:\n")
                tag_strings = [tag for tag, _ in tags]
                f.write(", ".join(tag_strings) + "\n")
        except Exception as e:
            raise Exception(f"Fehler beim Speichern der Tags: {e}")




"""
Modell-Download-Manager für Shila-Vision
Lädt automatisch das WD14 Tagger Modell von HuggingFace herunter.
"""

import os
import sys
from pathlib import Path
import urllib.request
from urllib.error import URLError, HTTPError


def download_file(url: str, destination: Path, description: str = ""):
    """
    Lädt eine Datei von einer URL herunter mit Progress-Anzeige.
    
    Args:
        url: URL der Datei
        destination: Ziel-Pfad
        description: Beschreibung der Datei (für Progress-Anzeige)
    """
    try:
        print(f"📥 Lade {description} herunter...")
        print(f"   URL: {url}")
        print(f"   Ziel: {destination}")
        
        # Erstelle Ziel-Ordner falls nicht vorhanden
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        def show_progress(block_num, block_size, total_size):
            """Zeigt Download-Progress an."""
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100) if total_size > 0 else 0
            size_mb = total_size / (1024 * 1024) if total_size > 0 else 0
            downloaded_mb = downloaded / (1024 * 1024)
            
            # Progress-Bar (einfach)
            bar_length = 40
            filled = int(bar_length * percent / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            print(f"\r   [{bar}] {percent:.1f}% ({downloaded_mb:.1f}/{size_mb:.1f} MB)", end='', flush=True)
        
        # Download mit Progress
        urllib.request.urlretrieve(url, destination, reporthook=show_progress)
        print("\n   ✅ Download abgeschlossen!")
        return True
        
    except HTTPError as e:
        print(f"\n   ❌ HTTP Fehler: {e.code} - {e.reason}")
        return False
    except URLError as e:
        print(f"\n   ❌ URL Fehler: {e.reason}")
        return False
    except Exception as e:
        print(f"\n   ❌ Fehler: {str(e)}")
        return False


def download_model():
    """Lädt das WD14 Tagger Modell herunter."""
    
    # Basis-URL für HuggingFace
    base_url = "https://huggingface.co/SmilingWolf/wd-v1-4-vit-tagger-v2/resolve/main"
    
    # Ziel-Ordner
    model_dir = Path("Modeltagger")
    
    # Dateien die heruntergeladen werden sollen
    files_to_download = {
        "model.onnx": f"{base_url}/model.onnx",
        "selected_tags.csv": f"{base_url}/selected_tags.csv"
    }
    
    print("=" * 60)
    print("🚀 Shila-Vision - Modell-Download-Manager")
    print("=" * 60)
    print()
    print(f"📁 Ziel-Ordner: {model_dir.absolute()}")
    print()
    
    # Prüfe ob Modell bereits vorhanden
    model_file = model_dir / "model.onnx"
    tags_file = model_dir / "selected_tags.csv"
    
    if model_file.exists() and tags_file.exists():
        print("⚠️  Modell bereits vorhanden!")
        response = input("   Möchtest du es trotzdem neu herunterladen? (j/n): ").lower()
        if response != 'j' and response != 'y':
            print("   ❌ Abgebrochen.")
            return False
        print()
    
    # Erstelle Modell-Ordner
    model_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Ordner erstellt: {model_dir.absolute()}")
    print()
    
    # Lade Dateien herunter
    success_count = 0
    for filename, url in files_to_download.items():
        destination = model_dir / filename
        
        if download_file(url, destination, filename):
            success_count += 1
        else:
            print(f"   ❌ Fehler beim Download von {filename}")
            print()
    
    print()
    print("=" * 60)
    
    # Zusammenfassung
    if success_count == len(files_to_download):
        print("✅ Alle Dateien erfolgreich heruntergeladen!")
        print()
        print(f"📦 Modell-Ordner: {model_dir.absolute()}")
        print(f"   - model.onnx")
        print(f"   - selected_tags.csv")
        print()
        print("🎉 Du kannst jetzt Shila-Vision starten!")
        return True
    else:
        print(f"⚠️  Nur {success_count}/{len(files_to_download)} Dateien heruntergeladen.")
        print("   Bitte versuche es erneut oder lade die Dateien manuell herunter.")
        print("   Siehe README-Modelle.md für weitere Informationen.")
        return False


def main():
    """Hauptfunktion."""
    try:
        success = download_model()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Download abgebrochen vom Benutzer.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unerwarteter Fehler: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


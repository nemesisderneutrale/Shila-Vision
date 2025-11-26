# Shila-Vision - Bild-Tagging Tool

Eine elegante Desktop-Anwendung für automatisches Bild-Tagging mit dem Waifu Diffusion 1.4 Tagger Modell.

![Shila-Vision Hauptansicht](screenshots/main.png)

## ✨ Features

- 🖼️ **Drag & Drop**: Ziehen Sie Bilder einfach in die Anwendung
- 🏷️ **Automatisches Tagging**: Generiert Booru-Style Tags für Ihre Bilder
- 🔄 **Multi-Tagger-System**: Zwei Tagger arbeiten parallel und wählen automatisch das beste Ergebnis
- 🧠 **Thinking Mode Engine**: Intelligente Bildanalyse vor dem Tagging für bessere Ergebnisse
- 📊 **Rating-Tags**: Separate Anzeige von General, Sensitive, Questionable, Explicit
- 📋 **Kopieren & Export**: Tags als Prompt kopieren oder als Datei speichern
- 🎨 **Dark Theme**: Modernes, augenschonendes Design mit Lila-Akzenten
- ⚙️ **Anpassbare Einstellungen**: Threshold, Tag-Filterung, Sortierung
- ⚡ **CPU-optimiert**: Läuft effizient auf Intel i5-11600K (keine GPU nötig)
- 🚀 **Standalone EXE**: Keine Python-Installation nötig

## 📦 Installation

### Option 1: Standalone EXE (Empfohlen)

1. Lade die `Shila-Vision.exe` aus dem `dist/` Ordner herunter
2. Führe die `.exe` aus - keine Installation nötig!

### Option 2: Von Quellcode

#### 1. Dependencies installieren

```bash
pip install -r requirements.txt
```

#### 2. Anwendung starten

```bash
python main.py
```

## 🎯 Verwendung

1. **Bilder hinzufügen**: 
   - Ziehen Sie Bilder per Drag & Drop in den oberen Bereich
   - Oder klicken Sie auf den Bereich, um Dateien auszuwählen

![Tagging in Aktion](screenshots/tagging.png)

2. **Tags anzeigen**: 
   - Die Tags werden automatisch generiert und angezeigt
   - Sie sehen sowohl einzelne Tags mit Konfidenz-Werten als auch den formatierten Prompt
   - Rating-Tags werden separat oben angezeigt

![Fertige Tags](screenshots/result.png)

3. **Tags anpassen**:
   - **Threshold**: Regelt wie viele Tags angezeigt werden (Standard: 0.20)
   - **Exclude Tags**: Bestimmte Tags ausschließen (z.B. "monochrome", "greyscale")
   - **Unterstriche → Leerzeichen**: Ersetzt Unterstriche durch Leerzeichen (Kaomojis bleiben geschützt)
   - **Alphabetisch sortieren**: Sortiert Tags alphabetisch statt nach Konfidenz

4. **Tags verwenden**:
   - **Kopieren**: Klicken Sie auf "Tags kopieren" um den Prompt in die Zwischenablage zu kopieren
   - **Exportieren**: Speichern Sie die Tags als Textdatei
   - **Aktualisieren**: Generiert Tags neu mit aktuellen Einstellungen

## 🔧 Technische Details

- **GUI Framework**: PySide6 (Qt 6)
- **Tagger 1**: Lokales ONNX-Modell (`Modeltagger/model.onnx`)
- **Tagger 2**: SwinV2-Modell via wdtagger (HuggingFace)
- **Bildverarbeitung**: OpenCV für verbesserte Preprocessing-Qualität
- **Python Version**: 3.10.6+
- **CPU**: Optimiert für Intel i5-11600K (keine dedizierte GPU nötig)

## 📁 Projektstruktur

```
WD1.4/
├── main.py                          # Hauptanwendung
├── gui/                             # GUI Module
│   ├── main_window.py              # Hauptfenster & Logik
│   └── components.py                # UI-Komponenten
├── tagger/                          # Tagger Module
│   ├── wd14_tagger.py              # WD14 Tagger Integration
│   └── local_model_loader.py       # Lokaler ONNX Modell-Lader
├── utils/                           # Utility Module
│   ├── file_handler.py             # Datei-Verarbeitung
│   └── image_processing.py         # Bildverarbeitungs-Utilities
├── Modeltagger/                     # Lokales KI-Modell
│   ├── model.onnx                  # ONNX-Modell (~50-100MB)
│   └── selected_tags.csv           # Tag-Datenbank (~9000 Tags)
├── requirements.txt                 # Dependencies
├── build_exe.bat                    # PyInstaller Build-Script
└── README.md                        # Diese Datei
```

## 🎨 Features im Detail

### Multi-Tagger-System
Die Anwendung nutzt zwei verschiedene Tagger-Modelle:
- **Tagger 1**: Lokales ONNX-Modell (schnell, offline)
- **Tagger 2**: SwinV2-Modell (via wdtagger, HuggingFace)

Beide Tagger arbeiten parallel und die Anwendung wählt automatisch das beste Ergebnis basierend auf:
- Durchschnittliche Konfidenz der Top 25 Tags
- Anzahl relevanter Tags (≥0.5 Konfidenz)

### Thinking Mode Engine
Vor dem eigentlichen Tagging analysiert die Anwendung das Bild:
- Bildgröße, Format, Modus
- Dominante Farben
- Helligkeit, Kontrast, Farbintensität
- Bildtyp (Foto vs. Illustration)
- Komposition und Objekterkennung

Diese Analyse hilft dem System, bessere Tags zu generieren.

![Thinking Mode Engine](screenshots/thinking.png)

### Rating-Tags
Die ersten 4 Tags sind spezielle Rating-Tags:
- **General**: Allgemeine Inhalte
- **Sensitive**: Sensible Inhalte
- **Questionable**: Fragwürdige Inhalte
- **Explicit**: Explizite Inhalte

Diese werden separat angezeigt mit farbcodierter Konfidenz-Anzeige.

### Verbesserte Bildverarbeitung
Die Anwendung verwendet erweiterte Bildverarbeitung:
- Alpha-Kanäle werden zu weißem Hintergrund konvertiert
- Bilder werden intelligent quadratisch gemacht (Padding)
- Smart Resize für optimale Qualität
- BGR-Format für bessere Modell-Kompatibilität

## 📝 Hinweise

- **Lokales Modell**: Das Modell wird aus dem `Modeltagger/` Ordner geladen
- **Fallback**: Falls kein lokales Modell gefunden wird, wird wdtagger verwendet
- **Threshold**: Niedrigere Werte (0.20) = mehr Tags, höhere Werte (0.35+) = weniger, aber relevantere Tags
- **Kaomojis**: Tags wie `0_0`, `^_^`, `o_o` behalten ihre Unterstriche auch bei "Unterstriche → Leerzeichen"

## 🐛 Bekannte Probleme und Lösungen

### Problem: Modell kann nicht geladen werden

Falls das Modell nicht geladen werden kann:

1. **Überprüfe den Modeltagger-Ordner**: Stelle sicher, dass `Modeltagger/model.onnx` und `Modeltagger/selected_tags.csv` vorhanden sind
2. **Fallback**: Die Anwendung verwendet automatisch wdtagger als Fallback
3. **Internetverbindung**: Für wdtagger wird eine Internetverbindung benötigt (HuggingFace-Download)

### Problem: Qt-Warnung "Unhandled scheme: data"

Diese Warnung ist harmlos und wurde behoben. Sie tritt auf, wenn "data:" URLs beim Drag & Drop erkannt werden, die ignoriert werden.

## 🚀 Build (EXE erstellen)

Um eine Standalone-EXE zu erstellen:

```bash
build_exe.bat
```

Die EXE wird im `dist/` Ordner erstellt.

**Hinweis**: Die EXE ist ~927MB groß, da sie alle Dependencies enthält (Python Runtime, Qt, ONNX, Modell, etc.).

## 📄 Lizenz

Public Domain (ähnlich dem Original WD14 Tagger)

## 🙏 Credits

- **Waifu Diffusion 1.4 Tagger**: Basierend auf dem Modell von SmilingWolf
- **Bildverarbeitung**: Inspiriert von `stable-diffusion-webui-wd14-tagger`
- **wdtagger**: Python-Bibliothek für WD14 Tagger Modelle

---

**Shila-Vision** - Elegantes Bild-Tagging für alle! ✨

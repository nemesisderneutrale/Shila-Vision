# Shila-Vision - Bild-Tagging Tool

Eine elegante Desktop-Anwendung für automatisches Bild-Tagging mit dem Waifu Diffusion 1.4 Tagger Modell.

![Shila-Vision Screenshot](screenshots/main_window.png)
*Hauptfenster der Shila-Vision Anwendung*

![Shila-Vision Tagging](screenshots/tagging_example.png)
*Beispiel: Automatisches Tagging eines Bildes*

## ✨ Features

- 🖼️ **Drag & Drop**: Ziehen Sie Bilder einfach in die Anwendung
- 🏷️ **Automatisches Tagging**: Generiert Booru-Style Tags für Ihre Bilder
- 🔄 **Multi-Tagger-System**: Zwei Tagger arbeiten parallel und wählen automatisch das beste Ergebnis
- 🧠 **Thinking Mode Engine**: Intelligente Bildanalyse vor dem Tagging für bessere Ergebnisse
- 📊 **Rating-Tags**: Separate Anzeige von General, Sensitive, Questionable, Explicit
- 📋 **Kopieren & Export**: Tags als Prompt kopieren oder als Datei speichern
- 🎨 **Dark Theme**: Modernes, augenschonendes Design mit Lila-Akzenten
- ⚙️ **Anpassbare Einstellungen**: Threshold, Tag-Filterung, Sortierung
- ⚡ **CPU-optimiert**: Läuft effizient auf CPU (keine GPU nötig)
- 🚀 **Standalone EXE**: Keine Python-Installation nötig

## 📦 Installation

### Option 1: Standalone EXE erstellen (Windows)

1. **EXE selbst erstellen**: Führe `build_exe.bat` aus, um die Standalone-EXE zu erstellen
   ```bash
   build_exe.bat
   ```
2. Die EXE wird im `dist/` Ordner erstellt
3. Führe die `Shila-Vision.exe` aus - keine Python-Installation nötig!
4. **Modell**: Wird beim ersten Start automatisch heruntergeladen (siehe [README-Modelle.md](README-Modelle.md))

**Hinweis**: Die EXE ist ~927MB groß, da sie alle Dependencies enthält (Python Runtime, Qt, ONNX, etc.).

### Option 2: Von Quellcode

#### Windows

##### 1. Virtual Environment erstellen (Empfohlen)

```bash
python -m venv venv
venv\Scripts\activate
```

##### 2. Dependencies installieren

```bash
pip install -r requirements.txt
```

##### 3. Modell installieren (Optional)

**Einfachste Methode**: Verwende den Download-Manager:
```bash
python download_model.py
```

Das Modell wird auch automatisch beim ersten Start heruntergeladen. Für weitere Optionen siehe [README-Modelle.md](README-Modelle.md).

##### 4. Anwendung starten

```bash
python main.py
```

#### Linux / WSL (Windows Subsystem for Linux)

##### 1. System-Dependencies installieren

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Fedora/RHEL:**
```bash
sudo dnf install python3 python3-pip
```

##### 2. Virtual Environment erstellen

```bash
python3 -m venv venv
source venv/bin/activate
```

##### 3. Dependencies installieren

```bash
pip install -r requirements.txt
```

**Wichtig für Linux/WSL**: Falls GUI-Probleme auftreten, installiere zusätzlich:
```bash
# Für WSL: X11-Forwarding einrichten
# Für Linux: Qt-Dependencies
sudo apt install libxcb-xinerama0 libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-sync1 libxcb-xfixes0 libxcb-xkb1 libxkbcommon-x11-0
```

##### 4. Modell installieren (Optional)

**Einfachste Methode**: Verwende den Download-Manager:
```bash
python3 download_model.py
```

##### 5. Anwendung starten

**Für Linux (mit Display):**
```bash
python3 main.py
```

**Für WSL (mit X11-Forwarding):**
```bash
# Stelle sicher, dass X11-Forwarding aktiviert ist
export DISPLAY=:0
python3 main.py
```

**Hinweis für WSL**: Du benötigst einen X-Server auf Windows (z.B. [VcXsrv](https://sourceforge.net/projects/vcxsrv/) oder [X410](https://x410.dev/)).

## 🎯 Verwendung

1. **Bilder hinzufügen**: 
   - Ziehen Sie Bilder per Drag & Drop in den oberen Bereich
   - Oder klicken Sie auf den Bereich, um Dateien auszuwählen

2. **Tags anzeigen**: 
   - Die Tags werden automatisch generiert und angezeigt
   - Sie sehen sowohl einzelne Tags mit Konfidenz-Werten als auch den formatierten Prompt
   - Rating-Tags werden separat oben angezeigt

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
- **CPU**: Optimiert für CPU-Ausführung (keine dedizierte GPU nötig)

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

- **Modell-Installation**: Das Modell ist nicht im Repository enthalten (zu groß). Siehe **[README-Modelle.md](README-Modelle.md)** für Installations-Anleitung
- **Automatischer Download**: Die Anwendung lädt das Modell automatisch beim ersten Start (benötigt Internet)
- **Lokales Modell**: Optional kannst du das Modell manuell in den `Modeltagger/` Ordner kopieren (siehe README-Modelle.md)
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

**Unlicense** - Public Domain

Dieses Projekt ist freie Software und wurde in die Public Domain veröffentlicht. 
Jeder kann den Code kopieren, modifizieren, veröffentlichen, verwenden, kompilieren, verkaufen oder verteilen - für jeden Zweck, kommerziell oder nicht-kommerziell, auf jede erdenkliche Weise.

Siehe `LICENSE` Datei für Details.

(Ähnlich dem Original WD14 Tagger)

## 🙏 Credits

- **Waifu Diffusion 1.4 Tagger**: Basierend auf dem Modell von SmilingWolf
- **Bildverarbeitung**: Inspiriert von `stable-diffusion-webui-wd14-tagger`
- **wdtagger**: Python-Bibliothek für WD14 Tagger Modelle

---

**Shila-Vision** - Elegantes Bild-Tagging für alle! ✨

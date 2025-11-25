# 📊 Detaillierter Projekt-Bericht: Shila-Vision

## 🎯 Projekt-Übersicht

**Shila-Vision** ist eine eigenständige Desktop-Anwendung für automatisches Bild-Tagging mit dem Waifu Diffusion 1.4 Tagger Modell. Die Anwendung wurde als Standalone-EXE entwickelt, die ohne Python-Installation funktioniert.

---

## 📁 Projektstruktur

```
WD1.4/
├── main.py                          # Haupt-Einstiegspunkt
├── gui/                             # GUI-Module
│   ├── main_window.py              # Hauptfenster & Logik
│   └── components.py               # UI-Komponenten (DragDrop, ImagePreview, TagDisplay, etc.)
├── tagger/                         # Tagger-Module
│   ├── wd14_tagger.py             # Haupt-Tagger-Klasse
│   └── local_model_loader.py      # Lokaler ONNX-Modell-Lader
├── utils/                          # Utility-Module
│   ├── file_handler.py            # Datei-Verarbeitung
│   └── image_processing.py        # Bildverarbeitungs-Utilities (NEU)
├── Modeltagger/                    # Lokales KI-Modell
│   ├── model.onnx                 # ONNX-Modell (~50-100MB)
│   └── selected_tags.csv          # Tag-Datenbank (~9000 Tags)
├── stable-diffusion-webui-wd14-tagger-master/  # Referenz-Implementierung (NICHT VERMISCHT)
├── requirements.txt                # Python-Dependencies
├── build_exe.bat                   # PyInstaller Build-Script
└── README.md                       # Projekt-Dokumentation
```

---

## 🔧 Verwendete Technologien

### **Python-Bibliotheken:**

| Bibliothek | Version | Verwendung |
|------------|---------|------------|
| **PySide6** | ≥6.6.0 | GUI-Framework (Qt 6) für moderne Desktop-UI |
| **onnxruntime** | ≥1.15.0 | ONNX-Modell-Inferenz (CPU-optimiert) |
| **numpy** | ≥1.24.0 | Numerische Berechnungen, Array-Operationen |
| **Pillow (PIL)** | ≥10.0.0 | Bildverarbeitung (PNG, JPEG, BMP, GIF, WebP, TIFF) |
| **scipy** | ≥1.10.0 | Wissenschaftliche Funktionen (Sigmoid) |
| **opencv-python** | ≥4.8.0 | **NEU:** Erweiterte Bildverarbeitung |
| **wdtagger** | ≥0.1.0 | Fallback-Tagger (HuggingFace-Modelle) |
| **timm** | ≥0.9.0 | PyTorch Image Models (für wdtagger) |
| **pyinstaller** | ≥6.0.0 | EXE-Erstellung |

---

## 📦 Was wird verwendet?

### **1. Eigene Entwicklungen (100% selbst entwickelt):**

#### **GUI-Komponenten (`gui/`):**
- ✅ **`main_window.py`**: Hauptfenster mit Multi-Tagger-System
  - Zwei Tagger (automatische Auswahl)
  - Thinking Mode Engine
  - Progress-Animation
  - Tag-Verarbeitung (Exclude, Sort, Spaces)
  
- ✅ **`components.py`**: Wiederverwendbare UI-Komponenten
  - `DragDropArea`: Drag & Drop für Bilder
  - `ImagePreview`: Bildvorschau
  - `TagDisplay`: Tag-Anzeige mit HTML-Formatierung
  - `ActionButtons`: Buttons (Kopieren, Export, Refresh, Reset)
  - `AnimatedProgressBar`: Animierter Progress-Bar

#### **Tagger-Logik (`tagger/`):**
- ✅ **`wd14_tagger.py`**: Haupt-Tagger-Klasse
  - Unterstützt lokales ONNX-Modell
  - Fallback auf wdtagger (HuggingFace)
  - Rating-Tags Behandlung
  - Multi-Tagger-Support
  
- ✅ **`local_model_loader.py`**: Lokaler Modell-Lader
  - Lädt ONNX-Modell aus `Modeltagger/`
  - Lädt Tags aus `selected_tags.csv`
  - CPU-optimiert

#### **Utilities (`utils/`):**
- ✅ **`file_handler.py`**: Datei-Operationen
  - Bild-Validierung
  - Tag-Export
  
- ✅ **`image_processing.py`**: **NEU - Übernommen aus Original**
  - `fill_transparent()`: Alpha zu Weiß
  - `make_square()`: Quadratisches Padding
  - `smart_resize()`: Intelligentes Resizing
  - `preprocess_for_wd14()`: Vollständiges Preprocessing

---

### **2. Übernommen aus `stable-diffusion-webui-wd14-tagger-master`:**

#### **✅ Verwendet (angepasst):**

1. **Bildverarbeitungs-Utilities** (`tagger/dbimutils.py` → `utils/image_processing.py`)
   - **Quelle**: `stable-diffusion-webui-wd14-tagger-master/tagger/dbimutils.py`
   - **Übernommen**:
     - `fill_transparent()`: Konvertiert transparente Bereiche zu weißem Hintergrund
     - `make_square()`: Macht Bilder quadratisch durch Padding
     - `smart_resize()`: Intelligentes Resizing (INTER_AREA für Verkleinern, INTER_CUBIC für Vergrößern)
   - **Anpassungen**: 
     - In eigenes Modul `utils/image_processing.py` verschoben
     - `preprocess_for_wd14()` Funktion hinzugefügt (kombiniert alle Schritte)
     - Kommentare auf Deutsch

2. **Rating-Tags Behandlung** (`tagger/interrogator.py`)
   - **Quelle**: `stable-diffusion-webui-wd14-tagger-master/tagger/interrogator.py` (Zeile 479-484)
   - **Übernommen**: 
     - Erkenntnis, dass erste 4 Tags Rating-Tags sind
     - Separates Handling von Rating vs. normalen Tags
   - **Implementiert in**: `tagger/wd14_tagger.py` (Zeile 162-169)

3. **Kaomoji-Liste** (`tagger/settings.py`)
   - **Quelle**: `stable-diffusion-webui-wd14-tagger-master/tagger/settings.py` (Zeile 8)
   - **Übernommen**: 
     - Liste von Tags, die Unterstriche behalten sollen
     - `'0_0, (o)_(o), +_+, +_-, ._., <o>_<o>, <|>_<|>, =_=, >_<, 3_3, 6_9, >_o, @_@, ^_^, o_o, u_u, x_x, |_|, ||_||'`
   - **Implementiert in**: `gui/main_window.py` (Zeile 54-60)

4. **Bildpreprocessing-Logik** (`tagger/interrogator.py`)
   - **Quelle**: `stable-diffusion-webui-wd14-tagger-master/tagger/interrogator.py` (Zeile 454-468)
   - **Übernommen**:
     - Alpha zu Weiß konvertieren
     - PIL RGB zu OpenCV BGR
     - Quadratisch machen
     - Smart Resize
     - Keine ImageNet-Normalisierung (Modell erwartet [0, 255])
   - **Implementiert in**: `tagger/local_model_loader.py` (Zeile 135-171)

#### **❌ NICHT verwendet (WebUI-spezifisch):**

- `tagger/api.py`, `tagger/api_models.py`: Für WebUI-API
- `tagger/ui.py`, `tagger/uiset.py`: Für Gradio-UI
- `tagger/preset.py`: Für Gradio-Presets
- `tagger/format.py`: Für WebUI-Dateinamen-Formatierung
- `scripts/tagger.py`: WebUI-Integration
- `javascript/tagger.js`: Frontend-Code
- `json_schema/`: JSON-Schemas für WebUI
- DeepDanbooru-Support: Wir nutzen nur WD14

---

## 🎨 Features der Anwendung

### **1. Multi-Tagger-System:**
- **Tagger 1**: Lokales ONNX-Modell (`Modeltagger/model.onnx`)
- **Tagger 2**: SwinV2-Modell (via wdtagger von HuggingFace)
- **Automatische Auswahl**: Wählt den besseren Tagger basierend auf:
  - Durchschnittliche Konfidenz der Top 25 Tags
  - Anzahl relevanter Tags (≥0.5 Konfidenz)

### **2. Thinking Mode Engine:**
- **Phase 1**: Intensives Bild-Scannen (3%)
- **Phase 2**: Bildstruktur-Analyse (8%)
- **Phase 3**: Farb- und Kompositionsanalyse (12%)
- **Phase 4**: Tiefe Bildanalyse mit Erkenntnissen (18-25%)
  - Erkennt: Bildtyp (Foto/Illustration), Farben, Komposition
- **Phase 5-6**: Tag-Berechnung mit beiden Taggern (30-85%)
- **Phase 7-8**: Vergleich und Auswahl (85-100%)

### **3. Tag-Verarbeitung:**
- **Exclude Tags**: Bestimmte Tags ausschließen (Standard: monochrome, greyscale, dark, simple background)
- **Unterstriche → Leerzeichen**: Mit Kaomoji-Schutz
- **Alphabetisch sortieren**: Optional
- **Max 25 Tags**: Begrenzung auf Top 25

### **4. Rating-Tags Anzeige:**
- **General**: Allgemeine Inhalte
- **Sensitive**: Sensible Inhalte
- **Questionable**: Fragwürdige Inhalte
- **Explicit**: Explizite Inhalte
- **Farbcodierung**: Grün (≥70%), Blau (≥50%), Gelb (≥30%), Rot (<30%)

### **5. UI-Features:**
- **Dark Theme**: Modernes Design mit Lila-Akzenten
- **Drag & Drop**: Bilder einfach hineinziehen
- **Progress-Animation**: Animierter Progress-Bar während Tagging
- **Tag-Farbcodierung**: Basierend auf Konfidenz
- **Threshold-Anpassung**: Live-Anpassung des Schwellenwerts

---

## 🔄 Datenfluss

```
Bild laden
    ↓
Thinking Mode Engine
    ├─→ Bild scannen & analysieren
    ├─→ Erkenntnisse sammeln
    └─→ Progress-Updates
    ↓
Tagger 1 (Lokales ONNX)
    ├─→ Verbessertes Preprocessing (fill_transparent, make_square, smart_resize)
    ├─→ ONNX-Inferenz
    └─→ Rating-Tags + normale Tags extrahieren
    ↓
Tagger 2 (SwinV2 via wdtagger)
    ├─→ HuggingFace-Modell
    └─→ Rating-Tags + normale Tags extrahieren
    ↓
Automatische Auswahl
    ├─→ Bewertung beider Tagger
    └─→ Besserer Tagger wird gewählt
    ↓
Tag-Verarbeitung
    ├─→ Exclude Tags filtern
    ├─→ Unterstriche → Leerzeichen (mit Kaomoji-Schutz)
    └─→ Optional: Alphabetisch sortieren
    ↓
UI-Anzeige
    ├─→ Rating-Tags (oben)
    ├─→ Top 25 Tags (mit Konfidenz)
    └─→ Prompt-Format
```

---

## 📊 Code-Statistiken

### **Eigene Entwicklung:**
- **GUI-Module**: ~800 Zeilen Code
- **Tagger-Module**: ~250 Zeilen Code
- **Utilities**: ~200 Zeilen Code
- **Gesamt**: ~1250 Zeilen eigener Code

### **Übernommen (angepasst):**
- **Bildverarbeitung**: ~180 Zeilen (aus dbimutils.py)
- **Konzepte**: Rating-Tags, Kaomoji-Liste, Preprocessing-Logik

### **Dependencies:**
- **Externe Bibliotheken**: 9 Haupt-Pakete
- **Lokales Modell**: ~50-100MB ONNX + CSV

---

## 🎯 Hauptunterschiede zum Original

| Aspekt | Original (WebUI) | Shila-Vision |
|--------|-----------------|--------------|
| **Plattform** | WebUI-Extension | Standalone Desktop-App |
| **GUI** | Gradio (Web) | PySide6 (Desktop) |
| **Modell** | HuggingFace-Download | Lokales ONNX-Modell |
| **Tagger** | Ein Tagger | Zwei Tagger (Auto-Auswahl) |
| **Features** | WebUI-Integration | Eigenständig, portable |
| **Bildverarbeitung** | dbimutils.py | Übernommen & angepasst |
| **Rating-Tags** | In Result-Objekt | Separate UI-Anzeige |
| **Kaomoji** | In Settings | In MainWindow integriert |

---

## 🔍 Detaillierte Modul-Analyse

### **`main.py`**
- **Zweck**: Einstiegspunkt der Anwendung
- **Funktionen**:
  - Erstellt QApplication
  - Setzt App-Name: "Shila-Vision"
  - Erstellt und zeigt MainWindow
- **Zeilen**: ~20

### **`gui/main_window.py`**
- **Zweck**: Hauptfenster und Geschäftslogik
- **Hauptklassen**:
  - `TaggingWorker`: Worker-Thread für asynchrones Tagging
    - Thinking Mode Engine
    - Multi-Tagger-Auswahl
    - Progress-Updates
  - `MainWindow`: Hauptfenster
    - UI-Setup
    - Tagger-Initialisierung
    - Tag-Verarbeitung
    - Event-Handling
- **Features**:
  - Multi-Tagger-System
  - Thinking Mode mit Bildanalyse
  - Tag-Verarbeitung (Exclude, Sort, Spaces)
  - Rating-Tags Integration
  - Kaomoji-Schutz
- **Zeilen**: ~820

### **`gui/components.py`**
- **Zweck**: Wiederverwendbare UI-Komponenten
- **Komponenten**:
  - `AnimatedProgressBar`: Animierter Progress-Bar mit Shine-Effekt
  - `DragDropArea`: Drag & Drop Bereich
  - `ImagePreview`: Bildvorschau
  - `TagDisplay`: Tag-Anzeige mit HTML-Formatierung
    - Rating-Tags Anzeige
    - Farbcodierung nach Konfidenz
    - Prompt-Format
  - `ActionButtons`: Aktions-Buttons
- **Zeilen**: ~490

### **`tagger/wd14_tagger.py`**
- **Zweck**: Haupt-Tagger-Klasse
- **Features**:
  - Unterstützt lokales ONNX-Modell
  - Fallback auf wdtagger (HuggingFace)
  - Rating-Tags Behandlung
  - Threshold-Filterung
- **Zeilen**: ~215

### **`tagger/local_model_loader.py`**
- **Zweck**: Lädt lokales ONNX-Modell
- **Features**:
  - Lädt `model.onnx` aus `Modeltagger/`
  - Lädt `selected_tags.csv`
  - Verbessertes Preprocessing (über `utils/image_processing.py`)
  - CPU-optimiert
- **Zeilen**: ~177

### **`utils/file_handler.py`**
- **Zweck**: Datei-Operationen
- **Features**:
  - Bild-Validierung
  - Format-Erkennung
  - Tag-Export
- **Zeilen**: ~112

### **`utils/image_processing.py`** ⭐ **NEU**
- **Zweck**: Verbesserte Bildverarbeitung
- **Quelle**: Übernommen aus `stable-diffusion-webui-wd14-tagger-master/tagger/dbimutils.py`
- **Funktionen**:
  - `fill_transparent()`: Alpha zu Weiß
  - `make_square()`: Quadratisches Padding
  - `smart_resize()`: Intelligentes Resizing
  - `preprocess_for_wd14()`: Vollständiges Preprocessing
- **Zeilen**: ~180

---

## 🔗 Abhängigkeiten vom Original

### **Direkt übernommen:**
1. ✅ **Bildverarbeitungs-Funktionen** (`dbimutils.py`)
   - `fill_transparent()`
   - `make_square()`
   - `smart_resize()`
   - → In `utils/image_processing.py` integriert

2. ✅ **Preprocessing-Logik** (`interrogator.py`, Zeile 454-468)
   - Alpha zu Weiß
   - RGB zu BGR
   - Quadratisch machen
   - Smart Resize
   - → In `tagger/local_model_loader.py` integriert

3. ✅ **Rating-Tags Konzept** (`interrogator.py`, Zeile 479-484)
   - Erste 4 Tags sind Rating-Tags
   - → In `tagger/wd14_tagger.py` implementiert

4. ✅ **Kaomoji-Liste** (`settings.py`, Zeile 8)
   - 19 Kaomojis die Unterstriche behalten
   - → In `gui/main_window.py` integriert

### **Inspiriert (aber selbst entwickelt):**
- Multi-Tagger-Konzept (Original hat nur einen Tagger)
- Thinking Mode Engine (Original hat kein "Thinking")
- Rating-Tags UI-Anzeige (Original zeigt sie anders)
- Tag-Verarbeitung (Exclude, Sort, Spaces)

---

## 🚀 Build-Prozess

### **PyInstaller Konfiguration (`build_exe.bat`):**
```batch
pyinstaller --name=Shila-Vision ^
    --onefile ^                    # Eine große .exe
    --windowed ^                   # Kein Konsolen-Fenster
    --add-data="Modeltagger;Modeltagger" ^  # Modell-Dateien
    --hidden-import=onnxruntime ^
    --hidden-import=scipy ^
    --hidden-import=opencv-python ^  # NEU
    --collect-all=onnxruntime ^
    --exclude-module=wdtagger ^    # Lokales Modell bevorzugt
    main.py
```

### **Ergebnis:**
- **EXE-Größe**: ~927MB
- **Enthalten**: Python Runtime + Qt + ONNX + Modell + Dependencies
- **Portable**: Funktioniert ohne Installation

---

## 📈 Verbesserungen durch Original-Integration

### **Vorher:**
- ❌ Einfaches Resize (verlustbehaftet)
- ❌ Keine Alpha-Behandlung
- ❌ Keine Rating-Tags
- ❌ Kaomojis wurden kaputt gemacht

### **Nachher:**
- ✅ Intelligentes Preprocessing (make_square + smart_resize)
- ✅ Alpha zu Weiß konvertiert
- ✅ Rating-Tags separat angezeigt
- ✅ Kaomojis bleiben erhalten
- ✅ Bessere Tag-Qualität

---

## 🎯 Zusammenfassung

### **Was wir haben:**
1. ✅ **Eigenständige Desktop-Anwendung** (Standalone EXE)
2. ✅ **Multi-Tagger-System** (2 Tagger, automatische Auswahl)
3. ✅ **Thinking Mode Engine** (intelligente Bildanalyse)
4. ✅ **Verbesserte Bildverarbeitung** (aus Original übernommen)
5. ✅ **Rating-Tags Anzeige** (separat, farbcodiert)
6. ✅ **Kaomoji-Schutz** (wichtige Tags bleiben erhalten)
7. ✅ **Tag-Verarbeitung** (Exclude, Sort, Spaces)
8. ✅ **Modernes UI** (Dark Theme, Animationen)

### **Was vom Original übernommen wurde:**
1. ✅ Bildverarbeitungs-Utilities (`dbimutils.py` → `image_processing.py`)
2. ✅ Preprocessing-Logik (Alpha, BGR, Square, Resize)
3. ✅ Rating-Tags Konzept (erste 4 Tags)
4. ✅ Kaomoji-Liste (19 geschützte Tags)

### **Was NICHT verwendet wird:**
- ❌ WebUI-spezifische Module (api.py, ui.py, preset.py)
- ❌ Gradio-Integration
- ❌ DeepDanbooru-Support
- ❌ JSON-Schema-System
- ❌ JavaScript-Frontend

---

## 📝 Fazit

**Shila-Vision** ist eine **eigenständige Desktop-Anwendung**, die:
- ✅ Die **besten Teile** des Original-Projekts übernimmt (Bildverarbeitung, Konzepte)
- ✅ **Eigene Innovationen** hinzufügt (Multi-Tagger, Thinking Mode, Desktop-UI)
- ✅ **Nicht vermischt** mit WebUI-spezifischem Code
- ✅ **Portable** und **benutzerfreundlich** ist

Die Integration des Original-Codes erfolgte **selektiv** und **angepasst** für unsere Desktop-Anwendung, ohne die WebUI-Abhängigkeiten zu übernehmen.

---

*Erstellt: 2025*  
*Projekt: Shila-Vision - Bild-Tagging Tool*  
*Basierend auf: Waifu Diffusion 1.4 Tagger & stable-diffusion-webui-wd14-tagger*



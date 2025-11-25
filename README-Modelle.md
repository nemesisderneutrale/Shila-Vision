# 📦 Modell-Installation für Shila-Vision

Shila-Vision benötigt das Waifu Diffusion 1.4 Tagger Modell für die Bild-Tagging-Funktion. Dieses Dokument erklärt, wie du das Modell installierst.

## 🎯 Option 1: Automatischer Download-Manager (Empfohlen)

Verwende den integrierten Download-Manager für einfache Installation:

```bash
python download_model.py
```

Der Download-Manager:
- ✅ Erstellt automatisch den `Modeltagger/` Ordner
- ✅ Lädt `model.onnx` herunter (~50-100MB)
- ✅ Lädt `selected_tags.csv` herunter (~1-2MB)
- ✅ Zeigt Progress-Anzeige während des Downloads
- ✅ Prüft ob Modell bereits vorhanden ist

**Vorteil**: Einfachste Installation - nur ein Befehl!

---

## 🎯 Option 2: Automatischer Download beim Start

Die Anwendung lädt das Modell **automatisch** beim ersten Start herunter, falls kein lokales Modell gefunden wird.

- **Tagger 1**: Verwendet `wdtagger` und lädt das Modell von HuggingFace
- **Tagger 2**: Lädt SwinV2-Modell automatisch von HuggingFace

**Vorteil**: Keine manuelle Installation nötig!

---

## 📥 Option 3: Manueller Download (Offline-Nutzung)

Falls du das Modell lokal speichern möchtest (für Offline-Nutzung oder schnellere Starts):

### Schritt 1: Modell herunterladen

Das Modell besteht aus zwei Dateien:

1. **`model.onnx`** (~50-100MB)
   - Das eigentliche KI-Modell
   - Download von: [HuggingFace - SmilingWolf/wd-v1-4-vit-tagger-v2](https://huggingface.co/SmilingWolf/wd-v1-4-vit-tagger-v2)

2. **`selected_tags.csv`** (~1-2MB)
   - Die Tag-Datenbank mit ~9000 Tags
   - Download von: [HuggingFace - SmilingWolf/wd-v1-4-vit-tagger-v2](https://huggingface.co/SmilingWolf/wd-v1-4-vit-tagger-v2)

### Schritt 2: Ordnerstruktur erstellen

Erstelle einen Ordner `Modeltagger/` im Hauptverzeichnis der Anwendung:

```
Shila-Vision/
├── main.py
├── gui/
├── tagger/
├── utils/
└── Modeltagger/          ← Erstelle diesen Ordner
    ├── model.onnx        ← Modell-Datei hier rein
    └── selected_tags.csv ← Tag-Datei hier rein
```

### Schritt 3: Dateien platzieren

1. Lade `model.onnx` herunter
2. Lade `selected_tags.csv` herunter
3. Platziere beide Dateien im `Modeltagger/` Ordner

### Schritt 4: Anwendung starten

Die Anwendung erkennt automatisch das lokale Modell und verwendet es statt des Online-Downloads.

---

## 🔗 Download-Links

### HuggingFace (Offiziell)

**Modell-Repository**: [SmilingWolf/wd-v1-4-vit-tagger-v2](https://huggingface.co/SmilingWolf/wd-v1-4-vit-tagger-v2)

**Direkte Downloads**:
- `model.onnx`: [Download model.onnx](https://huggingface.co/SmilingWolf/wd-v1-4-vit-tagger-v2/resolve/main/model.onnx)
- `selected_tags.csv`: [Download selected_tags.csv](https://huggingface.co/SmilingWolf/wd-v1-4-vit-tagger-v2/resolve/main/selected_tags.csv)

### Alternative Quellen

Falls HuggingFace nicht verfügbar ist, kannst du das Modell auch von anderen Quellen herunterladen:
- [Waifu Diffusion Tagger GitHub](https://github.com/picobyte/stable-diffusion-webui-wd14-tagger)
- [Danbooru Tagger Models](https://github.com/SmilingWolf/wd-tagger)

---

## ✅ Verifikation

Nach der Installation kannst du prüfen, ob das Modell korrekt geladen wird:

1. Starte die Anwendung
2. In der Statusleiste sollte stehen: **"Modell erfolgreich geladen! (9083 Tags)"**
3. Falls ein Fehler erscheint, überprüfe:
   - Sind beide Dateien im `Modeltagger/` Ordner?
   - Sind die Dateinamen korrekt? (`model.onnx` und `selected_tags.csv`)
   - Ist genug Speicherplatz verfügbar?

---

## 🚨 Fehlerbehebung

### Problem: "Modell nicht gefunden"

**Lösung**: 
- Überprüfe, ob der `Modeltagger/` Ordner existiert
- Überprüfe, ob beide Dateien vorhanden sind
- Überprüfe die Dateinamen (Groß-/Kleinschreibung beachten!)

### Problem: "Modell zu groß" oder Download-Fehler

**Lösung**:
- Die Anwendung verwendet automatisch `wdtagger` als Fallback
- Das Modell wird dann von HuggingFace geladen (benötigt Internet)

### Problem: Langsame Performance

**Lösung**:
- Stelle sicher, dass `model.onnx` im `Modeltagger/` Ordner ist
- Lokales Modell ist schneller als Online-Download
- Bei CPU-Nutzung kann das Tagging etwas länger dauern (normal)

---

## 📊 Modell-Details

- **Modell-Typ**: ONNX (Optimized Neural Network Exchange)
- **Modell-Größe**: ~50-100MB
- **Tags**: ~9000 verschiedene Tags
- **Format**: Booru-Style Tags (wie Danbooru)
- **Architektur**: Vision Transformer (ViT)

---

## 💡 Tipps

- **Erste Nutzung**: Lass die Anwendung das Modell automatisch herunterladen
- **Offline-Nutzung**: Lade das Modell manuell herunter für Offline-Betrieb
- **Backup**: Speichere eine Kopie des Modells für spätere Nutzung
- **Updates**: Das Modell wird nicht automatisch aktualisiert - bei Problemen neu herunterladen

---

**Hinweis**: Das Modell ist zu groß für GitHub, daher ist es nicht im Repository enthalten. Folge dieser Anleitung, um es zu installieren.


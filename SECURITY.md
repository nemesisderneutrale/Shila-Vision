# Security Policy

## 🔒 Unterstützte Versionen

Die folgenden Versionen von Shila-Vision werden derzeit mit Sicherheitsupdates unterstützt:

| Version | Unterstützt          |
| ------- | -------------------- |
| 1.0.x   | :white_check_mark:   |
| < 1.0   | :x:                  |

**Hinweis**: Da Shila-Vision ein relativ neues Projekt ist, wird aktuell nur die neueste Version (1.0.x) mit Sicherheitsupdates unterstützt.

## 🐛 Sicherheitslücken melden

Wenn du eine Sicherheitslücke in Shila-Vision gefunden hast, bitten wir dich, diese **verantwortungsvoll** zu melden.

### Wie melde ich eine Sicherheitslücke?

1. **Erstelle ein Issue** auf GitHub:
   - Gehe zu: https://github.com/nemesisderneutrale/Shila-Vision/issues
   - Klicke auf "New issue"
   - Verwende das Label "security" (falls verfügbar)
   - Beschreibe die Sicherheitslücke so detailliert wie möglich

2. **Was sollte in der Meldung enthalten sein?**
   - Beschreibung der Sicherheitslücke
   - Schritte zur Reproduktion (wenn möglich)
   - Erwartetes vs. tatsächliches Verhalten
   - Betroffene Version(en)
   - Mögliche Auswirkungen

### Was passiert nach der Meldung?

- **Bestätigung**: Du erhältst innerhalb von 48 Stunden eine Bestätigung, dass deine Meldung eingegangen ist
- **Bewertung**: Die Sicherheitslücke wird bewertet (normalerweise innerhalb von 7 Tagen)
- **Updates**: Du wirst über den Status informiert (angenommen/abgelehnt/in Bearbeitung)
- **Fix**: Wenn die Sicherheitslücke bestätigt wird, wird ein Fix entwickelt und veröffentlicht

### Verantwortungsvolle Offenlegung

Wir bitten dich, die Sicherheitslücke **nicht öffentlich zu diskutieren**, bis ein Fix verfügbar ist. Dies gibt uns Zeit, das Problem zu beheben und andere Nutzer zu schützen.

## ✅ Was wird als Sicherheitslücke betrachtet?

- **Kritisch**: 
  - Remote Code Execution (RCE)
  - Lokale Code Execution
  - Schwere Datenlecks
  - Authentifizierungs-/Autorisierungsprobleme

- **Hoch**:
  - Cross-Site Scripting (XSS) - falls die Anwendung Web-Features hat
  - Lokale Dateisystem-Zugriffe ohne Berechtigung
  - Denial of Service (DoS)

- **Niedrig**:
  - Informationsleck (z.B. Versionsinformationen)
  - Best Practices-Verletzungen ohne direkte Sicherheitsauswirkung

## 📝 Was ist KEINE Sicherheitslücke?

- Feature-Requests
- Bugs ohne Sicherheitsauswirkung
- Fragen zur Verwendung
- Verbesserungsvorschläge

Für diese Themen bitte normale Issues erstellen.

## 🙏 Danksagung

Wir danken allen, die Sicherheitslücken verantwortungsvoll melden. Dein Beitrag hilft, Shila-Vision sicherer zu machen!

---

**Letzte Aktualisierung**: 2025-01-26


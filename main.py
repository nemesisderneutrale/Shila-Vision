"""Haupt-Einstiegspunkt für die Shila-Vision Anwendung."""

import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Startet die Anwendung."""
    app = QApplication(sys.argv)
    app.setApplicationName("Shila-Vision")
    app.setOrganizationName("Shila-Vision")
    
    # Erstelle Hauptfenster
    window = MainWindow()
    window.show()
    
    # Starte Event-Loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


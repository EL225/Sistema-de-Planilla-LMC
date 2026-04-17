"""
Sistema de Planilla
───────────────────
Requiere: Python 3.10+  |  pip install openpyxl

Ejecutar:
    python main.py
"""

from planilla.ui.app import AplicacionPlanilla


if __name__ == "__main__":
    app = AplicacionPlanilla()
    app.mainloop()

from .constantes import COLORES, OPCIONES

try:
    from .widgets import campo_con_label, combo_con_label, boton_primario
except ImportError:
    pass  # tkinter no disponible en entorno no-GUI

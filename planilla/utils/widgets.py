import tkinter as tk
from tkinter import ttk

from planilla.utils.constantes import COLORES


def campo_con_label(parent, texto: str, row: int, col: int = 0,
                    width: int = 22, colspan: int = 1) -> tk.Entry:
    """Crea un Label + Entry apilados y devuelve el Entry."""
    tk.Label(
        parent, text=texto,
        bg=COLORES["fondo_frame"], fg=COLORES["label"],
        font=("Arial", 9, "bold"), anchor="w",
    ).grid(row=row, column=col, padx=(10, 4), pady=(6, 0), sticky="w")

    entry = tk.Entry(
        parent, width=width, font=("Arial", 10),
        relief="flat", bd=1,
        highlightthickness=1,
        highlightbackground=COLORES["borde"],
        highlightcolor=COLORES["secundario"],
    )
    entry.grid(row=row + 1, column=col, columnspan=colspan,
               padx=(10, 4), pady=(0, 4), sticky="ew")
    return entry


def combo_con_label(parent, texto: str, opciones: list, row: int,
                    col: int = 0, width: int = 20) -> tuple[tk.StringVar, ttk.Combobox]:
    """Crea un Label + Combobox apilados y devuelve (StringVar, Combobox)."""
    tk.Label(
        parent, text=texto,
        bg=COLORES["fondo_frame"], fg=COLORES["label"],
        font=("Arial", 9, "bold"), anchor="w",
    ).grid(row=row, column=col, padx=(10, 4), pady=(6, 0), sticky="w")

    var = tk.StringVar()
    combo = ttk.Combobox(parent, textvariable=var, values=opciones,
                         width=width, state="readonly", font=("Arial", 10))
    combo.grid(row=row + 1, column=col, padx=(10, 4), pady=(0, 4), sticky="ew")
    return var, combo


def boton_primario(parent, texto: str, comando,
                   color: str = None) -> tk.Button:
    """Botón estilizado con color de fondo sólido."""
    color = color or COLORES["secundario"]
    return tk.Button(
        parent, text=texto, command=comando,
        bg=color, fg="white", font=("Arial", 10, "bold"),
        relief="flat", padx=18, pady=7, cursor="hand2",
        activebackground=COLORES["primario"],
        activeforeground="white",
    )

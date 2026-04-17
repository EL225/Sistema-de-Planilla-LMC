import tkinter as tk
from tkinter import ttk

from planilla.models import Acreedor
from planilla.utils import COLORES, OPCIONES, combo_con_label, boton_primario


class VentanaBusquedaAvanzadaAcreedor(tk.Toplevel):
    """Diálogo de búsqueda avanzada con filtros combinados.

    Al cerrar, ``self.resultado`` contiene la lista filtrada
    (o None si el usuario canceló sin aplicar).
    """

    def __init__(self, parent, acreedores: list[Acreedor]):
        super().__init__(parent)
        self._acreedores = acreedores
        self.resultado: list[Acreedor] | None = None
        self.title("Búsqueda Avanzada — Acreedores")
        self.resizable(False, False)
        self.configure(bg=COLORES["fondo"])
        self._centrar(520, 460)
        self._construir()

    # ── Posicionamiento ───────────────────────────────────────────────────

    def _centrar(self, w: int, h: int) -> None:
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── Construcción UI ───────────────────────────────────────────────────

    def _construir(self) -> None:
        header = tk.Frame(self, bg=COLORES["secundario"], height=52)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="🔎  BÚSQUEDA AVANZADA",
            bg=COLORES["secundario"], fg="white",
            font=("Arial", 12, "bold"),
        ).pack(expand=True)

        frame = tk.Frame(self, bg=COLORES["fondo_frame"], padx=20, pady=16)
        frame.pack(fill="both", expand=True, padx=16, pady=12)
        frame.columnconfigure((0, 1), weight=1)

        def lbl_entry(texto, row, col=0):
            tk.Label(frame, text=texto, bg=COLORES["fondo_frame"],
                     fg=COLORES["label"], font=("Arial", 9, "bold"),
                     anchor="w").grid(row=row, column=col,
                                      padx=(0, 8), pady=(8, 0), sticky="w")
            e = tk.Entry(frame, font=("Arial", 10), relief="flat", bd=1,
                         highlightthickness=1,
                         highlightbackground=COLORES["borde"],
                         highlightcolor=COLORES["secundario"])
            e.grid(row=row+1, column=col, padx=(0, 8), pady=(0, 4),
                   sticky="ew")
            return e

        self.e_nombre   = lbl_entry("Nombre",     0, 0)
        self.e_numero   = lbl_entry("Acreedor",   0, 1)
        self.e_concepto = lbl_entry("Concepto",   2, 0)
        self.e_ruc      = lbl_entry("RUC",        2, 1)

        self.v_forma_pago,  _ = combo_con_label(
            frame, "Forma de Pago", [""] + OPCIONES["forma_pago"], 4, 0)
        self.v_banco,       _ = combo_con_label(
            frame, "Banco Pagador", [""] + OPCIONES["banco_pagador"], 4, 1, width=24)
        self.v_status,      _ = combo_con_label(
            frame, "Status", ["", "Activo", "Inactivo"], 6, 0)
        self.v_ahorro,      _ = combo_con_label(
            frame, "Ahorro", ["", "Sí", "No"], 6, 1)

        # Rango de prioridad
        tk.Label(frame, text="Prioridad mínima", bg=COLORES["fondo_frame"],
                 fg=COLORES["label"], font=("Arial", 9, "bold"),
                 anchor="w").grid(row=8, column=0, padx=(0, 8),
                                  pady=(8, 0), sticky="w")
        tk.Label(frame, text="Prioridad máxima", bg=COLORES["fondo_frame"],
                 fg=COLORES["label"], font=("Arial", 9, "bold"),
                 anchor="w").grid(row=8, column=1, padx=(0, 8),
                                  pady=(8, 0), sticky="w")
        vcmd = (self.register(lambda s: s.isdigit() or s == ""), "%P")
        self.e_prio_min = tk.Entry(frame, font=("Arial", 10), relief="flat",
                                   bd=1, highlightthickness=1,
                                   highlightbackground=COLORES["borde"],
                                   validate="key", validatecommand=vcmd)
        self.e_prio_min.grid(row=9, column=0, padx=(0, 8), pady=(0, 4),
                             sticky="ew")
        self.e_prio_max = tk.Entry(frame, font=("Arial", 10), relief="flat",
                                   bd=1, highlightthickness=1,
                                   highlightbackground=COLORES["borde"],
                                   validate="key", validatecommand=vcmd)
        self.e_prio_max.grid(row=9, column=1, padx=(0, 8), pady=(0, 4),
                             sticky="ew")

        # Contador de resultados en tiempo real
        self.lbl_resultado = tk.Label(
            frame, text="", bg=COLORES["fondo_frame"],
            fg=COLORES["secundario"], font=("Arial", 9, "italic"),
        )
        self.lbl_resultado.grid(row=10, column=0, columnspan=2,
                                pady=(10, 0), sticky="w")

        # Botones
        bframe = tk.Frame(self, bg=COLORES["fondo"])
        bframe.pack(pady=12)
        boton_primario(bframe, "🔍  Aplicar Filtros",
                       self._aplicar).pack(side="left", padx=6)
        boton_primario(bframe, "🔄  Limpiar Filtros",
                       self._limpiar, COLORES["acento"]).pack(side="left", padx=6)
        boton_primario(bframe, "✖  Cancelar",
                       self.destroy, COLORES["peligro"]).pack(side="left", padx=6)

        # Preview en tiempo real al teclear
        for widget in (self.e_nombre, self.e_numero,
                       self.e_concepto, self.e_ruc,
                       self.e_prio_min, self.e_prio_max):
            widget.bind("<KeyRelease>", lambda e: self._preview())
        for v in (self.v_forma_pago, self.v_banco,
                  self.v_status, self.v_ahorro):
            v.trace_add("write", lambda *_: self._preview())

        self._preview()

    # ── Lógica de filtrado ────────────────────────────────────────────────

    def _filtrar(self) -> list[Acreedor]:
        nombre   = self.e_nombre.get().lower().strip()
        numero   = self.e_numero.get().lower().strip()
        concepto = self.e_concepto.get().lower().strip()
        ruc      = self.e_ruc.get().lower().strip()
        forma    = self.v_forma_pago.get()
        banco    = self.v_banco.get()
        status   = self.v_status.get()
        ahorro   = self.v_ahorro.get()
        prio_min = int(self.e_prio_min.get()) if self.e_prio_min.get() else None
        prio_max = int(self.e_prio_max.get()) if self.e_prio_max.get() else None

        resultado = []
        for a in self._acreedores:
            if nombre   and nombre   not in a.nombre.lower():           continue
            if numero   and numero   not in a.numero_acreedor.lower():  continue
            if concepto and concepto not in a.concepto.lower():         continue
            if ruc      and ruc      not in (a.ruc or "").lower():      continue
            if forma    and a.forma_pago    != forma:                   continue
            if banco    and a.banco_pagador != banco:                   continue
            if status   and a.status        != status:                  continue
            if ahorro   and a.ahorro        != ahorro:                  continue
            if prio_min is not None:
                prio = int(a.prioridad) if (a.prioridad or "").isdigit() else 0
                if prio < prio_min: continue
            if prio_max is not None:
                prio = int(a.prioridad) if (a.prioridad or "").isdigit() else 0
                if prio > prio_max: continue
            resultado.append(a)
        return resultado

    def _preview(self) -> None:
        n = len(self._filtrar())
        self.lbl_resultado.config(
            text=f"→ {n} resultado{'s' if n != 1 else ''} encontrado{'s' if n != 1 else ''}"
        )

    def _aplicar(self) -> None:
        self.resultado = self._filtrar()
        self.destroy()

    def _limpiar(self) -> None:
        for e in (self.e_nombre, self.e_numero,
                  self.e_concepto, self.e_ruc,
                  self.e_prio_min, self.e_prio_max):
            e.delete(0, "end")
        for v in (self.v_forma_pago, self.v_banco,
                  self.v_status, self.v_ahorro):
            v.set("")
        self._preview()

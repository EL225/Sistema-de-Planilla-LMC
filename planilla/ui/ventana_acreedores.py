import tkinter as tk
from tkinter import ttk, messagebox

from planilla.repository import Repositorio
from planilla.utils import COLORES, boton_primario
from planilla.ui.ventana_nuevo_acreedor import VentanaNuevoAcreedor
from planilla.ui.ventana_busqueda_avanzada_acreedor import VentanaBusquedaAvanzadaAcreedor


class VentanaAcreedores(tk.Toplevel):
    """Ventana principal de gestión de acreedores."""

    # Columnas visibles en la tabla
    COLUMNAS = (
        "Nombre", "Acreedor", "Concepto", "Prioridad",
        "Ahorro", "Teléfono", "Dirección", "Observación",
        "Forma de Pago", "Tipo Cuenta", "Status",
        "RUC", "DV", "Banco Pagador",
    )
    ANCHOS = (160, 90, 130, 75, 65, 110, 160, 160,
              120, 110, 80, 100, 45, 160)

    def __init__(self, parent, repo: Repositorio):
        super().__init__(parent)
        self.repo = repo
        self._todos: list = []          # caché de todos los acreedores
        self.title("Acreedores")
        self.configure(bg=COLORES["fondo"])
        self._centrar(1260, 680)
        self._construir()
        self._refrescar()

    # ── Posicionamiento ───────────────────────────────────────────────────

    def _centrar(self, w: int, h: int) -> None:
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── Construcción UI ───────────────────────────────────────────────────

    def _construir(self) -> None:
        # ── Encabezado ────────────────────────────────────────────────────
        header = tk.Frame(self, bg=COLORES["primario"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="🏦  ACREEDORES",
            bg=COLORES["primario"], fg="white",
            font=("Arial", 14, "bold"),
        ).pack(expand=True)

        # ── Barra de herramientas ─────────────────────────────────────────
        toolbar = tk.Frame(self, bg=COLORES["fondo"], pady=8)
        toolbar.pack(fill="x", padx=12)

        # Búsqueda rápida
        tk.Label(toolbar, text="🔍", bg=COLORES["fondo"],
                 font=("Arial", 12)).pack(side="left", padx=(0, 4))
        self.e_busqueda = tk.Entry(
            toolbar, width=30, font=("Arial", 10),
            relief="flat", bd=1, highlightthickness=1,
            highlightbackground=COLORES["borde"],
            highlightcolor=COLORES["secundario"],
        )
        self.e_busqueda.pack(side="left", padx=(0, 10), ipady=4)
        self.e_busqueda.bind("<KeyRelease>", lambda e: self._filtrar_rapido())

        # Botones de acción
        boton_primario(toolbar, "🔎  Búsqueda Avanzada",
                       self._busqueda_avanzada,
                       COLORES["secundario"]).pack(side="left", padx=4)
        boton_primario(toolbar, "🗑️  Eliminar Acreedor",
                       self._eliminar,
                       COLORES["peligro"]).pack(side="left", padx=4)
        boton_primario(toolbar, "➕  Nuevo",
                       self._nuevo,
                       COLORES["exito"]).pack(side="left", padx=4)

        # Contador de registros
        self.lbl_total = tk.Label(
            toolbar, text="", bg=COLORES["fondo"],
            fg=COLORES["label"], font=("Arial", 9),
        )
        self.lbl_total.pack(side="right", padx=8)

        # ── Tabla ─────────────────────────────────────────────────────────
        tabla_frame = tk.Frame(self, bg=COLORES["fondo"])
        tabla_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        self.tabla = ttk.Treeview(
            tabla_frame, columns=self.COLUMNAS,
            show="headings", selectmode="browse",
        )
        for col, ancho in zip(self.COLUMNAS, self.ANCHOS):
            self.tabla.heading(col, text=col,
                               command=lambda c=col: self._ordenar(c))
            self.tabla.column(col, width=ancho, anchor="w", minwidth=50)

        vsb = ttk.Scrollbar(tabla_frame, orient="vertical",
                            command=self.tabla.yview)
        hsb = ttk.Scrollbar(tabla_frame, orient="horizontal",
                            command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=vsb.set,
                             xscrollcommand=hsb.set)

        self.tabla.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tabla_frame.rowconfigure(0, weight=1)
        tabla_frame.columnconfigure(0, weight=1)

        self.tabla.tag_configure("par",   background="#EBF5FB")
        self.tabla.tag_configure("impar", background="#FDFEFE")
        self.tabla.tag_configure("inactivo", foreground="#AAAAAA")

        # Doble clic → editar
        self.tabla.bind("<Double-1>", self._editar_seleccionado)

        # Ordenamiento
        self._orden_col: str = ""
        self._orden_asc: bool = True

    # ── Datos ─────────────────────────────────────────────────────────────

    def _refrescar(self) -> None:
        self._todos = self.repo.listar_acreedores()
        self._poblar_tabla(self._todos)

    def _poblar_tabla(self, lista) -> None:
        for row in self.tabla.get_children():
            self.tabla.delete(row)
        for i, a in enumerate(lista):
            tag = "inactivo" if a.status == "Inactivo" else (
                "par" if i % 2 == 0 else "impar"
            )
            self.tabla.insert("", "end",
                              iid=a.numero_acreedor,
                              tags=(tag,),
                              values=(
                                  a.nombre, a.numero_acreedor, a.concepto,
                                  a.prioridad, a.ahorro, a.telefono,
                                  a.direccion, a.observacion,
                                  a.forma_pago, a.tipo_cuenta, a.status,
                                  a.ruc, a.dv, a.banco_pagador,
                              ))
        total = len(lista)
        self.lbl_total.config(
            text=f"{total} acreedor{'es' if total != 1 else ''}"
        )

    # ── Búsqueda ──────────────────────────────────────────────────────────

    def _filtrar_rapido(self) -> None:
        texto = self.e_busqueda.get().lower().strip()
        if not texto:
            self._poblar_tabla(self._todos)
            return
        filtrados = [
            a for a in self._todos
            if texto in a.nombre.lower()
            or texto in a.numero_acreedor.lower()
            or texto in a.concepto.lower()
            or texto in (a.ruc or "").lower()
        ]
        self._poblar_tabla(filtrados)

    def _busqueda_avanzada(self) -> None:
        win = VentanaBusquedaAvanzadaAcreedor(self, self._todos)
        win.grab_set()
        self.wait_window(win)
        if win.resultado is not None:
            self._poblar_tabla(win.resultado)

    # ── Ordenamiento por columna ──────────────────────────────────────────

    def _ordenar(self, col: str) -> None:
        if self._orden_col == col:
            self._orden_asc = not self._orden_asc
        else:
            self._orden_col = col
            self._orden_asc = True
        idx = self.COLUMNAS.index(col)
        ordenados = sorted(
            self._todos,
            key=lambda a: (self._valor_fila(a)[idx] or "").lower(),
            reverse=not self._orden_asc,
        )
        self._poblar_tabla(ordenados)

    def _valor_fila(self, a) -> tuple:
        return (a.nombre, a.numero_acreedor, a.concepto,
                a.prioridad, a.ahorro, a.telefono,
                a.direccion, a.observacion,
                a.forma_pago, a.tipo_cuenta, a.status,
                a.ruc, a.dv, a.banco_pagador)

    # ── Acciones ──────────────────────────────────────────────────────────

    def _nuevo(self) -> None:
        win = VentanaNuevoAcreedor(self, self.repo)
        win.grab_set()
        self.wait_window(win)
        self._refrescar()

    def _editar_seleccionado(self, _event=None) -> None:
        sel = self.tabla.selection()
        if not sel:
            return
        acreedor = self.repo.buscar_acreedor(sel[0])
        if acreedor:
            win = VentanaNuevoAcreedor(self, self.repo, acreedor)
            win.grab_set()
            self.wait_window(win)
            self._refrescar()

    def _eliminar(self) -> None:
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning(
                "Aviso", "Selecciona un acreedor de la tabla primero.",
                parent=self,
            )
            return
        numero = sel[0]
        acreedor = self.repo.buscar_acreedor(numero)
        nombre = acreedor.nombre if acreedor else numero
        if messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar el acreedor «{nombre}»?\nEsta acción no se puede deshacer.",
            parent=self,
        ):
            self.repo.eliminar_acreedor(numero)
            self._refrescar()
            messagebox.showinfo("Eliminado",
                                f"Acreedor «{nombre}» eliminado.",
                                parent=self)

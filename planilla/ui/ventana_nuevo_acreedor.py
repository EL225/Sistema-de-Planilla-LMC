import tkinter as tk
from tkinter import ttk, messagebox

from planilla.models import Acreedor
from planilla.repository import Repositorio
from planilla.utils import COLORES, OPCIONES, campo_con_label, combo_con_label, boton_primario


class VentanaNuevoAcreedor(tk.Toplevel):
    """Formulario para crear o editar un acreedor."""

    def __init__(self, parent, repo: Repositorio,
                 acreedor: Acreedor | None = None):
        super().__init__(parent)
        self.repo     = repo
        self._edicion = acreedor                    # None → modo nuevo
        titulo = "Editar Acreedor" if acreedor else "Nuevo Acreedor"
        self.title(titulo)
        self.resizable(False, False)
        self.configure(bg=COLORES["fondo"])
        self._centrar(720, 640)
        self._construir()
        if acreedor:
            self._cargar(acreedor)

    # ── Posicionamiento ───────────────────────────────────────────────────

    def _centrar(self, w: int, h: int) -> None:
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── Construcción UI ───────────────────────────────────────────────────

    def _construir(self) -> None:
        icono  = "✏️" if self._edicion else "➕"
        titulo = "Editar Acreedor" if self._edicion else "Nuevo Acreedor"

        # Encabezado
        header = tk.Frame(self, bg=COLORES["primario"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text=f"{icono}  {titulo.upper()}",
            bg=COLORES["primario"], fg="white",
            font=("Arial", 13, "bold"),
        ).pack(expand=True)

        # Cuerpo con scroll
        canvas = tk.Canvas(self, bg=COLORES["fondo_frame"],
                           highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        self.frame = tk.Frame(canvas, bg=COLORES["fondo_frame"])
        win_id = canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.frame.bind("<Configure>",
                        lambda e: canvas.configure(
                            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win_id, width=e.width))

        self._construir_campos()

        # Botones
        bframe = tk.Frame(self, bg=COLORES["fondo"])
        bframe.pack(pady=12)
        boton_primario(bframe, "💾  Guardar",  self._guardar).pack(side="left", padx=6)
        boton_primario(bframe, "🔄  Limpiar",  self._limpiar,
                       COLORES["acento"]).pack(side="left", padx=6)
        boton_primario(bframe, "❌  Cerrar",   self.destroy,
                       COLORES["peligro"]).pack(side="left", padx=6)

    def _construir_campos(self) -> None:
        f = self.frame
        f.columnconfigure((0, 1, 2), weight=1)

        # ── Sección Identificación ────────────────────────────────────────
        self._seccion(f, "IDENTIFICACIÓN", 0)

        self.e_nombre   = campo_con_label(f, "Nombre *",   2, 0, colspan=2)
        self.e_numero   = campo_con_label(f, "Acreedor *", 2, 2)
        self.e_concepto = campo_con_label(f, "Concepto",   4, 0, colspan=2)
        self.e_ruc      = campo_con_label(f, "RUC",        4, 2)

        self.e_dv       = campo_con_label(f, "DV",         6, 0, width=10)

        # Prioridad: solo numérico
        tk.Label(f, text="Prioridad (número)", bg=COLORES["fondo_frame"],
                 fg=COLORES["label"], font=("Arial", 9, "bold"),
                 anchor="w").grid(row=6, column=1, padx=(10, 4),
                                  pady=(6, 0), sticky="w")
        vcmd = (self.register(lambda s: s.isdigit() or s == ""), "%P")
        self.e_prioridad = tk.Entry(
            f, width=22, font=("Arial", 10),
            relief="flat", bd=1, highlightthickness=1,
            highlightbackground=COLORES["borde"],
            highlightcolor=COLORES["secundario"],
            validate="key", validatecommand=vcmd,
        )
        self.e_prioridad.grid(row=7, column=1, padx=(10, 4),
                              pady=(0, 4), sticky="ew")

        self.v_ahorro, _ = combo_con_label(
            f, "Ahorro", OPCIONES["ahorro"], 6, 2)

        # ── Sección Contacto ──────────────────────────────────────────────
        self._seccion(f, "CONTACTO", 8)

        self.e_telefono = campo_con_label(f, "Teléfono", 10, 0)

        # Dirección: Text multilinea
        tk.Label(f, text="Dirección", bg=COLORES["fondo_frame"],
                 fg=COLORES["label"], font=("Arial", 9, "bold"),
                 anchor="w").grid(row=10, column=1, columnspan=2,
                                  padx=(10, 4), pady=(6, 0), sticky="w")
        self.t_direccion = tk.Text(
            f, width=42, height=3, font=("Arial", 10),
            relief="flat", bd=1, highlightthickness=1,
            highlightbackground=COLORES["borde"],
            highlightcolor=COLORES["secundario"],
            wrap="word",
        )
        self.t_direccion.grid(row=11, column=1, columnspan=2,
                              padx=(10, 4), pady=(0, 4), sticky="ew")

        # Observación: Text multilinea
        tk.Label(f, text="Observación", bg=COLORES["fondo_frame"],
                 fg=COLORES["label"], font=("Arial", 9, "bold"),
                 anchor="w").grid(row=12, column=0, columnspan=3,
                                  padx=(10, 4), pady=(6, 0), sticky="w")
        self.t_observacion = tk.Text(
            f, width=70, height=3, font=("Arial", 10),
            relief="flat", bd=1, highlightthickness=1,
            highlightbackground=COLORES["borde"],
            highlightcolor=COLORES["secundario"],
            wrap="word",
        )
        self.t_observacion.grid(row=13, column=0, columnspan=3,
                                padx=(10, 4), pady=(0, 4), sticky="ew")

        # ── Sección Pago ──────────────────────────────────────────────────
        self._seccion(f, "DATOS DE PAGO", 14)

        self.v_forma_pago,  _ = combo_con_label(
            f, "Forma de Pago",    OPCIONES["forma_pago"],    16, 0)
        self.v_tipo_cuenta, _ = combo_con_label(
            f, "Tipo de Cuenta",   OPCIONES["tipo_cuenta"],   16, 1)
        self.v_banco,       _ = combo_con_label(
            f, "Banco Pagador",    OPCIONES["banco_pagador"],  16, 2, width=26)
        self.v_status,      _ = combo_con_label(
            f, "Status",           OPCIONES["status_acreedor"], 18, 0)

    def _seccion(self, parent, titulo: str, row: int) -> None:
        tk.Label(parent, text=titulo,
                 bg=COLORES["fondo_frame"], fg=COLORES["primario"],
                 font=("Arial", 10, "bold")).grid(
            row=row, column=0, columnspan=3,
            padx=10, pady=(14, 2), sticky="w")
        ttk.Separator(parent, orient="horizontal").grid(
            row=row + 1, column=0, columnspan=3,
            sticky="ew", padx=10)

    # ── Carga de datos (modo edición) ─────────────────────────────────────

    def _cargar(self, a: Acreedor) -> None:
        def _set(entry, val):
            entry.delete(0, "end")
            entry.insert(0, val or "")

        _set(self.e_nombre,    a.nombre)
        _set(self.e_numero,    a.numero_acreedor)
        _set(self.e_concepto,  a.concepto)
        _set(self.e_ruc,       a.ruc)
        _set(self.e_dv,        a.dv)
        _set(self.e_prioridad, a.prioridad)
        _set(self.e_telefono,  a.telefono)

        self.t_direccion.delete("1.0", "end")
        self.t_direccion.insert("1.0", a.direccion or "")
        self.t_observacion.delete("1.0", "end")
        self.t_observacion.insert("1.0", a.observacion or "")

        self.v_ahorro.set(a.ahorro)
        self.v_forma_pago.set(a.forma_pago)
        self.v_tipo_cuenta.set(a.tipo_cuenta)
        self.v_banco.set(a.banco_pagador)
        self.v_status.set(a.status)

    # ── Recoger datos del formulario ──────────────────────────────────────

    def _recoger(self) -> Acreedor:
        return Acreedor(
            nombre=self.e_nombre.get().strip(),
            numero_acreedor=self.e_numero.get().strip(),
            concepto=self.e_concepto.get().strip(),
            prioridad=self.e_prioridad.get().strip(),
            ahorro=self.v_ahorro.get(),
            telefono=self.e_telefono.get().strip(),
            direccion=self.t_direccion.get("1.0", "end").strip(),
            observacion=self.t_observacion.get("1.0", "end").strip(),
            forma_pago=self.v_forma_pago.get(),
            tipo_cuenta=self.v_tipo_cuenta.get(),
            status=self.v_status.get() or "Activo",
            ruc=self.e_ruc.get().strip(),
            dv=self.e_dv.get().strip(),
            banco_pagador=self.v_banco.get(),
        )

    # ── Acciones ──────────────────────────────────────────────────────────

    def _guardar(self) -> None:
        acreedor = self._recoger()
        errores  = acreedor.validar()
        if errores:
            messagebox.showerror("Validación", "\n".join(errores), parent=self)
            return
        self.repo.guardar_acreedor(acreedor)
        accion = "actualizado" if self._edicion else "guardado"
        messagebox.showinfo("✅ Éxito",
                            f"Acreedor «{acreedor.nombre}» {accion} correctamente.",
                            parent=self)
        self._edicion = acreedor       # queda en modo edición tras guardar

    def _limpiar(self) -> None:
        if self._edicion:
            if not messagebox.askyesno(
                "Confirmar", "¿Descartar cambios y limpiar el formulario?",
                parent=self,
            ):
                return
        for e in (self.e_nombre, self.e_numero, self.e_concepto,
                  self.e_ruc, self.e_dv, self.e_prioridad, self.e_telefono):
            e.delete(0, "end")
        self.t_direccion.delete("1.0", "end")
        self.t_observacion.delete("1.0", "end")
        for v in (self.v_ahorro, self.v_forma_pago,
                  self.v_tipo_cuenta, self.v_banco, self.v_status):
            v.set("")
        self._edicion = None

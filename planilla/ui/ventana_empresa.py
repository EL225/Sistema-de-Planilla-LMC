import tkinter as tk
from tkinter import ttk, messagebox

from planilla.models import Empresa
from planilla.repository import Repositorio
from planilla.utils import COLORES, campo_con_label, boton_primario


class VentanaEmpresa(tk.Toplevel):
    """Ventana de gestión de empresas: tabla a la derecha, formulario a la izquierda,
    sidebar de navegación entre registros integrada en el panel del formulario."""

    COLUMNAS = ("Nombre", "RUC", "DV", "Correlativo",
                "Teléfono 1", "Email", "F. Apertura", "F. Expiración")
    ANCHOS   = (200, 110, 45, 100, 110, 180, 110, 110)

    def __init__(self, parent, repo: Repositorio):
        super().__init__(parent)
        self.repo = repo
        self._id_editando: str | None = None
        self._todos: list = []
        self._orden_col = ""
        self._orden_asc = True
        self.title("Gestión de Empresas")
        self.configure(bg=COLORES["fondo"])
        self._centrar(1100, 680)
        self._construir()
        self._refrescar()

    # ── Posicionamiento ───────────────────────────────────────────────────

    def _centrar(self, w: int, h: int) -> None:
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── Construcción principal ────────────────────────────────────────────

    def _construir(self) -> None:
        header = tk.Frame(self, bg=COLORES["primario"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="🏢  GESTIÓN DE EMPRESAS",
            bg=COLORES["primario"], fg="white",
            font=("Arial", 14, "bold"),
        ).pack(expand=True)

        paned = tk.PanedWindow(self, orient="horizontal",
                               bg=COLORES["fondo"], sashwidth=5,
                               sashrelief="flat")
        paned.pack(fill="both", expand=True, padx=12, pady=10)

        paned.add(self._panel_izquierdo(paned), minsize=400, width=440)
        paned.add(self._panel_derecho(paned),   minsize=380)

    # ── Panel izquierdo: sidebar de navegación + formulario ───────────────

    def _panel_izquierdo(self, paned) -> tk.Frame:
        outer = tk.Frame(paned, bg=COLORES["fondo"])

        # Sidebar angosta con botones de navegación y acción
        sidebar = tk.Frame(outer, bg=COLORES["primario"], width=46)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        def nav_btn(text, cmd):
            btn = tk.Button(
                sidebar, text=text, command=cmd,
                bg=COLORES["primario"], fg="white",
                font=("Arial", 13), relief="flat",
                activebackground=COLORES["secundario"],
                activeforeground="white", cursor="hand2",
                width=2, pady=5,
            )
            btn.pack(fill="x", pady=1, padx=3)
            return btn

        # tk.Label(sidebar, text="Nav", bg=COLORES["primario"], fg="#AED6F1",
        #          font=("Arial", 7)).pack(pady=(10, 3))
        # nav_btn("⏮", self._ir_primero)
        # nav_btn("◀",  self._ir_anterior)
        # nav_btn("▶",  self._ir_siguiente)
        # nav_btn("⏭", self._ir_ultimo)

        # ttk.Separator(sidebar, orient="horizontal").pack(
        #     fill="x", pady=6, padx=4)

        tk.Label(sidebar, text="Ops", bg=COLORES["primario"], fg="#AED6F1",
                 font=("Arial", 7)).pack(pady=(0, 3))
        nav_btn("🆕", self._nuevo)
        nav_btn("💾", self._guardar)
        nav_btn("🗑", self._eliminar)

        self.lbl_pos = tk.Label(
            sidebar, text="0/0",
            bg=COLORES["primario"], fg="#AED6F1",
            font=("Arial", 8),
        )
        self.lbl_pos.pack(pady=(10, 0))

        # Área de formulario con scroll
        form_area = tk.Frame(outer, bg=COLORES["fondo_frame"])
        form_area.pack(side="left", fill="both", expand=True)

        canvas = tk.Canvas(form_area, bg=COLORES["fondo_frame"],
                           highlightthickness=0)
        sb = ttk.Scrollbar(form_area, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        self.form = tk.Frame(canvas, bg=COLORES["fondo_frame"])
        win_id = canvas.create_window((0, 0), window=self.form, anchor="nw")
        self.form.bind("<Configure>",
                       lambda e: canvas.configure(
                           scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win_id, width=e.width))

        self._construir_formulario()
        return outer

    def _construir_formulario(self) -> None:
        f = self.form
        f.columnconfigure((0, 1), weight=1)

        self._seccion(f, "DATOS GENERALES", 0)
        self.e_nombre      = campo_con_label(f, "Nombre *",    2, 0, colspan=2, width=36)
        self.e_ruc         = campo_con_label(f, "RUC *",       4, 0)
        self.e_dv          = campo_con_label(f, "DV",          4, 1, width=10)
        self.e_correlativo = campo_con_label(f, "Correlativo", 6, 0)
        self.e_email       = campo_con_label(f, "Email",       6, 1)

        self._seccion(f, "CONTACTO", 8)
        self.e_tel1 = campo_con_label(f, "Teléfono 1", 10, 0)
        self.e_tel2 = campo_con_label(f, "Teléfono 2", 10, 1)
        self.e_dir  = campo_con_label(f, "Dirección",  12, 0, colspan=2, width=40)

        self._seccion(f, "FECHAS", 14)
        self.e_f_apertura   = campo_con_label(
            f, "Fecha de Apertura (AAAA-MM-DD)",   16, 0)
        self.e_f_expiracion = campo_con_label(
            f, "Fecha de Expiración (AAAA-MM-DD)", 16, 1)

        tk.Label(f, text="ID interno", bg=COLORES["fondo_frame"],
                 fg=COLORES["borde"], font=("Arial", 8), anchor="w").grid(
            row=18, column=0, padx=10, pady=(14, 0), sticky="w")
        self.lbl_id = tk.Label(f, text="—", bg=COLORES["fondo_frame"],
                               fg=COLORES["borde"], font=("Arial", 8), anchor="w")
        self.lbl_id.grid(row=19, column=0, padx=10, sticky="w")

    def _seccion(self, parent, titulo: str, row: int) -> None:
        tk.Label(parent, text=titulo,
                 bg=COLORES["fondo_frame"], fg=COLORES["primario"],
                 font=("Arial", 10, "bold")).grid(
            row=row, column=0, columnspan=2,
            padx=10, pady=(14, 2), sticky="w")
        ttk.Separator(parent, orient="horizontal").grid(
            row=row + 1, column=0, columnspan=2,
            sticky="ew", padx=10)

    # ── Panel derecho: búsqueda + tabla ───────────────────────────────────

    def _panel_derecho(self, paned) -> tk.Frame:
        outer = tk.Frame(paned, bg=COLORES["fondo"])

        toolbar = tk.Frame(outer, bg=COLORES["fondo"], pady=6)
        toolbar.pack(fill="x", padx=4)

        tk.Label(toolbar, text="🔍", bg=COLORES["fondo"],
                 font=("Arial", 12)).pack(side="left", padx=(0, 2))
        self.e_busqueda = tk.Entry(
            toolbar, font=("Arial", 10), relief="flat", bd=1,
            highlightthickness=1,
            highlightbackground=COLORES["borde"],
            highlightcolor=COLORES["secundario"],
        )
        self.e_busqueda.pack(side="left", fill="x", expand=True,
                             padx=(0, 8), ipady=4)
        self.e_busqueda.bind("<KeyRelease>", lambda e: self._filtrar())

        boton_primario(toolbar, "➕ Nueva",    self._nuevo,
                       COLORES["exito"]).pack(side="left", padx=2)
        boton_primario(toolbar, "🗑 Eliminar", self._eliminar,
                       COLORES["peligro"]).pack(side="left", padx=2)

        self.lbl_total = tk.Label(toolbar, text="", bg=COLORES["fondo"],
                                  fg=COLORES["label"], font=("Arial", 9))
        self.lbl_total.pack(side="right", padx=6)

        tabla_frame = tk.Frame(outer, bg=COLORES["fondo"])
        tabla_frame.pack(fill="both", expand=True, padx=4)

        self.tabla = ttk.Treeview(tabla_frame, columns=self.COLUMNAS,
                                  show="headings", selectmode="browse")
        for col, ancho in zip(self.COLUMNAS, self.ANCHOS):
            self.tabla.heading(col, text=col,
                               command=lambda c=col: self._ordenar(c))
            self.tabla.column(col, width=ancho, anchor="w", minwidth=40)

        vsb = ttk.Scrollbar(tabla_frame, orient="vertical",
                            command=self.tabla.yview)
        hsb = ttk.Scrollbar(tabla_frame, orient="horizontal",
                            command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tabla_frame.rowconfigure(0, weight=1)
        tabla_frame.columnconfigure(0, weight=1)

        self.tabla.tag_configure("par",   background="#EBF5FB")
        self.tabla.tag_configure("impar", background="#FDFEFE")
        self.tabla.bind("<<TreeviewSelect>>", self._seleccionar_fila)

        return outer

    # ── Datos ─────────────────────────────────────────────────────────────

    def _refrescar(self, mantener_sel: str = None) -> None:
        self._todos = self.repo.listar_empresas()
        self._poblar_tabla(self._todos)
        self._actualizar_pos()
        if mantener_sel:
            try:
                self.tabla.selection_set(mantener_sel)
                self.tabla.see(mantener_sel)
            except Exception:
                pass

    def _poblar_tabla(self, lista: list) -> None:
        for row in self.tabla.get_children():
            self.tabla.delete(row)
        for i, e in enumerate(lista):
            tag = "par" if i % 2 == 0 else "impar"
            self.tabla.insert("", "end", iid=e.id, tags=(tag,), values=(
                e.nombre, e.ruc, e.dv, e.correlativo,
                e.telefono1, e.email, e.fecha_apertura, e.fecha_expiracion,
            ))
        n = len(lista)
        self.lbl_total.config(
            text=f"{n} empresa{'s' if n != 1 else ''}")

    # ── Navegación sidebar ────────────────────────────────────────────────

    # def _ids_tabla(self) -> list[str]:
    #     return list(self.tabla.get_children())

    # def _ir_primero(self) -> None:
    #     ids = self._ids_tabla()
    #     if ids:
    #         self._nav_a(ids[0])

    # def _ir_ultimo(self) -> None:
    #     ids = self._ids_tabla()
    #     if ids:
    #         self._nav_a(ids[-1])

    # def _ir_anterior(self) -> None:
    #     ids = self._ids_tabla()
    #     if not ids:
    #         return
    #     sel = self.tabla.selection()
    #     idx = ids.index(sel[0]) if sel and sel[0] in ids else 0
    #     self._nav_a(ids[max(0, idx - 1)])

    # def _ir_siguiente(self) -> None:
    #     ids = self._ids_tabla()
    #     if not ids:
    #         return
    #     sel = self.tabla.selection()
    #     idx = ids.index(sel[0]) if sel and sel[0] in ids else -1
    #     self._nav_a(ids[min(len(ids) - 1, idx + 1)])

    # def _nav_a(self, id: str) -> None:
    #     self.tabla.selection_set(id)
    #     self.tabla.see(id)
    #     empresa = self.repo.buscar_empresa(id)
    #     if empresa:
    #         self._cargar_en_form(empresa)
    #     self._actualizar_pos()

    # def _actualizar_pos(self) -> None:
    #     ids  = self._ids_tabla()
    #     sel  = self.tabla.selection()
    #     pos  = (ids.index(sel[0]) + 1) if (sel and sel[0] in ids) else 0
    #     self.lbl_pos.config(text=f"{pos}/{len(ids)}")

    # ── Filtrado y ordenamiento ───────────────────────────────────────────

    def _actualizar_pos(self) -> None:
        pass  # sidebar eliminado; reservado para uso futuro

    def _filtrar(self) -> None:
        texto = self.e_busqueda.get().lower().strip()
        filtrados = self._todos if not texto else [
            e for e in self._todos
            if texto in e.nombre.lower()
            or texto in e.ruc.lower()
            or texto in (e.email or "").lower()
        ]
        self._poblar_tabla(filtrados)
        self._actualizar_pos()

    def _ordenar(self, col: str) -> None:
        self._orden_asc = not self._orden_asc if self._orden_col == col else True
        self._orden_col = col
        idx = self.COLUMNAS.index(col)
        ordered = sorted(
            self._todos,
            key=lambda e: (self._fila_vals(e)[idx] or "").lower(),
            reverse=not self._orden_asc,
        )
        self._poblar_tabla(ordered)

    def _fila_vals(self, e: Empresa) -> tuple:
        return (e.nombre, e.ruc, e.dv, e.correlativo,
                e.telefono1, e.email, e.fecha_apertura, e.fecha_expiracion)

    # ── Formulario ────────────────────────────────────────────────────────

    def _seleccionar_fila(self, _event=None) -> None:
        sel = self.tabla.selection()
        if sel:
            empresa = self.repo.buscar_empresa(sel[0])
            if empresa:
                self._cargar_en_form(empresa)
            self._actualizar_pos()

    def _cargar_en_form(self, e: Empresa) -> None:
        self._id_editando = e.id
        self._limpiar_campos()

        def _s(entry, val):
            entry.delete(0, "end")
            entry.insert(0, val or "")

        _s(self.e_nombre,       e.nombre)
        _s(self.e_ruc,          e.ruc)
        _s(self.e_dv,           e.dv)
        _s(self.e_correlativo,  e.correlativo)
        _s(self.e_email,        e.email)
        _s(self.e_tel1,         e.telefono1)
        _s(self.e_tel2,         e.telefono2)
        _s(self.e_dir,          e.direccion)
        _s(self.e_f_apertura,   e.fecha_apertura)
        _s(self.e_f_expiracion, e.fecha_expiracion)
        self.lbl_id.config(text=e.id)

    def _recoger_form(self) -> Empresa:
        return Empresa(
            id=self._id_editando,
            nombre=self.e_nombre.get().strip(),
            ruc=self.e_ruc.get().strip(),
            dv=self.e_dv.get().strip(),
            correlativo=self.e_correlativo.get().strip(),
            email=self.e_email.get().strip(),
            telefono1=self.e_tel1.get().strip(),
            telefono2=self.e_tel2.get().strip(),
            direccion=self.e_dir.get().strip(),
            fecha_apertura=self.e_f_apertura.get().strip(),
            fecha_expiracion=self.e_f_expiracion.get().strip(),
        )

    def _limpiar_campos(self) -> None:
        for e in (self.e_nombre, self.e_ruc, self.e_dv, self.e_correlativo,
                  self.e_email, self.e_tel1, self.e_tel2, self.e_dir,
                  self.e_f_apertura, self.e_f_expiracion):
            e.delete(0, "end")

    # ── Acciones ──────────────────────────────────────────────────────────

    def _nuevo(self) -> None:
        self.tabla.selection_remove(*self.tabla.selection())
        self._id_editando = None
        self._limpiar_campos()
        self.lbl_id.config(text="—")
        self._actualizar_pos()
        self.e_nombre.focus_set()

    def _guardar(self) -> None:
        empresa = self._recoger_form()
        errores = empresa.validar()
        if errores:
            messagebox.showerror("Validación", "\n".join(errores), parent=self)
            return
        self.repo.guardar_empresa(empresa)
        self._id_editando = empresa.id
        self._refrescar(mantener_sel=empresa.id)
        messagebox.showinfo("✅ Guardado",
                            f"Empresa «{empresa.nombre}» guardada correctamente.",
                            parent=self)

    def _eliminar(self) -> None:
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Aviso",
                                   "Selecciona una empresa de la tabla primero.",
                                   parent=self)
            return
        empresa = self.repo.buscar_empresa(sel[0])
        nombre  = empresa.nombre if empresa else sel[0]
        if messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar la empresa «{nombre}»?\nEsta acción no se puede deshacer.",
            parent=self,
        ):
            self.repo.eliminar_empresa(sel[0])
            self._id_editando = None
            self._limpiar_campos()
            self.lbl_id.config(text="—")
            self._refrescar()
            messagebox.showinfo("Eliminado",
                                f"Empresa «{nombre}» eliminada.", parent=self)

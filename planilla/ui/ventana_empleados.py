import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from planilla.models import Empleado
from planilla.repository import Repositorio
from planilla.utils import COLORES, OPCIONES, campo_con_label, combo_con_label, boton_primario
from planilla.constantes.tasas_css import calcular_css


class VentanaEmpleados(tk.Toplevel):
    """Ventana completa de gestión de empleados (formulario + tabla)."""

    def __init__(self, parent, repo: Repositorio):
        super().__init__(parent)
        self.repo = repo
        self._emp_editando: str | None = None
        self.title("Gestión de Empleados")
        self.configure(bg=COLORES["fondo"])
        self._centrar(1060, 720)
        self._construir()
        self._actualizar_tabla()

    # ── Posicionamiento ───────────────────────────────────────────────────

    def _centrar(self, w: int, h: int) -> None:
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── Construcción general ──────────────────────────────────────────────

    def _construir(self) -> None:
        header = tk.Frame(self, bg=COLORES["primario"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="👥  GESTIÓN DE EMPLEADOS",
            bg=COLORES["primario"], fg="white",
            font=("Arial", 14, "bold"),
        ).pack(expand=True)

        paned = tk.PanedWindow(self, orient="horizontal",
                               bg=COLORES["fondo"], sashwidth=5,
                               sashrelief="flat")
        paned.pack(fill="both", expand=True, padx=12, pady=10)

        form_outer = self._crear_panel_formulario(paned)
        tabla_frame = tk.Frame(paned, bg=COLORES["fondo"])

        paned.add(form_outer,  minsize=420, width=480)
        paned.add(tabla_frame, minsize=400)

        self._construir_tabla(tabla_frame)

    # ── Panel izquierdo: formulario con scroll ────────────────────────────

    def _crear_panel_formulario(self, paned) -> tk.Frame:
        outer = tk.Frame(paned, bg=COLORES["fondo"])

        # ── Formulario con scroll ─────────────────────────────────────────
        canvas = tk.Canvas(outer, bg=COLORES["fondo_frame"],
                           highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

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

        self._seccion(f, "DATOS PERSONALES", 0)

        self.e_nombre    = campo_con_label(f, "Nombre *",                2, 0)
        self.e_apellido  = campo_con_label(f, "Apellido *",              2, 1)
        self.e_codigo    = campo_con_label(f, "Código de Empleado *",    4, 0)
        self.e_cedula    = campo_con_label(f, "Cédula *",                4, 1)
        self.e_f_nac     = campo_con_label(f, "Fecha Nacimiento (AAAA-MM-DD)", 6, 0)

        self.v_sexo,        _ = combo_con_label(f, "Sexo",         OPCIONES["sexo"],        6, 1)
        self.v_estado_civil, _ = combo_con_label(f, "Estado Civil", OPCIONES["estado_civil"], 8, 0)

        self.e_tel1  = campo_con_label(f, "Teléfono 1", 8,  1)
        self.e_tel2  = campo_con_label(f, "Teléfono 2", 10, 0)
        self.e_email = campo_con_label(f, "Email",       10, 1)
        self.e_dir   = campo_con_label(f, "Dirección",   12, 0, colspan=2, width=40)

        self._seccion(f, "DATOS LABORALES", 14)

        self.e_f_inicio = campo_con_label(f, "Fecha Inicio (AAAA-MM-DD)",      16, 0)
        self.e_f_term   = campo_con_label(f, "Fecha Terminación (AAAA-MM-DD)", 16, 1)

        self.v_dpto,         _ = combo_con_label(f, "Departamento",   OPCIONES["departamento"],  18, 0)
        self.v_tipo_planilla, self._cb_tipo_planilla = combo_con_label(f, "Tipo Planilla",  OPCIONES["tipo_planilla"], 18, 1)
        self.v_status,       _ = combo_con_label(f, "Status",          OPCIONES["status"],        20, 0)
        self.v_horas_quincena, self._cb_horas = combo_con_label(f, "Horas Laboradas", ["104", "96", "88"], 20, 1)

        # Empresa (debajo de Status, columna 0)
        self.v_empresa, self._cb_empresa = combo_con_label(f, "Empresa", [], 22, 0)
        self._refrescar_empresas()

        # Botón Horas Laboradas por Mes (debajo de Horas Laboradas, columna 1)
        btn_horas_mes = tk.Button(
            f, text="📅  Horas Laboradas por Mes",
            command=self._abrir_ventana_horas_mes,
            bg=COLORES["secundario"], fg="white",
            font=("Arial", 9, "bold"), relief="flat",
            padx=8, pady=4, cursor="hand2",
            activebackground=COLORES["primario"],
            activeforeground="white",
        )
        btn_horas_mes.grid(row=23, column=1, padx=10, pady=(4, 6), sticky="w")

        # Casilla de horas personalizadas (oculta — mantenida por compatibilidad)
        self._frame_horas_personalizadas = tk.Frame(f, bg=COLORES["fondo_frame"])
        self.e_horas_personalizadas = tk.Entry(self._frame_horas_personalizadas)

        # Vincular cambio de tipo de planilla
        self.v_tipo_planilla.trace_add("write", self._on_tipo_planilla_change)


        self._seccion(f, "DATOS BANCARIOS", 25)

        self.v_tipo_cuenta, _ = combo_con_label(f, "Tipo de Cuenta", OPCIONES["tipo_cuenta"], 27, 0)
        self.e_cuenta = campo_con_label(f, "Número de Cuenta Banco", 27, 1, width=22)
        self.v_tipo_cuenta, _ = combo_con_label(f, "Tipo de Cuenta",   OPCIONES["tipo_cuenta"], 27, 0)
        self.e_salario = campo_con_label(f, "Salario",                  29, 0, width=22)

        # Seguro Social
        self.v_seguro = tk.BooleanVar()
        ss_frame = tk.Frame(f, bg=COLORES["fondo_frame"])
        ss_frame.grid(row=31, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        tk.Checkbutton(
            ss_frame, text="  Retención de Seguro Social",
            variable=self.v_seguro,
            bg=COLORES["fondo_frame"], fg=COLORES["texto"],
            font=("Arial", 10),
            activebackground=COLORES["fondo_frame"],
            selectcolor=COLORES["fondo_frame"],
        ).pack(side="left")

        # Botones
        btn_frame = tk.Frame(f, bg=COLORES["fondo_frame"])
        btn_frame.grid(row=33, column=0, columnspan=2, pady=14)
        boton_primario(btn_frame, "💾  Guardar",  self._guardar_empleado).pack(side="left", padx=5)
        boton_primario(btn_frame, "🗑️  Eliminar", self._eliminar_empleado,
                       COLORES["peligro"]).pack(side="left", padx=5)
        boton_primario(btn_frame, "🆕  Nuevo",    self._limpiar_form,
                       COLORES["acento"]).pack(side="left", padx=5)

    def _seccion(self, parent, titulo: str, row: int) -> None:
        tk.Label(parent, text=titulo,
                 bg=COLORES["fondo_frame"], fg=COLORES["primario"],
                 font=("Arial", 10, "bold")).grid(
            row=row, column=0, columnspan=2, padx=10, pady=(12, 2), sticky="w")
        ttk.Separator(parent, orient="horizontal").grid(
            row=row + 1, column=0, columnspan=2, sticky="ew", padx=10)

    # ── Panel derecho: tabla ──────────────────────────────────────────────

    def _construir_tabla(self, parent: tk.Frame) -> None:
        busq_frame = tk.Frame(parent, bg=COLORES["fondo"])
        busq_frame.pack(fill="x", pady=(0, 6))
        tk.Label(busq_frame, text="🔍", bg=COLORES["fondo"],
                 font=("Arial", 12)).pack(side="left", padx=(4, 2))
        self.e_busqueda = tk.Entry(
            busq_frame, font=("Arial", 10), relief="flat", bd=1,
            highlightthickness=1, highlightbackground=COLORES["borde"],
            highlightcolor=COLORES["secundario"],
        )
        self.e_busqueda.pack(side="left", fill="x", expand=True, padx=4, pady=4)
        self.e_busqueda.bind("<KeyRelease>", lambda e: self._filtrar())

        NOMBRES_MES = ["1er Mes", "2do Mes", "3er Mes", "4to Mes", "5to Mes",
                       "6to Mes", "7mo Mes", "8vo Mes", "9no Mes", "10mo Mes",
                       "11mo Mes", "12mo Mes", "13er Mes"]

        cols = ("Código", "Empresa", "Nombre Completo", "Cédula", "Departamento",
                "Tipo Planilla", "Hrs. Lab.", "Rata/Hora", "Hrs. Desc.",
                *NOMBRES_MES,
                "Salario Neto", "Salario Anual", "ISR", "Status", "Seg. Social",
                "SSE", "SSP", "SEE", "SEP")
        anchos = [90, 140, 190, 110, 130, 110, 80, 85, 80,
                  *[90]*13,
                  95, 105, 90, 90, 85, 80, 80, 80, 80]

        tabla_frame = tk.Frame(parent, bg=COLORES["fondo"])
        tabla_frame.pack(fill="both", expand=True)
        tabla_frame.rowconfigure(0, weight=1)
        tabla_frame.columnconfigure(0, weight=1)

        vsb = ttk.Scrollbar(tabla_frame, orient="vertical")
        hsb = ttk.Scrollbar(tabla_frame, orient="horizontal")

        self.tabla = ttk.Treeview(
            tabla_frame, columns=cols, show="headings",
            selectmode="browse", height=20,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
        )
        vsb.configure(command=self.tabla.yview)
        hsb.configure(command=self.tabla.xview)

        for col, ancho in zip(cols, anchos):
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center")

        self.tabla.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.tabla.tag_configure("par",   background="#EBF5FB")
        self.tabla.tag_configure("impar", background="#FDFEFE")
        self.tabla.bind("<<TreeviewSelect>>", self._seleccionar_empleado)

    # ── Lógica de tabla ───────────────────────────────────────────────────

    def _actualizar_tabla(self, filtro: str = "") -> None:
        for row in self.tabla.get_children():
            self.tabla.delete(row)
        filtro = filtro.lower()
        hoy = date.today()
        for i, emp in enumerate(self.repo.listar_empleados()):
            if filtro and filtro not in emp.nombre_completo().lower() \
                    and filtro not in emp.cedula.lower() \
                    and filtro not in emp.codigo.lower():
                continue
            tag = "par" if i % 2 == 0 else "impar"

            # Hrs. Lab.: mostrar horas del contrato
            hrs_mostrar = emp.horas_quincena

            # Calcular los 13 meses acumulativos
            acumulado = 0.0
            vals_mes = []
            for m in range(1, 14):
                horas_mes = getattr(emp, f"horas_mes_{m}", "") or ""
                if horas_mes:
                    ganado = self._calcular_ganado_mes(
                        emp.salario, emp.horas_quincena,
                        horas_mes, emp.tipo_planilla)
                else:
                    try:
                        ganado = float(emp.salario)
                    except (ValueError, TypeError):
                        ganado = 0.0
                acumulado = round(acumulado + ganado, 2)
                vals_mes.append(f"${acumulado:.2f}")

            # Salario Neto = acumulado del mes 13
            salario_neto_f = acumulado
            salario_neto   = f"${salario_neto_f:.2f}"

            # Salario Anual = Salario Neto × 13  (campo heredado)
            try:
                salario_base = float(emp.salario)
                descontado_f = float(emp.descontado) if getattr(emp, "descontado", "") else 0.0
                salario_mensual = salario_base - descontado_f
                salario_anual_f = salario_mensual * 13
                salario_anual = f"${salario_anual_f:.2f}"
            except (ValueError, TypeError):
                salario_anual_f = 0.0
                salario_anual = ""

            # ISR = (Salario Anual - 11000) × tasa
            try:
                base_isr = salario_anual_f - 11000
                if base_isr <= 0:
                    isr = "$0.00"
                elif base_isr <= 50000:
                    isr = f"${base_isr * 0.15:.2f}"
                else:
                    isr = f"${base_isr * 0.25:.2f}"
            except Exception:
                isr = ""

            descontado = getattr(emp, "descontado", "") or ""

            # Calcular SS y SE usando Salario Neto mensual como base
            if emp.seguro_social:
                try:
                    base_ss = salario_base - descontado_f
                except Exception:
                    base_ss = 0.0
                css = calcular_css(base_ss, hoy)
                sse = f"${css['empleado']:.2f}"
                ssp = f"${css['patronal']:.2f}"
                see = f"${css['see']:.2f}"
                sep = f"${css['sep']:.2f}"
            else:
                sse = ssp = see = sep = ""

            self.tabla.insert("", "end", iid=emp.codigo, tags=(tag,), values=(
                emp.codigo, getattr(emp, "empresa", "") or "",
                emp.nombre_completo(), emp.cedula,
                emp.departamento, emp.tipo_planilla, hrs_mostrar,
                emp.rata_hora, descontado,
                *vals_mes,
                salario_neto, salario_anual, isr,
                emp.status, "Sí" if emp.seguro_social else "No",
                sse, ssp, see, sep,
            ))
        self._actualizar_pos()

    def _filtrar(self) -> None:
        self._actualizar_tabla(self.e_busqueda.get())

    # ── Navegación tabla ──────────────────────────────────────────────────

    def _actualizar_pos(self) -> None:
        pass  # sidebar eliminado; reservado para uso futuro

    def _seleccionar_empleado(self, _event) -> None:
        sel = self.tabla.selection()
        if sel:
            emp = self.repo.buscar_empleado(sel[0])
            if emp:
                self._cargar_en_form(emp)

    # ── Formulario: carga / recogida / limpieza ───────────────────────────

    def _cargar_en_form(self, emp: Empleado) -> None:
        self._emp_editando = emp.codigo
        self._limpiar_form(limpiar_codigo=False)

        def _set(entry, val):
            entry.delete(0, "end")
            entry.insert(0, val or "")

        _set(self.e_nombre,   emp.nombre)
        _set(self.e_apellido, emp.apellido)
        _set(self.e_codigo,   emp.codigo)
        _set(self.e_cedula,   emp.cedula)
        _set(self.e_f_nac,    emp.fecha_nacimiento)
        _set(self.e_tel1,     emp.telefono1)
        _set(self.e_tel2,     emp.telefono2)
        _set(self.e_email,    emp.email)
        _set(self.e_dir,      emp.direccion)
        _set(self.e_f_inicio, emp.fecha_inicio)
        _set(self.e_f_term,   emp.fecha_terminacion)
        _set(self.e_cuenta,   emp.cuenta_banco)
        _set(self.e_salario, emp.salario)

        self.v_sexo.set(emp.sexo)
        self.v_estado_civil.set(emp.estado_civil)
        self.v_dpto.set(emp.departamento)
        self.v_tipo_planilla.set(emp.tipo_planilla)  # dispara _on_tipo_planilla_change
        self.v_status.set(emp.status)
        self.v_tipo_cuenta.set(emp.tipo_cuenta)
        self.v_horas_quincena.set(emp.horas_quincena)
        self.v_seguro.set(emp.seguro_social)
        self.v_empresa.set(getattr(emp, "empresa", "") or "")
        self.e_horas_personalizadas.delete(0, "end")
        self.e_horas_personalizadas.insert(0, getattr(emp, "horas_personalizadas", "") or "")

    def _recoger_form(self) -> Empleado:
        tipo_planilla = self.v_tipo_planilla.get()
        salario       = self.e_salario.get().strip()
        horas         = self.v_horas_quincena.get()
        horas_pers    = self.e_horas_personalizadas.get().strip()

        rata = self._calcular_rata(salario, horas, tipo_planilla)

        if tipo_planilla in ("Por Hora", "Temporal") and horas_pers:
            descontado = self._calcular_descontado(salario, horas, horas_pers, tipo_planilla)
        else:
            descontado = ""

        # Preservar horas_mes del empleado guardado para no perderlas al editar
        codigo_actual = self.e_codigo.get().strip()
        emp_existente = self.repo.buscar_empleado(codigo_actual) if codigo_actual else None
        horas_mes_guardadas = {
            f"horas_mes_{i}": getattr(emp_existente, f"horas_mes_{i}", "") or ""
            for i in range(1, 14)
        } if emp_existente else {}

        return Empleado(
            nombre=self.e_nombre.get().strip(),
            apellido=self.e_apellido.get().strip(),
            codigo=codigo_actual,
            fecha_nacimiento=self.e_f_nac.get().strip(),
            cedula=self.e_cedula.get().strip(),
            sexo=self.v_sexo.get(),
            estado_civil=self.v_estado_civil.get(),
            telefono1=self.e_tel1.get().strip(),
            telefono2=self.e_tel2.get().strip(),
            direccion=self.e_dir.get().strip(),
            email=self.e_email.get().strip(),
            fecha_inicio=self.e_f_inicio.get().strip(),
            fecha_terminacion=self.e_f_term.get().strip(),
            tipo_cuenta=self.v_tipo_cuenta.get(),
            cuenta_banco=self.e_cuenta.get().strip(),
            departamento=self.v_dpto.get(),
            tipo_planilla=tipo_planilla,
            status=self.v_status.get(),
            seguro_social=self.v_seguro.get(),
            salario=salario,
            horas_quincena=horas,
            rata_hora=rata,
            horas_personalizadas=horas_pers,
            descontado=descontado,
            empresa=self.v_empresa.get(),
            **horas_mes_guardadas,
        )

    def _limpiar_form(self, limpiar_codigo: bool = True) -> None:
        self._emp_editando = None
        entries = [self.e_nombre, self.e_apellido, self.e_cedula,
                   self.e_f_nac, self.e_tel1, self.e_tel2,
                   self.e_email, self.e_dir, self.e_f_inicio,
                   self.e_f_term, self.e_cuenta, self.e_salario,
                   self.e_horas_personalizadas]
        if limpiar_codigo:
            entries.append(self.e_codigo)
        for e in entries:
            e.delete(0, "end")
        for v in (self.v_sexo, self.v_estado_civil, self.v_dpto,
                  self.v_tipo_planilla, self.v_status, self.v_tipo_cuenta,
                  self.v_horas_quincena, self.v_empresa):
            v.set("")
        self.v_seguro.set(False)
        self._frame_horas_personalizadas.grid_remove()

    # ── Acciones ──────────────────────────────────────────────────────────

    def _refrescar_empresas(self) -> None:
        """Actualiza el dropdown de Empresa con las empresas guardadas."""
        nombres = [e.nombre for e in self.repo.listar_empresas()]
        self._cb_empresa.configure(values=nombres)
        if self.v_empresa.get() not in nombres:
            self.v_empresa.set("")

    def _abrir_ventana_horas_mes(self) -> None:
        """Abre ventana para ingresar horas trabajadas por mes (13 meses)."""
        # Usar datos del formulario actual (no requiere empleado guardado)
        codigo        = self.e_codigo.get().strip()
        nombre        = self.e_nombre.get().strip()
        apellido      = self.e_apellido.get().strip()
        salario       = self.e_salario.get().strip()
        horas_contrato = self.v_horas_quincena.get()
        tipo_planilla  = self.v_tipo_planilla.get()

        # Cargar valores guardados si el empleado ya existe
        emp_guardado = self.repo.buscar_empleado(codigo) if codigo else None
        nombre_display = f"{nombre} {apellido}".strip() or "Nuevo Empleado"

        win = tk.Toplevel(self)
        win.title(f"Horas Laboradas por Mes — {nombre_display}")
        win.configure(bg=COLORES["fondo"])
        win.resizable(False, False)
        win.grab_set()

        # Header
        header = tk.Frame(win, bg=COLORES["primario"], height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="📅  HORAS LABORADAS POR MES",
                 bg=COLORES["primario"], fg="white",
                 font=("Arial", 12, "bold")).pack(expand=True)

        frame = tk.Frame(win, bg=COLORES["fondo_frame"], padx=20, pady=16)
        frame.pack(fill="both", expand=True, padx=12, pady=10)

        NOMBRES_MES = [
            "1er Mes", "2do Mes", "3er Mes", "4to Mes", "5to Mes",
            "6to Mes", "7mo Mes", "8vo Mes", "9no Mes", "10mo Mes",
            "11mo Mes", "12mo Mes", "13er Mes",
        ]

        entradas = []
        for i, nombre_mes in enumerate(NOMBRES_MES):
            row = i // 2
            col = (i % 2) * 2
            tk.Label(frame, text=nombre_mes, bg=COLORES["fondo_frame"],
                     fg=COLORES["label"], font=("Arial", 9, "bold"),
                     anchor="w").grid(row=row*2, column=col, padx=(10, 4),
                                      pady=(6, 0), sticky="w")
            e = tk.Entry(frame, width=10, font=("Arial", 10),
                         relief="flat", bd=1, highlightthickness=1,
                         highlightbackground=COLORES["borde"],
                         highlightcolor=COLORES["secundario"])
            e.grid(row=row*2+1, column=col, padx=(10, 4), pady=(0, 4), sticky="ew")

            # Valor guardado si existe, si no el default del dropdown de horas
            if emp_guardado:
                val = getattr(emp_guardado, f"horas_mes_{i+1}", "") or horas_contrato
            else:
                val = horas_contrato
            e.insert(0, val)
            entradas.append(e)

        def _guardar_horas():
            # Si ya existe en repo, actualizarlo; si no, guardar en memoria del form
            if emp_guardado:
                emp = emp_guardado
            else:
                emp = self._recoger_form()
                if not emp.codigo:
                    messagebox.showwarning("Aviso",
                        "Ingresa al menos el código del empleado antes de guardar las horas.",
                        parent=win)
                    return
            for i, e in enumerate(entradas):
                setattr(emp, f"horas_mes_{i+1}", e.get().strip())
            self.repo.guardar_empleado(emp)
            self._actualizar_tabla()
            win.destroy()
            messagebox.showinfo("✅ Guardado", "Horas por mes guardadas.", parent=self)

        btn_frame = tk.Frame(win, bg=COLORES["fondo"])
        btn_frame.pack(pady=(0, 12))
        boton_primario(btn_frame, "💾  Guardar", _guardar_horas).pack(
            side="left", padx=6)
        boton_primario(btn_frame, "❌  Cancelar", win.destroy,
                       COLORES["peligro"]).pack(side="left", padx=6)

    def _calcular_ganado_mes(self, salario: str, horas_contrato: str,
                              horas_reales: str, tipo_planilla: str) -> float:
        """Ganado en un mes = salario - descuento por horas no trabajadas."""
        try:
            s  = float(salario)
            hc = int(horas_contrato)
            hr = int(horas_reales)
            if hc <= 0 or hr <= 0:
                return s  # sin horas ingresadas, salario completo

            def _rata(h: int) -> float:
                if h < 88:
                    return s / h
                elif h <= 104:
                    return s / (h * 2)
                else:
                    return s / h

            descuento = (hc - hr) * _rata(hc)
            return round(s - descuento, 2)
        except (ValueError, ZeroDivisionError):
            return 0.0

    def _on_tipo_planilla_change(self, *_) -> None:
        """Actualiza las opciones de Horas Laboradas según el tipo de planilla."""
        tipo = self.v_tipo_planilla.get()

        if tipo == "Semanal":
            opciones = ["40", "44", "48"]
        elif tipo == "Quincenal":
            opciones = ["104", "96", "88"]
        else:  # Mensual
            opciones = ["176", "192", "208"]

        self._cb_horas["values"] = opciones
        if self.v_horas_quincena.get() not in opciones:
            self.v_horas_quincena.set("")

    def _calcular_rata(self, salario: str, horas: str, tipo_planilla: str = "") -> str:
        """Rata/hora según el tipo de planilla y las horas del contrato."""
        try:
            s = float(salario)
            h = int(horas)
            if h <= 0:
                return ""
            if tipo_planilla == "Semanal":
                return f"{s / h:.2f}"
            elif tipo_planilla == "Mensual":
                return f"{s / h:.2f}"
            else:  # Quincenal (y fallback)
                return f"{s / (h * 2):.2f}"
        except (ValueError, ZeroDivisionError):
            return ""

    def _calcular_descontado(self, salario: str, horas_contrato: str,
                              horas_reales: str, tipo_planilla: str) -> str:
        """Descuento = (horas_contrato - horas_reales) × rata_hora_contrato."""
        try:
            s  = float(salario)
            hc = int(horas_contrato)
            hr = int(horas_reales)
            if hc <= 0 or hr <= 0:
                return ""

            def _rata(h: int) -> float:
                if h < 88:       # rango semanal
                    return s / h
                elif h <= 104:   # rango quincenal (incluye 88)
                    return s / (h * 2)
                else:            # rango mensual (176-208)
                    return s / h

            rata_hora  = _rata(hc)
            descuento  = (hc - hr) * rata_hora
            return f"{descuento:.2f}"
        except (ValueError, ZeroDivisionError):
            return ""

    def _guardar_empleado(self) -> None:
        emp = self._recoger_form()
        errores = emp.validar()
        if errores:
            messagebox.showerror("Validación", "\n".join(errores), parent=self)
            return
        self.repo.guardar_empleado(emp)
        self._actualizar_tabla()
        messagebox.showinfo("✅ Guardado",
                            f"Empleado {emp.nombre_completo()} guardado correctamente.",
                            parent=self)
        self._emp_editando = emp.codigo

    def _eliminar_empleado(self) -> None:
        codigo = self.e_codigo.get().strip()
        if not codigo:
            messagebox.showwarning("Aviso", "Selecciona un empleado primero.",
                                   parent=self)
            return
        if messagebox.askyesno("Confirmar",
                               f"¿Eliminar el empleado con código {codigo}?",
                               parent=self):
            self.repo.eliminar_empleado(codigo)
            self._actualizar_tabla()
            self._limpiar_form()
            messagebox.showinfo("Eliminado", "Empleado eliminado.", parent=self)

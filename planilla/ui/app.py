import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import asksaveasfilename
from datetime import date

from planilla.repository import Repositorio
from planilla.repository.exportador_excel import ExportadorExcel
from planilla.models import Empresa
from planilla.utils import COLORES
from planilla.ui.ventana_empresa import VentanaEmpresa
from planilla.ui.ventana_empleados import VentanaEmpleados
from planilla.ui.ventana_acreedores import VentanaAcreedores


class AplicacionPlanilla(tk.Tk):
    """Ventana principal del Sistema de Planilla."""

    def __init__(self):
        super().__init__()
        self.repo = Repositorio()
        self.exportador = ExportadorExcel()
        self.title("Sistema de Planilla LMC")
        self.configure(bg=COLORES["fondo"])
        self.resizable(False, False)
        self._centrar(520, 460)
        self._aplicar_estilos()
        self._construir()

    # ── Posicionamiento ───────────────────────────────────────────────────

    def _centrar(self, w: int, h: int) -> None:
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── Estilos globales ttk ──────────────────────────────────────────────

    def _aplicar_estilos(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview",
                        background=COLORES["fondo_frame"],
                        fieldbackground=COLORES["fondo_frame"],
                        foreground=COLORES["texto"],
                        rowheight=26, font=("Arial", 10))
        style.configure("Treeview.Heading",
                        background=COLORES["primario"],
                        foreground="white",
                        font=("Arial", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", COLORES["secundario"])],
                  foreground=[("selected", "white")])
        style.configure("TCombobox", font=("Arial", 10))

    # ── Construcción de la UI ─────────────────────────────────────────────

    def _construir(self) -> None:
        # Encabezado limpio — sin nombre de empresa
        header = tk.Frame(self, bg=COLORES["primario"], height=90)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="📋  SISTEMA DE PLANILLA \n LEON MORA & CO.",
            bg=COLORES["primario"], fg="white",
            font=("Arial", 20, "bold"),
        ).pack(expand=True)

        # Botones de menú
        btn_area = tk.Frame(self, bg=COLORES["fondo"])
        btn_area.pack(expand=True, fill="both", padx=40, pady=30)

        self._boton_menu(
            btn_area, "🏢  Empresa",
            "Registrar datos de la empresa",
            self._abrir_empresa, COLORES["primario"],
        ).pack(fill="x", pady=6)

        self._boton_menu(
            btn_area, "👥  Empleados",
            "Gestionar empleados de la planilla",
            self._abrir_empleados, COLORES["secundario"],
        ).pack(fill="x", pady=6)

        self._boton_menu(
            btn_area, "🏦  Acreedores",
            "Gestionar acreedores y formas de pago",
            self._abrir_acreedores, "#6C3483",
        ).pack(fill="x", pady=6)

        self._boton_menu(
            btn_area, "📊  Exportar a Excel",
            "Generar planilla en formato .xlsx",
            self._exportar, "#1E8449",
        ).pack(fill="x", pady=6)

        # Footer
        tk.Label(
            self, text=f"v1.0  ·  {date.today().year}",
            bg=COLORES["fondo"], fg=COLORES["borde"],
            font=("Arial", 8),
        ).pack(pady=8)

    def _boton_menu(self, parent, titulo: str, subtitulo: str,
                    comando, color: str) -> tk.Frame:
        frame = tk.Frame(parent, bg=color, cursor="hand2")
        frame.bind("<Button-1>", lambda e: comando())
        tk.Label(frame, text=titulo, bg=color, fg="white",
                 font=("Arial", 12, "bold"), anchor="w").pack(
            side="left", padx=16, pady=8)
        tk.Label(frame, text=subtitulo, bg=color, fg="#D6EAF8",
                 font=("Arial", 9), anchor="e").pack(side="right", padx=16)
        for child in frame.winfo_children():
            child.bind("<Button-1>", lambda e: comando())
        return frame

    # ── Acciones del menú ─────────────────────────────────────────────────

    def _abrir_empresa(self) -> None:
        win = VentanaEmpresa(self, self.repo)
        win.grab_set()
        self.wait_window(win)

    def _abrir_empleados(self) -> None:
        win = VentanaEmpleados(self, self.repo)
        win.grab_set()
        self.wait_window(win)

    def _abrir_acreedores(self) -> None:
        win = VentanaAcreedores(self, self.repo)
        win.grab_set()
        self.wait_window(win)

    def _exportar(self) -> None:
        ruta = asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
            initialfile="planilla_exportada.xlsx",
            title="Guardar planilla como...",
        )
        if not ruta:
            return
        try:
            empresas = self.repo.listar_empresas()
            empresa = empresas[0] if empresas else Empresa()
            empleados = self.repo.listar_empleados()
            self.exportador.exportar(ruta, empresa, empleados)
            messagebox.showinfo("✅ Exportado",
                                f"Planilla exportada exitosamente:\n{ruta}")
        except Exception as ex:
            messagebox.showerror("Error", f"No se pudo exportar:\n{ex}")

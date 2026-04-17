import json
import os

from planilla.models import Empresa, Empleado, Acreedor


class Repositorio:
    """Gestiona la persistencia de datos en un archivo JSON local."""

    ARCHIVO = "planilla_datos.json"

    def __init__(self, archivo: str = None):
        self._archivo = archivo or self.ARCHIVO
        self._datos: dict = {"empresas": [], "empleados": [], "acreedores": []}
        self._cargar()

    # ── Persistencia interna ──────────────────────────────────────────────

    def _cargar(self) -> None:
        if os.path.exists(self._archivo):
            with open(self._archivo, "r", encoding="utf-8") as f:
                self._datos = json.load(f)
        # Migración: empresa única heredada → lista
        if "empresa" in self._datos and "empresas" not in self._datos:
            legacy = self._datos.pop("empresa")
            self._datos["empresas"] = [legacy] if legacy.get("nombre") else []
        self._datos.setdefault("empresas", [])
        self._datos.setdefault("empleados", [])
        self._datos.setdefault("acreedores", [])

    def _guardar(self) -> None:
        with open(self._archivo, "w", encoding="utf-8") as f:
            json.dump(self._datos, f, ensure_ascii=False, indent=2)

    # ── Empresas ──────────────────────────────────────────────────────────

    def guardar_empresa(self, empresa: Empresa) -> None:
        lista = self._datos["empresas"]
        for i, e in enumerate(lista):
            if e.get("id") == empresa.id:
                lista[i] = empresa.to_dict()
                self._guardar()
                return
        lista.append(empresa.to_dict())
        self._guardar()

    def eliminar_empresa(self, id: str) -> None:
        self._datos["empresas"] = [
            e for e in self._datos["empresas"] if e.get("id") != id
        ]
        self._guardar()

    def listar_empresas(self) -> list[Empresa]:
        return [Empresa.from_dict(e) for e in self._datos["empresas"]]

    def buscar_empresa(self, id: str) -> Empresa | None:
        for e in self._datos["empresas"]:
            if e.get("id") == id:
                return Empresa.from_dict(e)
        return None

    # ── Empleados ─────────────────────────────────────────────────────────

    def guardar_empleado(self, empleado: Empleado) -> None:
        lista = self._datos["empleados"]
        for i, e in enumerate(lista):
            if e.get("codigo") == empleado.codigo:
                lista[i] = empleado.to_dict()
                self._guardar()
                return
        lista.append(empleado.to_dict())
        self._guardar()

    def eliminar_empleado(self, codigo: str) -> None:
        self._datos["empleados"] = [
            e for e in self._datos["empleados"] if e.get("codigo") != codigo
        ]
        self._guardar()

    def listar_empleados(self) -> list[Empleado]:
        return [Empleado.from_dict(e) for e in self._datos["empleados"]]

    def buscar_empleado(self, codigo: str) -> Empleado | None:
        for e in self._datos["empleados"]:
            if e.get("codigo") == codigo:
                return Empleado.from_dict(e)
        return None

    # ── Acreedores ────────────────────────────────────────────────────────

    def guardar_acreedor(self, acreedor: Acreedor) -> None:
        lista = self._datos["acreedores"]
        for i, a in enumerate(lista):
            if a.get("numero_acreedor") == acreedor.numero_acreedor:
                lista[i] = acreedor.to_dict()
                self._guardar()
                return
        lista.append(acreedor.to_dict())
        self._guardar()

    def eliminar_acreedor(self, numero: str) -> None:
        self._datos["acreedores"] = [
            a for a in self._datos["acreedores"]
            if a.get("numero_acreedor") != numero
        ]
        self._guardar()

    def listar_acreedores(self) -> list[Acreedor]:
        return [Acreedor.from_dict(a) for a in self._datos["acreedores"]]

    def buscar_acreedor(self, numero: str) -> Acreedor | None:
        for a in self._datos["acreedores"]:
            if a.get("numero_acreedor") == numero:
                return Acreedor.from_dict(a)
        return None

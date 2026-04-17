import re
import uuid


class Empresa:
    """Modelo de datos para una empresa (soporta múltiples registros)."""

    def __init__(self, nombre="", ruc="", dv="", direccion="",
                 telefono1="", telefono2="", email="",
                 correlativo="", fecha_apertura="", fecha_expiracion="",
                 id: str = None):
        self.id               = id or str(uuid.uuid4())[:8].upper()
        self.nombre           = nombre
        self.ruc              = ruc
        self.dv               = dv
        self.direccion        = direccion
        self.telefono1        = telefono1
        self.telefono2        = telefono2
        self.email            = email
        self.correlativo      = correlativo
        self.fecha_apertura   = fecha_apertura
        self.fecha_expiracion = fecha_expiracion

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, d: dict) -> "Empresa":
        known = {"nombre", "ruc", "dv", "direccion", "telefono1", "telefono2",
                 "email", "correlativo", "fecha_apertura", "fecha_expiracion", "id"}
        return cls(**{k: v for k, v in d.items() if k in known})

    def validar(self) -> list[str]:
        errores = []
        if not self.nombre.strip():
            errores.append("El nombre de la empresa es obligatorio.")
        if not self.ruc.strip():
            errores.append("El RUC es obligatorio.")
        if self.email and not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            errores.append("El email no tiene un formato válido.")
        return errores

    def __repr__(self) -> str:
        return f"<Empresa id={self.id!r} nombre={self.nombre!r} ruc={self.ruc!r}>"

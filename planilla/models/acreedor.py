import re


class Acreedor:
    """Modelo de datos para un acreedor."""

    def __init__(self, nombre="", numero_acreedor="", concepto="",
                 prioridad="", ahorro="", telefono="", direccion="",
                 observacion="", forma_pago="", tipo_cuenta="",
                 status="Activo", ruc="", dv="", banco_pagador=""):
        self.nombre           = nombre
        self.numero_acreedor  = numero_acreedor
        self.concepto         = concepto
        self.prioridad        = prioridad        # numérico, guardado como str
        self.ahorro           = ahorro           # "Sí" | "No"
        self.telefono         = telefono
        self.direccion        = direccion
        self.observacion      = observacion
        self.forma_pago       = forma_pago
        self.tipo_cuenta      = tipo_cuenta
        self.status           = status
        self.ruc              = ruc
        self.dv               = dv
        self.banco_pagador    = banco_pagador

    # ── Serialización ─────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, d: dict) -> "Acreedor":
        obj = cls()
        for k, v in d.items():
            setattr(obj, k, v)
        return obj

    # ── Validación ────────────────────────────────────────────────────────

    def validar(self) -> list[str]:
        errores = []
        if not self.nombre.strip():
            errores.append("El nombre del acreedor es obligatorio.")
        if not self.numero_acreedor.strip():
            errores.append("El número de acreedor es obligatorio.")
        if self.prioridad and not self.prioridad.strip().isdigit():
            errores.append("La prioridad debe ser un valor numérico entero.")
        return errores

    def __repr__(self) -> str:
        return f"<Acreedor numero={self.numero_acreedor!r} nombre={self.nombre!r}>"

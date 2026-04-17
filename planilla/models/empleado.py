import re


class Empleado:
    """Modelo de datos para un empleado."""

    def __init__(self, nombre="", apellido="", codigo="",
                 fecha_nacimiento="", cedula="", sexo="",
                 estado_civil="", telefono1="", telefono2="",
                 direccion="", email="", fecha_inicio="",
                 fecha_terminacion="", tipo_cuenta="", cuenta_banco="",
                 salario="", departamento="", tipo_planilla="", status="",
                 horas_quincena="", rata_hora="", seguro_social=False,
                 horas_personalizadas="", descontado="", empresa="",
                 **horas_mes):
        # horas_mes_1 … horas_mes_13  (recibidos como kwargs para compatibilidad JSON)
        for i in range(1, 14):
            key = f"horas_mes_{i}"
            setattr(self, key, horas_mes.get(key, ""))
        self.nombre = nombre
        self.apellido = apellido
        self.codigo = codigo
        self.fecha_nacimiento = fecha_nacimiento
        self.cedula = cedula
        self.sexo = sexo
        self.estado_civil = estado_civil
        self.telefono1 = telefono1
        self.telefono2 = telefono2
        self.direccion = direccion
        self.email = email
        self.fecha_inicio = fecha_inicio
        self.fecha_terminacion = fecha_terminacion
        self.tipo_cuenta = tipo_cuenta
        self.cuenta_banco = cuenta_banco
        self.salario = salario
        self.departamento = departamento
        self.tipo_planilla = tipo_planilla
        self.status = status
        self.horas_quincena = horas_quincena
        self.rata_hora = rata_hora
        self.seguro_social = seguro_social
        self.horas_personalizadas = horas_personalizadas
        self.descontado = descontado
        self.empresa = empresa
        # horas_mes_1 … horas_mes_13 already set above via **horas_mes

    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}".strip()

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, d: dict) -> "Empleado":
        known = {k: v for k, v in d.items() if not k.startswith("horas_mes_")}
        horas_mes = {k: v for k, v in d.items() if k.startswith("horas_mes_")}
        obj = cls(**{**known, **horas_mes})
        return obj

    def validar(self) -> list[str]:
        errores = []
        if not self.nombre.strip():
            errores.append("El nombre es obligatorio.")
        if not self.apellido.strip():
            errores.append("El apellido es obligatorio.")
        if not self.cedula.strip():
            errores.append("La cédula es obligatoria.")
        if not self.codigo.strip():
            errores.append("El código de empleado es obligatorio.")
        if self.email and not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            errores.append("El email no tiene formato válido.")
        return errores

    def __repr__(self) -> str:
        return f"<Empleado codigo={self.codigo!r} nombre={self.nombre_completo()!r}>"

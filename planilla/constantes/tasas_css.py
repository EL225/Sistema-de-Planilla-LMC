from datetime import date

TASA_EMPLEADO         = 0.0975
TASA_PATRONAL_NUEVA   = 0.1325   # desde 2025-05-01
TASA_PATRONAL_ANTIGUA = 0.1225
FECHA_CAMBIO_PATRONAL = date(2025, 5, 1)

TASA_SEE = 0.0125   # Seguro Educativo Empleado
TASA_SEP = 0.0150   # Seguro Educativo Patronal


def calcular_css(salario_bruto: float, fecha_periodo: date) -> dict:
    """Calcula las cuotas de la Caja de Seguro Social (CSS) y Seguro Educativo.

    Args:
        salario_bruto: Salario bruto del empleado (debe ser > 0).
        fecha_periodo: Fecha del período de pago para determinar la tasa patronal.

    Returns:
        Diccionario con claves ``"empleado"``, ``"patronal"``, ``"see"`` y ``"sep"``.
    """
    if salario_bruto <= 0:
        return {"empleado": 0.0, "patronal": 0.0, "see": 0.0, "sep": 0.0}

    tasa_patronal = (
        TASA_PATRONAL_NUEVA
        if fecha_periodo >= FECHA_CAMBIO_PATRONAL
        else TASA_PATRONAL_ANTIGUA
    )
    return {
        "empleado": round(salario_bruto * TASA_EMPLEADO, 2),
        "patronal": round(salario_bruto * tasa_patronal, 2),
        "see":      round(salario_bruto * TASA_SEE, 2),
        "sep":      round(salario_bruto * TASA_SEP, 2),
    }

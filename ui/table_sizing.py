"""Reparto de columnas sin depender de Qt (medidas en píxeles lógicos)."""


def fit_column_widths(preferred, minimum, available, weights=None):
    """Ajusta columnas al viewport, manteniendo los mínimos de acciones/cabeceras.

    Si ni siquiera caben los mínimos, conserva esos mínimos y permite scroll;
    nunca oculta acciones para simular que una tabla cabe.
    """
    if len(preferred) != len(minimum):
        raise ValueError("Se requiere un mínimo por columna")
    if not preferred:
        return []
    minimum = [max(1, int(value)) for value in minimum]
    preferred = [max(low, int(value)) for low, value in zip(minimum, preferred)]
    available = max(0, int(available))
    if available <= sum(minimum):
        return minimum
    if sum(preferred) > available:
        slack = [high - low for high, low in zip(preferred, minimum)]
        extra = available - sum(minimum)
        total = sum(slack)
        result = [low + extra * room // total for low, room in zip(minimum, slack)]
        order = sorted(range(len(result)), key=lambda i: slack[i], reverse=True)
    else:
        result = preferred[:]
        weights = list(weights) if weights is not None else [1] * len(result)
        if len(weights) != len(result) or any(value < 0 for value in weights):
            raise ValueError("Pesos de columna inválidos")
        if not sum(weights):
            return result
        extra = available - sum(result)
        total = sum(weights)
        result = [width + extra * weight // total for width, weight in zip(result, weights)]
        order = sorted(range(len(result)), key=lambda i: weights[i], reverse=True)
    for index in order[:available - sum(result)]:
        result[index] += 1
    return result

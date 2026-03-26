"""
construir_esperado.py
---------------------
Genera fact_esperado: tabla con las ejecuciones ESPERADAS por mes.

Lógica:
  - Un cliente debería ejecutar 1 vez por mes cada herramienta
    donde Usa Herramienta = True en el Relevamiento.
  - Se cruzan los meses reales del período de DB_Server con
    la lista de cliente × herramienta del Relevamiento.

Output: una fila por (cuit, herramienta, anio, mes) esperada.
En Power BI se compara con fact_ejecuciones para ver Real vs Esperado.
"""

import pandas as pd


def construir_esperado(
    dim_relevamiento: pd.DataFrame,
    fact: pd.DataFrame,
) -> pd.DataFrame:
    """
    Parameters
    ----------
    dim_relevamiento : salida de leer_relevamiento()
    fact             : salida de construir_fact_ejecuciones()

    Returns
    -------
    fact_esperado : DataFrame con columnas:
        cuit, nombre_cliente, herramienta, anio, mes, ejecuciones_esperadas
    """

    # Solo herramientas que el cliente DEBE usar
    debe_usar = dim_relevamiento[
        dim_relevamiento["usa_herramienta"] == True
    ][["cuit", "nombre_cliente", "herramienta"]].copy()

    # Período real de los datos (meses que existen en fact)
    periodos = (
        fact[fact["anio"].notna() & fact["mes"].notna()]
        [["anio", "mes"]]
        .drop_duplicates()
        .sort_values(["anio", "mes"])
        .reset_index(drop=True)
    )
    periodos["anio"] = periodos["anio"].astype(int)
    periodos["mes"]  = periodos["mes"].astype(int)

    # Cross join: cada combinación cliente×herramienta × cada mes del período
    debe_usar["_key"] = 1
    periodos["_key"]  = 1

    fact_esperado = debe_usar.merge(periodos, on="_key").drop(columns=["_key"])
    fact_esperado["ejecuciones_esperadas"] = 1  # 1 por mes

    print(f"  → fact_esperado: {len(fact_esperado):,} filas "
          f"({len(debe_usar):,} combinaciones × {len(periodos):,} meses)")

    return fact_esperado[[
        "cuit", "nombre_cliente", "herramienta",
        "anio", "mes", "ejecuciones_esperadas"
    ]].reset_index(drop=True)
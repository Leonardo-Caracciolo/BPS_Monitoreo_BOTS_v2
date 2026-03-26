import pandas as pd

from settings import PROCESO_A_HERRAMIENTA, PROCESOS_SIN_HERRAMIENTA


_ESTADO_MAP = {
    "correcto":                              "Correcto",
    "erróneo":                               "Erroneo",
    "erroneo":                               "Erroneo",
    "proceso terminado con errores":         "Erroneo",
    "proceso finalizado con errores":        "Erroneo",
    "finalizado con observaciones":          "Con Observaciones",
    "proceso terminado con observaciones":   "Con Observaciones",
    "proceso finalizado con observaciones":  "Con Observaciones",
    "correo no enviado":                     "Correo no enviado",
    "finalizado":                            "Correcto",
    "0":                                     "Erroneo",
}


def construir_fact_ejecuciones(
    df_db: pd.DataFrame,
    dim_clientes: pd.DataFrame,
) -> pd.DataFrame:
    """
    Construye la tabla de hechos principal combinando df_db con dim_clientes.

    Aplica:
      - Mapeo proceso_original → herramienta canónica
      - Flag en_relevamiento
      - Normalización de estado
      - Join con dim_clientes por CUIT para traer nombre y gerente

    Parameters
    ----------
    df_db         : salida de leer_db_server()
    dim_clientes  : salida de leer_relevamiento()

    Returns
    -------
    fact_ejecuciones : DataFrame con 19 columnas listas para Power BI
    """
    df = df_db.copy()

    # Mapeo proceso → herramienta
    df["herramienta"] = df["proceso_original"].str.strip().map(PROCESO_A_HERRAMIENTA)
    sin_mapeo = df["herramienta"].isna()
    df.loc[sin_mapeo, "herramienta"] = df.loc[sin_mapeo, "proceso_original"].str.strip()

    # Flag en_relevamiento
    df["en_relevamiento"] = ~df["proceso_original"].str.strip().isin(PROCESOS_SIN_HERRAMIENTA)

    # Normalizar estado
    df["estado_normalizado"] = (
        df["estado"].astype(str).str.strip().str.lower()
        .map(_ESTADO_MAP)
        .fillna(df["estado"].astype(str).str.strip())
    )

    # Join con dim_clientes por CUIT
    lookup = (
        dim_clientes[["cuit", "nombre_cliente", "gerente_responsable"]]
        .drop_duplicates(subset=["cuit"])
        .set_index("cuit")
    )
    df["nombre_cliente_canonico"] = df["cuit_cliente"].map(lookup["nombre_cliente"])
    df["gerente_responsable"]     = df["cuit_cliente"].map(lookup["gerente_responsable"])

    # Si no tiene CUIT pero tiene nombre de texto → usarlo como display
    sin_nombre = df["nombre_cliente_canonico"].isna()
    df.loc[sin_nombre, "nombre_cliente_canonico"] = df.loc[sin_nombre, "cliente_nombre"]

    return df[[
        "id", "username", "proceso_original", "herramienta", "en_relevamiento",
        "estado", "estado_normalizado",
        "iniciado", "finalizado", "duracion_segundos",
        "tipo_cliente", "cuit_cliente", "nombre_cliente_canonico", "gerente_responsable",
        "items_count", "observaciones",
        "anio", "mes", "semana",
    ]].reset_index(drop=True)
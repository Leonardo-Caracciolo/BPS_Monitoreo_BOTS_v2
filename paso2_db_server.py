import re
import pandas as pd
from pathlib import Path

from clean_datos import clean_datos
from settings import CLIENTE_VARIANTES


_CUIT_RE = re.compile(r"^\d{10,11}$")


def _clasificar_cliente(valor) -> str:
    """Clasifica el campo cliente en: CUIT / NOMBRE / VACIO."""
    if pd.isna(valor):
        return "VACIO"
    s = str(valor).strip()
    if not s or s.lower() in ("no definido", "nan", ""):
        return "VACIO"
    if _CUIT_RE.match(s):
        return "CUIT"
    return "NOMBRE"


def _limpiar_cuit(valor) -> str:
    if pd.isna(valor):
        return ""
    return str(valor).replace("-", "").replace(" ", "").strip()


def _duracion_segundos(iniciado: pd.Series, finalizado: pd.Series) -> pd.Series:
    i = pd.to_datetime(iniciado,  errors="coerce")
    f = pd.to_datetime(finalizado, errors="coerce")
    return (f - i).dt.total_seconds().clip(lower=0)


def leer_db_server(path_db: Path, path_tabla_cuits: Path) -> pd.DataFrame:
    """
    Usa clean_datos() como base y agrega:
      - Normalización de variantes de cliente (CLIENTE_VARIANTES)
      - Clasificación: CUIT / NOMBRE / VACIO
      - Lookup CUIT para registros con nombre (via Tabla_Cuits.xlsx)
      - Cálculo de duracion_segundos, anio, mes, semana

    Returns
    -------
    DataFrame con 30.881 filas y columnas clasificadas y enriquecidas.
    """
    # Base: función del usuario (lee y limpia strings)
    df = clean_datos(str(path_db))

    # Lookup nombre → CUIT via Tabla_Cuits
    df_cuits = pd.read_excel(path_tabla_cuits)
    df_cuits.columns = df_cuits.columns.str.strip()
    df_cuits["_key"] = df_cuits["razon_social"].astype(str).str.upper().str.strip()
    df_cuits["_rfc"] = df_cuits["RFC"].apply(_limpiar_cuit)
    lookup_cuit: dict = (
        df_cuits[df_cuits["_rfc"].str.len() > 0]
        .drop_duplicates(subset=["_key"])
        .set_index("_key")["_rfc"]
        .to_dict()
    )

    # Normalizar variantes de nombre de cliente
    df["cliente_norm"] = df["cliente"].apply(
        lambda v: CLIENTE_VARIANTES.get(str(v).strip(), str(v).strip())
        if not pd.isna(v) else v
    )

    # Clasificar
    df["tipo_cliente"]   = df["cliente_norm"].apply(_clasificar_cliente)
    df["cuit_cliente"]   = ""
    df["cliente_nombre"] = ""

    mask_cuit   = df["tipo_cliente"] == "CUIT"
    mask_nombre = df["tipo_cliente"] == "NOMBRE"

    df.loc[mask_cuit,   "cuit_cliente"]   = df.loc[mask_cuit,   "cliente_norm"].astype(str).str.strip()
    df.loc[mask_nombre, "cliente_nombre"] = df.loc[mask_nombre, "cliente_norm"].astype(str).str.strip()
    df.loc[mask_nombre, "cuit_cliente"]   = (
        df.loc[mask_nombre, "cliente_norm"]
        .astype(str).str.upper().str.strip()
        .map(lookup_cuit).fillna("")
    )

    # Campos temporales
    df["iniciado"]          = pd.to_datetime(df["iniciado"],   errors="coerce")
    df["finalizado"]        = pd.to_datetime(df["finalizado"], errors="coerce")
    df["duracion_segundos"] = _duracion_segundos(df["iniciado"], df["finalizado"])
    
    #Se reemplaza astype(int) por astype("Int64") para permitir valores nulos (NaN) en las columnas de año, mes y semana.
    df["anio"]   = df["iniciado"].dt.year.fillna(0).astype("Int64")
    df["mes"]    = df["iniciado"].dt.month.fillna(0).astype("Int64")
    df["semana"] = df["iniciado"].dt.isocalendar().week.fillna(0).astype("Int64")

    df.rename(columns={"proceso": "proceso_original"}, inplace=True)

    return df[[
        "id", "username", "proceso_original", "estado",
        "iniciado", "finalizado", "duracion_segundos",
        "tipo_cliente", "cuit_cliente", "cliente_nombre",
        "items_count", "observaciones",
        "anio", "mes", "semana",
    ]].reset_index(drop=True)
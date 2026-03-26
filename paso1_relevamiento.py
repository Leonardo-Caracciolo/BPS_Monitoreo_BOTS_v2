import pandas as pd
from pathlib import Path

from merge_datos import merge_datos


def _limpiar_cuit(valor) -> str:
    """Quita guiones y espacios. Ej: '30-71757936-0' → '30717579360'"""
    if pd.isna(valor):
        return ""
    return str(valor).replace("-", "").replace(" ", "").strip()


def _es_cuit_dummy(cuit: str) -> bool:
    """True si el CUIT es un placeholder tipo 00000000001."""
    return bool(cuit) and int(cuit) < 100 if cuit.isdigit() else False


def leer_relevamiento(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Usa merge_datos() como base y agrega:
      - Limpieza de CUITs (quita guiones)
      - Detección de CUITs dummy
      - Normalización de nombres de herramienta
      - Deduplicación de dim_clientes por CUIT (requerido por Power BI)
      - Conversión Usa Herramienta → bool

    Returns
    -------
    dim_clientes     : 1 fila por CUIT único
    dim_relevamiento : 1 fila por cliente × herramienta
    """
    
    df_clientes, df_herramientas = merge_datos(str(path))

    # Normalizar columnas
    df_clientes.columns     = df_clientes.columns.str.strip()
    df_herramientas.columns = df_herramientas.columns.str.strip()

    # Enriquecer df_clientes
    df_clientes["cuit"]                = df_clientes["Cuit"].apply(_limpiar_cuit)
    df_clientes["cuit_es_dummy"]       = df_clientes["cuit"].apply(_es_cuit_dummy)
    df_clientes["nombre_cliente"]      = df_clientes["Cliente"].astype(str).str.strip()
    df_clientes["gerente_responsable"] = df_clientes["Gerente responsable"].astype(str).str.strip()

    # dim_clientes: deduplicar por CUIT (Power BI requiere PK sin duplicados)
    dim_clientes = (
        df_clientes[["ID_Cliente", "cuit", "nombre_cliente", "gerente_responsable", "cuit_es_dummy"]]
        .drop_duplicates(subset=["ID_Cliente"])
        .drop_duplicates(subset=["cuit"], keep="first")
        .reset_index(drop=True)
    )

    # Normalizar herramienta (colapsa espacios dobles)
    df_herramientas["herramienta"] = (
        df_herramientas["Herramienta"].astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    # Usa Herramienta → bool
    df_herramientas["usa_herramienta"] = (
        df_herramientas["Usa Herramienta"]
        .astype(str).str.strip().str.upper()
        .map({"SI": True, "NO": False})
        .fillna(False)
    )

    df_herramientas["nombre_cliente"]      = df_herramientas["Cliente"].astype(str).str.strip()
    df_herramientas["gerente_responsable"] = df_herramientas["Gerente responsable"].astype(str).str.strip()
    df_herramientas["cuit"]                = df_herramientas["Cuit"].apply(_limpiar_cuit)

    dim_relevamiento = df_herramientas[[
        "ID_Cliente", "cuit", "nombre_cliente", "herramienta",
        "usa_herramienta", "gerente_responsable"
    ]].reset_index(drop=True)

    return dim_clientes, dim_relevamiento
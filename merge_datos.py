import pandas as pd


def merge_datos(file_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Lee Relevamiento BPS .xlsm y agrega la columna Cuit
    a la sheet "Uso de herramientas" via join por ID_Cliente.

    Parameters
    ----------
    file_path : str
        Ruta al archivo .xlsm del Relevamiento.

    Returns
    -------
    df_clientes     : DataFrame  (sheet Clientes)
    df_herramientas : DataFrame  (sheet Uso de herramientas + columna Cuit)
    """
    df_clientes     = pd.read_excel(file_path, sheet_name="Clientes",           engine="openpyxl")
    df_herramientas = pd.read_excel(file_path, sheet_name="Uso de herramientas", engine="openpyxl")

    print(f"  merge_datos: Clientes={len(df_clientes)} filas, Uso herramientas={len(df_herramientas)} filas")

    # Si Cuit ya existe en df_herramientas la eliminamos antes del merge
    if "Cuit" in df_herramientas.columns:
        df_herramientas = df_herramientas.drop(columns=["Cuit"])

    df_herramientas = df_herramientas.merge(
        df_clientes[["ID_Cliente", "Cuit"]],
        on="ID_Cliente",
        how="left"
    )

    return df_clientes, df_herramientas
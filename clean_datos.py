import pandas as pd


def clean_datos(file_path: str) -> pd.DataFrame:
    """
    Lee DB_Server.xlsx y limpia strings (strip + colapsa espacios).

    Parameters
    ----------
    file_path : str
        Ruta al archivo DB_Server.xlsx

    Returns
    -------
    pd.DataFrame con sheet "Tabla Monitoreos" limpia.
    """
    df_server = pd.read_excel(file_path, sheet_name="Tabla Monitoreos", engine="openpyxl")
    df_server = df_server.apply(
        lambda col: col.str.strip().str.replace(r"\s+", " ", regex=True)
        if col.dtype == "object" else col
    )
    print(f"  clean_datos: {len(df_server):,} filas leídas")
    return df_server



#! Eliminar a nosotros como usuarios (leo, dani, etc)
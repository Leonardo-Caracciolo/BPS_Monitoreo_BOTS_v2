import pandas as pd
from pathlib import Path
from datetime import datetime


def generar_diagnostico(
    fact: pd.DataFrame,
    dim_clientes: pd.DataFrame,
    dim_relevamiento: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Genera un Excel con 7 hojas de diagnóstico de calidad de datos.

    Sheets:
      - resumen_general
      - cobertura_tipo_cliente
      - procesos_sin_cliente
      - procesos_sin_relevam
      - top_clientes
      - top_procesos
      - errores_por_proceso
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ts    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = len(fact)
    ok    = (fact["estado_normalizado"] == "Correcto").sum()
    err   = (fact["estado_normalizado"] == "Erroneo").sum()
    vacios = (fact["tipo_cliente"] == "VACIO").sum()
    con_cuit = (fact["cuit_cliente"] != "").sum()

    resumen = pd.DataFrame([
        ["Generado el",                     ts],
        ["Total ejecuciones",               total],
        ["Con CUIT resuelto",               con_cuit],
        ["Con CUIT resuelto (%)",           f"{con_cuit/total*100:.1f}%"],
        ["Sin cliente (vacío)",             vacios],
        ["Sin cliente (%)",                 f"{vacios/total*100:.1f}%"],
        ["Estado Correcto",                 ok],
        ["Estado Correcto (%)",             f"{ok/total*100:.1f}%"],
        ["Estado Erróneo",                  err],
        ["Estado Erróneo (%)",              f"{err/total*100:.1f}%"],
        ["Clientes únicos (Relevamiento)",  dim_clientes["nombre_cliente"].nunique()],
        ["Herramientas únicas",             dim_relevamiento["herramienta"].nunique()],
    ], columns=["Métrica", "Valor"])

    cobertura = (
        fact.groupby("tipo_cliente").size()
        .reset_index(name="ejecuciones")
    )
    cobertura["porcentaje"] = (cobertura["ejecuciones"] / total * 100).round(1)

    sin_cliente = (
        fact[fact["tipo_cliente"] == "VACIO"]
        .groupby("proceso_original").size()
        .reset_index(name="ejecuciones")
        .sort_values("ejecuciones", ascending=False)
    )

    sin_herram = (
        fact[~fact["en_relevamiento"]]
        .groupby(["proceso_original", "herramienta"])
        .size().reset_index(name="ejecuciones")
        .sort_values("ejecuciones", ascending=False)
    )

    top_clientes = (
        fact[fact["nombre_cliente_canonico"].notna() & (fact["nombre_cliente_canonico"] != "")]
        .groupby("nombre_cliente_canonico")
        .agg(
            ejecuciones=("id", "count"),
            correctas=("estado_normalizado", lambda x: (x == "Correcto").sum()),
            erroneas=("estado_normalizado",  lambda x: (x == "Erroneo").sum()),
        )
        .reset_index()
        .sort_values("ejecuciones", ascending=False)
        .head(50)
    )
    top_clientes["tasa_exito_%"] = (
        top_clientes["correctas"] / top_clientes["ejecuciones"] * 100
    ).round(1)

    top_procesos = (
        fact.groupby(["proceso_original", "herramienta", "en_relevamiento"])
        .agg(
            ejecuciones=("id", "count"),
            correctas=("estado_normalizado", lambda x: (x == "Correcto").sum()),
            erroneas=("estado_normalizado",  lambda x: (x == "Erroneo").sum()),
        )
        .reset_index()
        .sort_values("ejecuciones", ascending=False)
    )
    top_procesos["tasa_exito_%"] = (
        top_procesos["correctas"] / top_procesos["ejecuciones"] * 100
    ).round(1)

    errores_df = (
        fact[fact["estado_normalizado"] == "Erroneo"]
        .groupby(["proceso_original", "nombre_cliente_canonico"])
        .size().reset_index(name="errores")
        .sort_values("errores", ascending=False)
    )

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        resumen.to_excel(writer,      sheet_name="resumen_general",        index=False)
        cobertura.to_excel(writer,    sheet_name="cobertura_tipo_cliente", index=False)
        sin_cliente.to_excel(writer,  sheet_name="procesos_sin_cliente",   index=False)
        sin_herram.to_excel(writer,   sheet_name="procesos_sin_relevam",   index=False)
        top_clientes.to_excel(writer, sheet_name="top_clientes",           index=False)
        top_procesos.to_excel(writer, sheet_name="top_procesos",           index=False)
        errores_df.to_excel(writer,   sheet_name="errores_por_proceso",    index=False)

    print(f"  📋 Diagnóstico generado: {output_path}")
#!Agregado de fact_esperado
"""
main.py
-------
Entry point del pipeline BPS Monitoreo Bots.

Ejecutar:
    python main.py                  ← usa el Excel que ya existe en data/inputs/
    python main.py --fetch          ← descarga datos frescos de SQL Server primero (requiere VPN)

Produce en data/outputs/:
    dim_clientes.csv
    dim_herramientas.csv
    dim_relevamiento.csv
    fact_ejecuciones.csv
    fact_esperado.csv
    diagnostico_matcheo.xlsx
"""

import sys
import pandas as pd

from settings import (
    PATH_DB_SERVER, PATH_RELEVAMIENTO, PATH_TABLA_CUITS,
    OUTPUTS_DIR,
    OUT_DIM_CLIENTES, OUT_DIM_HERRAMIENTAS, OUT_DIM_RELEVAMIENTO,
    OUT_FACT_EJECUCIONES, OUT_FACT_ESPERADO, OUT_DIAGNOSTICO,
)
from paso1_relevamiento      import leer_relevamiento
from paso2_db_server         import leer_db_server
from paso3_fact_ejecuciones  import construir_fact_ejecuciones
from construir_esperado      import construir_esperado
from paso4_diagnostico       import generar_diagnostico


def banner(texto: str) -> None:
    sep = "─" * 60
    print(f"\n{sep}\n  {texto}\n{sep}")


def main() -> None:

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # ── PASO 0 (opcional): Fetch desde SQL Server ─────────────────────────────
    if "--fetch" in sys.argv:
        from fetch_db_server import fetch_and_export
        banner("PASO 0 | Descargando datos desde SQL Server...")
        fetch_and_export(PATH_DB_SERVER)

    # ── PASO 1: Relevamiento ──────────────────────────────────────────────────
    banner("PASO 1 | Leyendo Relevamiento BPS...")
    dim_clientes, dim_relevamiento = leer_relevamiento(PATH_RELEVAMIENTO)
    print(f"  → dim_clientes:     {len(dim_clientes):>6,} filas")
    print(f"  → dim_relevamiento: {len(dim_relevamiento):>6,} filas")

    dim_herramientas = (
        dim_relevamiento[["herramienta"]]
        .drop_duplicates()
        .assign(en_relevamiento=True)
        .sort_values("herramienta")
        .reset_index(drop=True)
    )

    # ── PASO 2: DB Server ─────────────────────────────────────────────────────
    banner("PASO 2 | Leyendo y clasificando DB_Server...")
    df_db = leer_db_server(PATH_DB_SERVER, PATH_TABLA_CUITS)
    tipos = df_db["tipo_cliente"].value_counts()
    print(f"  → Total ejecuciones: {len(df_db):,}")
    for tipo, cnt in tipos.items():
        print(f"     {tipo:<12}: {cnt:>6,}  ({cnt/len(df_db)*100:.1f}%)")

    # ── PASO 3: fact_ejecuciones ──────────────────────────────────────────────
    banner("PASO 3 | Construyendo fact_ejecuciones...")
    fact = construir_fact_ejecuciones(df_db, dim_clientes)
    print(f"  → fact_ejecuciones: {len(fact):,} filas")
    print(f"  → Herramientas únicas:  {fact['herramienta'].nunique()}")
    print(f"  → Clientes con CUIT:    {(fact['cuit_cliente'] != '').sum():,}")
    print(f"  → En Relevamiento:      {fact['en_relevamiento'].sum():,} ({fact['en_relevamiento'].mean()*100:.1f}%)")

    # Agregar herramientas externas a dim_herramientas
    herr_extra = (
        fact[~fact["en_relevamiento"]][["herramienta"]]
        .drop_duplicates()
        .assign(en_relevamiento=False)
    )
    dim_herramientas = (
        pd.concat([dim_herramientas, herr_extra], ignore_index=True)
        .drop_duplicates(subset=["herramienta"])
        .sort_values(["en_relevamiento", "herramienta"], ascending=[False, True])
        .reset_index(drop=True)
    )

    # ── PASO 4: fact_esperado ─────────────────────────────────────────────────
    banner("PASO 4 | Construyendo fact_esperado (Real vs Esperado)...")
    fact_esp = construir_esperado(dim_relevamiento, fact)
    print(f"  → fact_esperado: {len(fact_esp):,} filas")

    # ── PASO 5: Exportar CSVs ─────────────────────────────────────────────────
    banner("PASO 5 | Exportando tablas para Power BI...")
    dim_clientes.to_csv(OUT_DIM_CLIENTES,         index=False, encoding="utf-8-sig")
    dim_herramientas.to_csv(OUT_DIM_HERRAMIENTAS, index=False, encoding="utf-8-sig")
    dim_relevamiento.to_csv(OUT_DIM_RELEVAMIENTO, index=False, encoding="utf-8-sig")
    fact.to_csv(OUT_FACT_EJECUCIONES,             index=False, encoding="utf-8-sig")
    fact_esp.to_csv(OUT_FACT_ESPERADO,            index=False, encoding="utf-8-sig")
    print(f"  ✅ dim_clientes.csv          → {len(dim_clientes):,} filas")
    print(f"  ✅ dim_herramientas.csv      → {len(dim_herramientas):,} filas")
    print(f"  ✅ dim_relevamiento.csv      → {len(dim_relevamiento):,} filas")
    print(f"  ✅ fact_ejecuciones.csv      → {len(fact):,} filas")
    print(f"  ✅ fact_esperado.csv         → {len(fact_esp):,} filas")

    # ── PASO 6: Diagnóstico ───────────────────────────────────────────────────
    banner("PASO 6 | Generando diagnóstico de calidad...")
    generar_diagnostico(fact, dim_clientes, dim_relevamiento, OUT_DIAGNOSTICO)

    banner("✅ Pipeline finalizado correctamente")
    print(f"\n  Outputs en: {OUTPUTS_DIR}\n")


if __name__ == "__main__":
    main()
    
    
    

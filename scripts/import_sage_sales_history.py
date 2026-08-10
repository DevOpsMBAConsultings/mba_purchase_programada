#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import_sage_sales_history.py
============================
Script de importación del historial de ventas de Sage hacia Odoo 18 CE.
Crea/actualiza registros en mba.product.sales.history.

Uso:
    python3 import_sage_sales_history.py --dry-run   # Auditoría: sin escribir
    python3 import_sage_sales_history.py             # Importación real

Requisitos:
    pip install openpyxl

MBA Consultings, Brooks González
"""

import sys
import xmlrpc.client
import openpyxl
from pathlib import Path

# ===========================================================================
# CONFIGURACIÓN — ajustar antes de ejecutar
# ===========================================================================
ODOO_URL = "https://simplificat.mbaconsultings.com"
DB = "odoo18"          # nombre de la base de datos en Odoo
USER = "admin"              # usuario con permisos de stock manager
import os
PASSWORD = os.environ.get("ODOO_PASSWORD", "")

XLSX_PATH = Path(__file__).parent.parent.parent.parent.parent / \
    "proyectos/Simplifica T/historico/MOQ REORDER.xlsx"
# Ajustar la ruta si ejecutas desde otra ubicación:
# XLSX_PATH = Path("/ruta/absoluta/a/MOQ REORDER.xlsx")

# Mapa columna del XLSX → (mes, año)
# Col índice 0-based: 5=Jul, 6=Jun, 7=May, 8=Apr
COL_MONTH_MAP = {
    5: (7, 2026),   # Units Sold 7/31/26
    6: (6, 2026),   # Units Sold 6/30/26
    7: (5, 2026),   # Units Sold 5/31/26
    8: (4, 2026),   # Units Sold 4/30/26
}
# ===========================================================================

DRY_RUN = "--dry-run" in sys.argv


def connect_odoo():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USER, PASSWORD, {})
    if not uid:
        print("❌ Error: no se pudo autenticar en Odoo. Verificar credenciales.")
        sys.exit(1)
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    print(f"✅ Conectado a Odoo como UID={uid}")
    return uid, models


def main():
    print("=" * 60)
    print("MBA - Importación Historial Ventas Sage → Odoo")
    print(f"MODO: {'🔍 DRY RUN (sin cambios)' if DRY_RUN else '⚠️  IMPORTACIÓN REAL'}")
    print("=" * 60)

    if not XLSX_PATH.exists():
        print(f"❌ No se encontró el archivo: {XLSX_PATH}")
        sys.exit(1)

    print(f"📄 Leyendo: {XLSX_PATH.name}")
    wb = openpyxl.load_workbook(str(XLSX_PATH))
    ws = wb["COMPRA MENSUAL"]

    uid, models = connect_odoo()

    matched = 0
    not_found = []
    created = 0
    updated = 0
    skipped_zero = 0

    for row in ws.iter_rows(min_row=6, values_only=True):
        item_id = row[0]
        if not item_id:
            continue

        # Buscar product.template por Referencia (default_code)
        tmpl_ids = models.execute_kw(
            DB, uid, PASSWORD,
            'product.template', 'search',
            [[['default_code', '=', str(item_id).strip()]]]
        )

        if not tmpl_ids:
            not_found.append(item_id)
            continue

        matched += 1
        tmpl_id = tmpl_ids[0]

        if DRY_RUN:
            continue

        for col_idx, (month, year) in COL_MONTH_MAP.items():
            units = row[col_idx] or 0.0

            # Buscar si ya existe registro para este producto/mes/año
            existing_ids = models.execute_kw(
                DB, uid, PASSWORD,
                'mba.product.sales.history', 'search',
                [[
                    ['product_tmpl_id', '=', tmpl_id],
                    ['month', '=', month],
                    ['year', '=', year],
                ]]
            )

            if existing_ids:
                models.execute_kw(
                    DB, uid, PASSWORD,
                    'mba.product.sales.history', 'write',
                    [existing_ids, {'units_sold': units}]
                )
                updated += 1
            else:
                models.execute_kw(
                    DB, uid, PASSWORD,
                    'mba.product.sales.history', 'create',
                    [{
                        'product_tmpl_id': tmpl_id,
                        'month': month,
                        'year': year,
                        'units_sold': units,
                    }]
                )
                created += 1

    # Reporte final
    print("\n" + "=" * 60)
    print("📊 RESULTADO")
    print(f"  ✅ Productos con match:     {matched}")
    print(f"  ❌ Item IDs sin match:      {len(not_found)}")
    if not DRY_RUN:
        print(f"  🆕 Registros creados:       {created}")
        print(f"  ✏️  Registros actualizados:  {updated}")
    print("=" * 60)

    if not_found:
        print(f"\n⚠️  Primeros 20 Item IDs sin match en Odoo:")
        for item in not_found[:20]:
            print(f"    - {item}")
        if len(not_found) > 20:
            print(f"    ... y {len(not_found) - 20} más.")

    if DRY_RUN:
        print(
            f"\n💡 Para ejecutar la importación real, corre sin --dry-run:\n"
            f"   python3 {Path(__file__).name}"
        )


if __name__ == "__main__":
    main()

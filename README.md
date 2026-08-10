# SimplificaT - Odoo 18/19 Custom Modules

Este repositorio centraliza los módulos personalizados desarrollados por **MBA Consultings** para el entorno de Odoo 18/19 del cliente **SimplificaT** y el proyecto **Suplidora JC**. Los módulos están diseñados para adaptar y extender el comportamiento estándar de Odoo a los procesos de negocio específicos, manteniendo las mejores prácticas de desarrollo y modularidad técnica.

## 📁 Estructura del Repositorio

```
.
├── mba-facturacion-panama/           # Módulos de localización Panamá (Facturación Electrónica DGI)
│   ├── mba_pa_base/                  # Catálogos base DGI (Provincias, Distritos, Corregimientos)
│   ├── mba_pa_products/              # Catálogo productos CPBS y Unidades de Medida DGI
│   ├── mba_pa_edi/                   # Core facturación electrónica DGI (sin PAC asignado)
│   ├── mba_pa_edi_digifact/          # Conector PAC Digifact (XML)
│   ├── mba_pa_edi_hka/               # Conector PAC The Factory HKA (REST API)
│   ├── mba_pa_sale/                  # Integración Ventas DGI (cotizaciones/pedidos)
│   └── mba_pa_pos/                   # POS Facturación Electrónica DGI
├── l10n_pa_simplificat/              # Plan de cuentas Panamá - Simplifica T
├── mba_reportes_diarios/             # Reportes diarios de cierre de caja (Panamá)
├── sale_line_pricelist/              # Lista de precios por línea de venta
├── product_multi_pricelist_display/  # Visualización multi-lista precios en productos
├── formato_cotizacion_simplificat/   # Formato cotización corporativo
├── partner_social/                   # Redes sociales en contactos (Panamá)
├── mb_sale_order_availability/       # Disponibilidad de stock en líneas de cotización
├── mba_importador_cotizaciones_pdf/  # Importador de cotizaciones/facturas PDF
├── mba_purchase_order_format/        # Formato de orden de compra personalizado
├── mba_purchase_consolidation/       # Consolidación de órdenes de compra
├── mb_stock_orderpoint_vendor/       # Proveedor en reglas de reabastecimiento
├── mba_account_aging/                # Antigüedad de saldos (CxC/CxP)
├── mba_finance_dashboard/            # Tablero financiero
├── base_account_budget/              # Gestión de presupuestos (Cybrosys, vendorizado)
├── base_accounting_kit/              # Kit completo de contabilidad (Cybrosys, vendorizado)
├── dynamic_accounts_report/          # Reportes contables dinámicos (Cybrosys, vendorizado)
└── web_responsive_custom/            # Personalización tema Web Responsive
```

---

## 📦 Módulos Incluidos

### 🇵🇦 Localización Panamá - Facturación Electrónica DGI

#### 1. Panamá - Catálogos Base (`mba_pa_base`)
**v18.0.1.0.2** | Categoría: Accounting/Localizations
- Catálogos oficiales DGI: Provincias, Distritos, Corregimientos
- Extiende `res.partner` y `res.company` con campos DGI
- Wizard de validación DGI en contactos
- Dependencias: `base`, `contacts`

#### 2. Panamá - Catálogo de Productos (`mba_pa_products`)
**v18.0.1.0.0** | Categoría: Accounting/Localizations
- Códigos CPBS (Segmento, Familia) oficiales DGI
- Unidades de medida DGI precargadas
- Extiende `product.template` con campos CPBS/Unidad DGI
- Dependencias: `mba_pa_base`, `product`

#### 3. Panamá - Facturación Electrónica Core (`mba_pa_edi`)
**v18.0.1.0.2** | Categoría: Accounting/Localizations
- Core FE sin PAC asignado (multi-PAC ready)
- Tipos de documento DGI, secuencias NC/ND
- Métodos de pago DGI, tipos de retención
- Wizard confirmar/enviar facturas
- CSS ribbon para estados FE en backend
- Dependencias: `account`, `sale`, `mba_pa_base`, `mba_pa_products`

#### 4. Panamá - Conector Digifact (`mba_pa_edi_digifact`)
**v18.0.1.0.1** | Categoría: Accounting/Localizations
- Conector XML para PAC Digifact
- Builder NUC (Número Único de Control)
- Logs de comunicación Digifact
- Configuración compañía (credenciales, endpoints)
- Dependencias: `mba_pa_edi`, `mba_pa_sale`

#### 5. Panamá - Conector The Factory HKA (`mba_pa_edi_hka`)
**v18.0.1.0.5** | Categoría: Accounting/Localizations
- Conector REST API para PAC The Factory HKA
- Anulación de facturas (wizard)
- Crédito otros vencimientos, pago otras descripciones (wizards)
- Configuración compañía (API keys, ambiente)
- Dependencias: `mba_pa_edi`, `mba_pa_sale`

#### 6. Panamá - Integración con Ventas (`mba_pa_sale`)
**v18.0.1.0.11** | Categoría: Sales
- Extensión cotizaciones/pedidos para DGI
- Validaciones DGI en sale.order (wizard + JS)
- Campos DGI en líneas de venta
- Dependencias: `sale`, `mba_pa_base`, `mba_pa_edi`

#### 7. Panamá - POS Facturación Electrónica (`mba_pa_pos`)
**v18.0.1.0.3** | Categoría: Point of Sale
- Integración POS con FE DGI
- Configuración POS para facturación electrónica
- Órdenes POS con datos DGI
- Dependencias: `point_of_sale`, `mba_pa_edi`

#### 8. Panamá - Plan de Cuentas Simplifica T (`l10n_pa_simplificat`)
**v18.0.1.0.5** | Categoría: Accounting/Localizations/Account Charts
- Plan de cuentas contable propio para Panamá, instalable como plantilla fiscal (`account.chart.template`) al crear la compañía
- Define cuentas por defecto de la compañía: por cobrar, por pagar, ingresos, gastos, banco, caja, transferencias, diferencia de cambio, descuentos por pronto pago, diferencias de caja
- **Cómo funciona:** usa el decorador `@template('pa_simplificat')` de Odoo 18 para registrar un juego de cuentas nuevo bajo el país Panamá; al seleccionarlo en la configuración fiscal de la compañía, Odoo crea automáticamente todas las cuentas y las vincula a los campos contables correspondientes
- Dependencias: `account`

#### 9. Panamá - Reportes Diarios Cierre de Caja (`mba_reportes_diarios`)
**v18.0.1.3.16** | Categoría: Accounting/Localizations
- Cierre de caja diario: facturación, cobros de cuentas por cobrar (CxC) y ventas de Punto de Venta
- Matriz mensual "mes a la fecha" (MTD) de ingresos y reporte de comisiones de ventas
- **Cómo funciona:** agrega un modelo `mba.report.template` que actúa como catálogo de reportes disponibles (cada uno con su wizard e icono); cada wizard (`mba.daily.cxc.wizard`, etc.) pide una fecha y compañía, clasifica facturas/pagos (incluyendo detección de pagos que vienen del POS) y genera un PDF con totales formateados. Un reporte queda oculto automáticamente si el módulo de Odoo del que depende (ej. `point_of_sale`) no está instalado
- Dependencias: `account`

---

### 💰 Ventas y CRM

#### 10. Sale Line Pricelist (`sale_line_pricelist`)
**v18.0.1.0.0** | Categoría: Sales | **Aplicación**
- Permite seleccionar lista de precios **por línea de pedido**
- Control de precios unitario/impuestos por regla de pricelist
- Campo *Nota Interna Proveedor* en líneas de venta
- Oculta pricelist global, muestra columnas por línea
- Dependencias: `sale`

#### 11. Product Multi Pricelist Display (`product_multi_pricelist_display`)
**v18.0.1.0.0** | Categoría: Sales
- Muestra precios de múltiples listas en vista lista producto
- Marcado de listas a visualizar (checkbox en pricelist)
- Columnas dinámicas con precios por lista seleccionada
- Dependencias: `product`, `sale`

#### 12. Formato Cotización (`formato_cotizacion_simplificat`)
**v18.0.1.0.0** | Categoría: Sales
- Plantilla base reutilizable (limpia referencias hardcoded)
- Inyección automática: logos, tipografías, colores corporativos
- Sobreescribe `report_saleorder` estándar
- Dependencias: `sale`

#### 13. Redes Sociales en Contactos (`partner_social`)
**v1.0** | Categoría: Sales/CRM | **Aplicación** | Compatible Odoo 18/19
- Campos: Facebook, Instagram, LinkedIn en `res.partner`
- Acceso rápido a redes sociales de clientes
- Diseñado para empresas en Panamá
- Dependencias: `base`, `contacts`

#### 14. Disponibilidad de Producto en Cotización (`mb_sale_order_availability`)
**v18.0.1.0.0** | Categoría: Sales
- Agrega la columna **Stock Disp.** en las líneas de la cotización, justo antes de la Unidad de Medida
- **Cómo funciona:** un campo calculado (`free_qty_available`) en `sale.order.line` que, cada vez que cambia el producto o el almacén de la cotización, consulta la cantidad libre (`free_qty`/`qty_available`) de ese producto en ese almacén específico — así el vendedor ve el stock real disponible sin salir de la cotización
- Dependencias: `sale`, `sale_stock`

#### 15. Importador de Cotizaciones PDF (`mba_importador_cotizaciones_pdf`)
**v18.0.1.0.2** | Categoría: Sales/Sales
- Importa cotizaciones y comprobantes electrónicos (CAFE DGI/HKA) directamente desde un PDF, sin depender de APIs de pago ni de IA
- Homologación automática: si el cliente del PDF no existe en la base, la línea se asigna a "Consumidor Final" conservando el nombre original para auditoría
- Maneja productos no encontrados dejando la línea sin vincular (con descripción, cantidad, precio e impuesto) para que el vendedor la revise
- Adjunta el PDF original al chatter del pedido y marca alertas visuales si hubo advertencias en la importación
- **Cómo funciona:** usa la librería `PyMuPDF` (`fitz`) para leer el texto y los bloques del PDF localmente; primero detecta si es un comprobante DGI/HKA o una cotización genérica (buscando texto como "Comprobante Auxiliar" o "DGI"), y aplica un parser distinto con expresiones regulares para extraer cabecera, líneas y totales según el formato detectado
- Dependencias: `sale_management`, `mail`

---

### 🛒 Compras

#### 16. Formato de Orden de Compra (`mba_purchase_order_format`)
**v18.0.1.0.1** | Categoría: Purchases
- Rediseña el reporte PDF estándar de orden de compra con identidad corporativa (azul/rojo)
- **Cómo funciona:** es solo una vista QWeb (`views/report_purchaseorder.xml`) que hereda y sobreescribe el reporte nativo de compras; no agrega modelos ni lógica de negocio
- Dependencias: `purchase`

#### 17. Consolidación de Órdenes de Compra (`mba_purchase_consolidation`)
**v18.0.1.0.2** | Categoría: Purchase
- Wizard para fusionar varias órdenes de compra en borrador del mismo proveedor en una sola orden de destino
- Opción de eliminar las órdenes originales tras consolidar (en vez de solo cancelarlas)
- **Cómo funciona:** adaptación del wizard `purchase_order_merge` de OCA/Camptocamp; valida que las órdenes seleccionadas sean compatibles (mismo proveedor, misma compañía, etc.), mueve las líneas de las órdenes origen a la orden destino y reasigna las referencias que apuntaban a las órdenes fusionadas
- Dependencias: `purchase`

---

### 📦 Inventario

#### 18. Proveedor en Reabastecimiento (`mb_stock_orderpoint_vendor`)
**v18.0.1.0.4** | Categoría: Inventory/Inventory
- En las reglas de reabastecimiento (`stock.warehouse.orderpoint`), asigna automáticamente el primer proveedor configurado en la pestaña de Compras del producto
- Restringe el selector de proveedor solo a los proveedores ya configurados en ese producto (evita crear proveedores "al vuelo" desde ahí)
- Agrega columnas opcionales con el historial de ventas de los últimos 4 meses (ventana móvil M-1 a M-4 más total), útil para decidir cuánto reabastecer
- **Cómo funciona:** un campo calculado filtra los `seller_ids` del producto por compañía y toma el primero como proveedor sugerido; el historial de ventas vive en un modelo separado (`mba.product.sales.history`, un registro por producto/mes/año) que hoy se alimenta importando datos desde Sage mediante un script incluido (`scripts/import_sage_sales_history.py`), pensado para migrarse a cálculo nativo desde Odoo más adelante
- Dependencias: `stock`, `purchase_stock`

---

### 📊 Contabilidad y Reportes Financieros

#### 19. Antigüedad de Saldos (`mba_account_aging`)
**v18.0.1.0.0** | Categoría: Accounting/Reporting
- Clasifica las facturas/pagos abiertos de clientes y proveedores en tramos de días vencidos (por defecto 0-30/31-60/61-90/+90), configurables por compañía
- Analizable en pivote, gráfico de pastel y lista; se puede insertar en hojas de cálculo y tableros
- **Cómo funciona:** en vez de un campo calculado y almacenado (que se volvería obsoleto al día siguiente), expone una **vista SQL de solo lectura** (`_auto = False`) que calcula los días vencidos contra `CURRENT_DATE` en cada consulta — siempre está al día y no necesita tareas programadas ni recálculos. Cubre cuentas por cobrar y por pagar en un mismo modelo, distinguidas por el campo `ledger`
- Dependencias: `account`

#### 20. Tablero Financiero (`mba_finance_dashboard`)
**v18.0.1.0.0** | Categoría: Accounting/Reporting
- Tablero que se instala ya armado en **Tableros → Finance → Finance Overview**: antigüedad de CxC/CxP, posición neta y cobertura, estado de resultados del año, y top 10 de clientes/proveedores con saldo vencido
- **Cómo funciona:** es una hoja de cálculo de Odoo (`spreadsheet.dashboard`) cuyo contenido vive en un archivo `.osheet.json` cargado como dato del módulo; las cifras se recalculan en vivo cada vez que se abre, tomando los datos del modelo de `mba_account_aging`. Se puede editar desde la interfaz (agregar bloques, reordenar) sin tocar código
- Dependencias: `mba_account_aging`, `spreadsheet_dashboard`, `spreadsheet_account`

#### 21. Gestión de Presupuestos (`base_account_budget`) — Cybrosys, vendorizado
**v18.0.1.0.0** | Categoría: Accounting
- Presupuestos por cuenta analítica: se define el monto planeado y luego se compara contra el monto real ejecutado
- Vista de lista y vista gráfica del avance de cada presupuesto
- ⚠️ Módulo de terceros (Cybrosys Techno Solutions), incluido tal cual en el repositorio; no se modifica directamente, cualquier ajuste se hace por herencia en un módulo propio
- Dependencias: `base`, `account`

#### 22. Kit Completo de Contabilidad (`base_accounting_kit`) — Cybrosys, vendorizado
**v18.0.5.0.9** | Categoría: Accounting | **Aplicación**
- Suite de reportes financieros (mayor general, balance de comprobación, libro de bancos/caja/diario), activos fijos, cheques posfechados (PDC), límite de crédito por cliente y seguimientos (follow-ups) de cobranza
- Import de estados de cuenta bancarios (formatos OFX/QIF/Excel)
- ⚠️ Módulo de terceros (Cybrosys Techno Solutions), incluido tal cual; es prerrequisito de `dynamic_accounts_report`
- Dependencias: `account`, `sale`, `account_check_printing`, `analytic`, `base_account_budget`

#### 23. Reportes Contables Dinámicos (`dynamic_accounts_report`) — Cybrosys, vendorizado
**v18.0.1.3.4** | Categoría: Accounting
- Reportes dinámicos (filtrables/exportables desde la interfaz, sin asistente): libro mayor, balance de comprobación, balance general, estado de resultados, libro de bancos/caja, libro de socios (partner ledger), antigüedad de CxC/CxP y reportes de impuestos
- ⚠️ Módulo de terceros (Cybrosys Techno Solutions), incluido tal cual; requiere `base_accounting_kit` instalado
- Dependencias: `base_accounting_kit`

---

### 🌐 Web

#### 24. Web Responsive Customization (`web_responsive_custom`)
**v18.0.1.0.0** | Categoría: Web | Auto-install
- Extiende configuraciones del tema `web_responsive`
- Personalización settings de usuario
- Dependencias: `web_responsive`

---

## 🛠 Instalación y Despliegue

Todos los módulos están construidos bajo el estándar **Odoo 18.0** (compatibles 19.0 donde se indica).

### Requisitos Previos
- Odoo 18.0+ instalado y configurado
- Acceso al servidor para clonar repositorio
- Ruta `addons_path` configurada en `odoo.conf`

### Pasos de Instalación

```bash
# 1. Clonar repositorio en ruta de addons personalizados
cd /opt/odoo/custom-addons/
git clone -b 18.0 https://github.com/DevOpsMBAConsultings/simplificat.git

# 2. Verificar/actualizar addons_path en odoo18.conf
# addons_path = /opt/odoo/custom-addons,/opt/odoo/addons,/opt/odoo/odoo/addons

# 3. Reiniciar servicio Odoo
sudo systemctl restart odoo18

# 4. En Odoo: Modo Desarrollador → Aplicaciones → Actualizar Lista → Instalar módulos
```

### Orden de Instalación Recomendado (Panamá FE)
```
1. mba_pa_base
2. mba_pa_products
3. mba_pa_edi
4. mba_pa_sale
5. mba_pa_edi_digifact  (si usa Digifact)
   O
   mba_pa_edi_hka       (si usa The Factory HKA)
6. mba_pa_pos           (si usa POS)
```

### Orden de Instalación Recomendado (Contabilidad/Reportes)
```
1. mba_account_aging
2. mba_finance_dashboard       (requiere mba_account_aging + spreadsheet_dashboard/account)
3. base_account_budget
4. base_accounting_kit         (requiere base_account_budget)
5. dynamic_accounts_report     (requiere base_accounting_kit)
```

---

## ⚙️ Configuración Post-Instalación

### Panamá FE - PAC Digifact
1. Ir a **Configuración > Compañías > Editar > Facturación Electrónica (Digifact)**
2. Configurar: Client ID, Client Secret, Ambiente (Prueba/Producción)
3. Probar conexión

### Panamá FE - PAC The Factory HKA
1. Ir a **Configuración > Compañías > Editar > Facturación Electrónica (HKA)**
2. Configurar: API Key, Ambiente, Endpoint
3. Probar autorización

### Sale Line Pricelist
1. Ir a **Ventas > Configuración > Listas de Precios**
2. Crear/editar listas de precios
3. En cotización/pedido: columna "Lista de Precios" disponible por línea

### Antigüedad de Saldos / Tablero Financiero
1. Ir a **Contabilidad > Ajustes > Aged Balance** y definir los tramos de días vencidos (por defecto 30/60/90)
2. Consultar en **Contabilidad > Informes > Aged Receivable / Aged Payable** (vista pivote)
3. Si está instalado `mba_finance_dashboard`, el tablero ya armado aparece en **Tableros > Finance > Finance Overview**

---

## 🔧 Desarrollo y Contribución

### Estándares
- Código: OCA Guidelines (Odoo Community Association)
- Ramas: `18.0`, `19.0` por versión Odoo
- Commits: Conventional Commits
- Licencias: LGPL-3 / AGPL-3 según módulo

### Testing
```bash
# Ejecutar tests (si aplica)
cd /opt/odoo/custom-addons/simplificat
odoo-bin --test-enable --stop-after-init -d test_db -i mba_pa_edi
```

---

## 🤝 Mantenimiento y Soporte

**MBA Consultings**  
Desarrollo y Arquitectura Cloud | DevOps & Odoo Specialists  
🌐 https://www.mbaconsultings.com  
📧 info@mbaconsultings.com

*Repositorio gestionado bajo el estándar de ramas de versión de la OCA (Odoo Community Association).*

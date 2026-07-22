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
├── sale_line_pricelist/              # Lista de precios por línea de venta
├── formato_cotizacion_simplificat/   # Formato cotización corporativo
├── partner_social/                   # Redes sociales en contactos (Panamá)
├── product_multi_pricelist_display/  # Visualización multi-lista precios en productos
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

---

### 💰 Ventas y CRM

#### 8. Sale Line Pricelist (`sale_line_pricelist`)
**v18.0.1.0.0** | Categoría: Sales | **Aplicación**
- Permite seleccionar lista de precios **por línea de pedido**
- Control de precios unitario/impuestos por regla de pricelist
- Campo *Nota Interna Proveedor* en líneas de venta
- Oculta pricelist global, muestra columnas por línea
- Dependencias: `sale`

#### 9. Product Multi Pricelist Display (`product_multi_pricelist_display`)
**v18.0.1.0.0** | Categoría: Sales
- Muestra precios de múltiples listas en vista lista producto
- Marcado de listas a visualizar (checkbox en pricelist)
- Columnas dinámicas con precios por lista seleccionada
- Dependencias: `product`, `sale`

#### 10. Formato Cotización (`formato_cotizacion_simplificat`)
**v18.0.1.0.0** | Categoría: Sales
- Plantilla base reutilizable (limpia referencias hardcoded)
- Inyección automática: logos, tipografías, colores corporativos
- Sobreescribe `report_saleorder` estándar
- Dependencias: `sale`

#### 11. Redes Sociales en Contactos (`partner_social`)
**v1.0** | Categoría: Sales/CRM | **Aplicación** | Compatible Odoo 18/19
- Campos: Facebook, Instagram, LinkedIn en `res.partner`
- Acceso rápido a redes sociales de clientes
- Diseñado para empresas en Panamá
- Dependencias: `base`, `contacts`

---

### 🌐 Web

#### 12. Web Responsive Customization (`web_responsive_custom`)
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
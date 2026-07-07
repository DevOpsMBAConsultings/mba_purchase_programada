# SimplificaT - Odoo 18 Custom Modules

Este repositorio centraliza los módulos personalizados desarrollados para el entorno de Odoo 18 del cliente **SimplificaT**. Los módulos aquí presentes están diseñados para adaptar y extender el comportamiento estándar de Odoo a los procesos de negocio específicos de la empresa, manteniendo las mejores prácticas de desarrollo y modularidad técnica.

## 📦 Módulos Incluidos

### 1. Lista de Precios por Línea de Venta (`simplificat_sale_line_pricelist`)
Este módulo altera el comportamiento estándar de Odoo en las cotizaciones y pedidos de venta, trasladando el control de las listas de precios desde la cabecera del documento hacia cada línea individual de producto.

**Características principales:**
* **Flexibilidad Comercial:** Permite asignar una lista de precios (tarifa) diferente a cada producto dentro de una misma cotización.
* **Control de Precios:** Bloquea los campos de *Precio Unitario* e *Impuestos* en la vista de lista, impidiendo la edición manual. Los valores se calculan estrictamente en base a la regla de la lista de precios seleccionada, garantizando integridad en los márgenes.
* **Gestión de Proveedores:** Incorpora un campo opcional de *Nota Interna de Proveedor* (`internal_vendor_note`) directamente en las líneas de venta para facilitar el seguimiento de compras y abastecimiento.
* **UI Optimizada:** Oculta la lista de precios global para evitar confusiones y añade las nuevas columnas estratégicamente antes del precio unitario.

### 2. Formato de Cotización SimplificaT (`formato_cotizacion_simplificat`)
Módulo encargado de la identidad visual e imagen corporativa en los documentos PDF generados desde Odoo.

**Características principales:**
* **Diseño Agnostic:** Hereda y limpia módulos base de cotización para eliminar referencias quemadas a clientes anteriores, convirtiendo la plantilla en una estructura reutilizable y limpia.
* **Identidad de Marca:** Inyecta de forma automatizada los logotipos, tipografías y colores corporativos de **SimplificaT** en los reportes de ventas (`report_saleorder`).
* **Profesionalismo:** Garantiza que cada documento PDF enviado al cliente final mantenga un estándar de calidad, accesibilidad y diseño superior.

---

## 🛠 Instalación y Despliegue

Todos los módulos en este repositorio están construidos bajo el estándar de la versión **18.0**. 

1. Clona este repositorio en el servidor dentro de la ruta de addons personalizados (ej. `/opt/odoo/custom-addons/`).
   ```bash
   git clone -b 18.0 https://github.com/DevOpsMBAConsultings/simplificat.git
   ```
2. Asegúrate de que la ruta del repositorio esté incluida en el parámetro `addons_path` de tu archivo de configuración `odoo18.conf`.
3. Reinicia el servicio de Odoo:
   ```bash
   sudo systemctl restart odoo18
   ```
4. Activa el **Modo Desarrollador** en Odoo, ve a **Aplicaciones**, haz clic en **Actualizar Lista de Aplicaciones** e instala los módulos.

## 🤝 Mantenimiento y Soporte
**MBA Consultings**  
Desarrollo y Arquitectura Cloud | DevOps & Odoo Specialists  
*Repositorio gestionado bajo el estándar de ramas de versión de la OCA (Odoo Community Association).*

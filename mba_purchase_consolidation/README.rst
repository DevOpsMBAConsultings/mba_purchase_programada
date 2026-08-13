==============================
Purchase Order Consolidation
==============================

.. |badge_license| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge_version| image:: https://img.shields.io/badge/odoo-18.0-purple.png
    :alt: Odoo 18.0

|badge_license| |badge_version|

Consolida varias solicitudes de cotización (RFQ) del mismo proveedor en una
sola, desde la vista de lista de órdenes de compra.

Origen del código
=================

Este módulo es una **adaptación de** ``purchase_merge``. El código fuente
original pertenece a **Camptocamp SA** y se distribuye a través de la **Odoo
Community Association (OCA)** en el proyecto `OCA/purchase-workflow
<https://github.com/OCA/purchase-workflow>`_, bajo licencia AGPL-3.

MBA Consultings lo modificó para adaptarlo a las necesidades de sus clientes y
para hacerlo compatible con Odoo 18.0. Se conserva la licencia original AGPL-3.

Esta adaptación **no es mantenida por la OCA**. Para soporte de este fork,
contactar a MBA Consultings.

Qué hace
========

Un asistente que se invoca desde el menú *Acciones* de la vista de lista de
órdenes de compra. Si se cumplen los criterios de fusión, todas las líneas de
las órdenes seleccionadas se transfieren a la orden destino, y los campos
``origin`` y ``partner_ref`` se concatenan. Se registra un mensaje en el chatter
de cada orden indicando cuándo ocurrió la fusión y qué órdenes estuvieron
involucradas. Las órdenes de origen quedan canceladas, o eliminadas si así se
indica.

Criterios de fusión
===================

Todas las órdenes seleccionadas deben compartir:

* Proveedor
* Estado borrador
* Moneda
* Tipo de operación (picking type)
* Incoterm
* Términos de pago
* Posición fiscal

Uso
===

1. Ir a **Compras → Órdenes → Solicitudes de cotización**.
2. Seleccionar con las casillas las órdenes que se quieren consolidar.
3. Abrir el menú **Acciones** y elegir **Merge Selected Purchase**.
4. En el asistente, seleccionar la orden **destino** (por defecto la más
   antigua) y marcar **Delete Source POs** si se quieren eliminar las órdenes
   de origen en lugar de cancelarlas.
5. Pulsar **Merge Purchase**.

Si alguna orden no cumple los criterios, el asistente lo indica con un mensaje
detallando qué campo difiere y en qué órdenes.

Cambios respecto al módulo original
===================================

* **Opción de eliminar las órdenes de origen** en lugar de solo cancelarlas.
* **Compatibilidad con Odoo 18.0**: vistas migradas de ``tree`` a ``list``.
* **Sin dependencia de** ``openupgradelib``: la reasignación de referencias
  (mensajes, actividades, seguidores, adjuntos y documentos relacionados) se
  hace con el ORM nativo. La librería es incompatible con Odoo 18 porque
  depende del modelo ``ir.property``, eliminado en esta versión.

Créditos
========

Autores del código original
---------------------------

* `Camptocamp <https://www.camptocamp.com>`_:

  * Thomas Nowicki
  * Bojan Anchev

Publicado originalmente por la `Odoo Community Association (OCA)
<https://odoo-community.org>`_.

Adaptación a Odoo 18.0
----------------------

* `MBA Consultings <https://www.mbaconsultings.com>`_:

  * Brooks Gonzalez

Licencia
========

AGPL-3, la misma del módulo original. Ver el archivo ``LICENSE``.

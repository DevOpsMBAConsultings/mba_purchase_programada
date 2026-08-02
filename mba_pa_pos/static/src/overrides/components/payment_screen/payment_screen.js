/** @odoo-module **/
// -*- coding: utf-8 -*-
//
// Panamá - POS Facturación Electrónica DGI (MBA Consultings)
//
// Regla de negocio: si el punto de venta NO usa impresora fiscal
// (config.l10n_pa_fiscal_printer = false), TODA orden debe facturarse
// electrónicamente vía PAC/DGI (ver pos_order.py:_process_order y
// _generate_pos_order_invoice, que ya fuerzan to_invoice=True y exigen
// cliente en el backend).
//
// Sin este parche, el checkbox "Factura" del POS queda desmarcado por
// defecto y el cajero solo se entera de que falta el cliente hasta que
// el backend rechaza la orden con un error crudo, después de haber
// llenado todo el ticket. Este patrón replica el que usa la propia
// localización de Perú (l10n_pe_pos), que enfrenta el mismo requisito
// de factura electrónica obligatoria.
//
// Al forzar is_to_invoice() = true ANTES de validar, se activa el aviso
// nativo de Odoo en PaymentScreen._isOrderValid() ("Please select the
// Customer / You need to select the customer before you can invoice"),
// que abre el selector de cliente directamente, en vez de dejar que la
// orden viaje al servidor y falle allí.

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    onMounted() {
        super.onMounted();
        if (!this.pos.config.l10n_pa_fiscal_printer) {
            this.currentOrder.set_to_invoice(true);
        }
    },

    toggleIsToInvoice() {
        // Sin impresora fiscal, la factura es obligatoria: no se permite
        // desmarcar el toggle. El backend la forzaría de todas formas
        // (pos_order.py:_process_order), pero bloquearlo aquí evita que
        // el cajero pierda el aviso temprano de "selecciona un cliente".
        if (this.pos.config.l10n_pa_fiscal_printer) {
            super.toggleIsToInvoice();
        }
    },

    shouldDownloadInvoice() {
        if (!this.pos.config.l10n_pa_fiscal_printer) {
            // Evitamos la descarga silenciosa/emergente ("Guardar como") nativa
            // del POS, ya que la factura DGI se mostrará embebido en ReceiptScreen.
            return false;
        }
        return super.shouldDownloadInvoice();
    },
});


/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);

        if (this.props.resModel !== "sale.order") {
            return;
        }

        const actionService = useService("action");
        const orm = useService("orm");

        onMounted(async () => {
            const record = this.model.root;

            // Solo para registros nuevos (sin ID guardado) con partner pre-cargado
            if (record.resId || !record.data.partner_id) {
                return;
            }

            const partnerId = record.data.partner_id[0];

            const partners = await orm.read(
                "res.partner",
                [partnerId],
                ["l10n_pa_is_dgi_validated", "parent_id", "name"]
            );

            if (!partners.length) return;
            const partner = partners[0];

            let isValid = partner.l10n_pa_is_dgi_validated;
            if (!isValid && partner.parent_id) {
                const parents = await orm.read(
                    "res.partner",
                    [partner.parent_id[0]],
                    ["l10n_pa_is_dgi_validated"]
                );
                if (parents.length) {
                    isValid = parents[0].l10n_pa_is_dgi_validated;
                }
            }

            if (!isValid) {
                await actionService.doAction({
                    name: "Cliente no Validado con DGI",
                    type: "ir.actions.act_window",
                    res_model: "partner.dgi.warning.wizard",
                    view_mode: "form",
                    target: "new",
                    context: {
                        default_partner_name: partner.name,
                        default_message_type: "sale",
                    },
                });
            }
        });
    },
});

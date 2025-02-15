# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartnerExemption(models.Model):
    _inherit = "res.partner.exemption"

    sign_oca_request_id = fields.Many2one("sign.oca.request")

    def write(self, vals):
        if vals.get("state") == "cancel":
            for record in self:
                record.sign_oca_request_id.cancel()
        return super().write(vals)

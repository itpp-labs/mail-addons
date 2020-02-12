from odoo import api, models


class Partner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def read(self, fields=None, load="_classic_read"):
        res = super(Partner, self).read(fields=fields, load=load)
        if fields and "message_ids" in fields:
            for vals in res:
                partner = self.browse(vals["id"])
                if not partner.is_company:
                    continue
                domain = [
                    ("model", "=", "res.partner"),
                    ("res_id", "in", [partner.id] + partner.child_ids.ids),
                ]
                vals["message_ids"] = self.env["mail.message"].search(domain).ids
        return res

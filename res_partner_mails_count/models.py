# -*- coding: utf-8 -*-

from openerp import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"
    mails_to = fields.Integer(compute="_compute_mails_to")
    mails_from = fields.Integer(compute="_compute_mails_from")

    @api.multi
    def _compute_mails_to(self):
        for r in self:
            r.mails_to = (
                self.env["mail.message"]
                .sudo()
                .search_count([("partner_ids", "in", r.id)])
            )

    @api.multi
    def _compute_mails_from(self):
        for r in self:
            r.mails_from = (
                self.env["mail.message"].sudo().search_count([("author_id", "=", r.id)])
            )

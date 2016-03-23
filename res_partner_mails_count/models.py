# -*- coding: utf-8 -*-

from openerp import models, fields, api


class res_partner(models.Model):
    _inherit = 'res.partner'
    mails_to = fields.Integer(compute="_mails_to")
    mails_from = fields.Integer(compute="_mails_from")

    @api.one
    def _mails_to(self):
        for r in self:
            r.mails_to = self.env['mail.message'].sudo().search_count([('partner_ids', 'in', r.id)])

    @api.one
    def _mails_from(self):
        for r in self:
            r.mails_from = self.env['mail.message'].sudo().search_count([('author_id', '=', r.id)])

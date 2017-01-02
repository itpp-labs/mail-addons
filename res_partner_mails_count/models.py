# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    mails_to = fields.Integer(compute="_mails_to")
    mails_from = fields.Integer(compute="_mails_from")

    @api.multi
    def _mails_to(self):
        for r in self:
            r._mails_to_one(self)

    @api.multi
    def _mails_to_one(self):
        self.ensure_one()
        for r in self:
            r.mails_to = self.env['mail.message'].sudo().search_count([('partner_ids', 'in', r.id)])

    @api.multi
    def _mails_from(self):
        for r in self:
            r._mails_from_one(self)

    @api.multi
    def _mails_from_one(self):
        self.ensure_one()
        for r in self:
            r.mails_from = self.env['mail.message'].sudo().search_count([('author_id', '=', r.id)])

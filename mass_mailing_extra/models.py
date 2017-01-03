# -*- coding: utf-8 -*-
from openerp import api, models, fields


class MailMailStats(models.Model):

    _inherit = 'mail.mail.statistics'

    partner_ids = fields.Many2many('res.partner', related='mail_mail_id.recipient_ids', string='Partners (Mail)')

    @api.multi
    def _get_partner_id(self):
        for r in self:
            r._get_partner_id_one(self)

    @api.multi
    def _get_partner_id_one(self):
        self.ensure_one()
        if self.model == 'res.partner':
            self.partner_id = self.res_id
        else:
            self.partner_id = None

    partner_id = fields.Many2one('res.partner', compute=_get_partner_id, string='Partner (Document ID)')

    @api.multi
    def _get_partners(self):
        for r in self:
            r._get_partners_one(self)

    @api.multi
    def _get_partners_one(self):
        self.ensure_one()
        res = {}
        for p in self.partner_ids:
            res[p.id] = p
        if self.partner_id and self.partner_id.id not in res:
            res[self.partner_id.id] = self.partner_id
        self.partners = ', '.join([('%s <%s>' % (p.name, p.email)) for id, p in res.items()])

    partners = fields.Char('Partners', compute=_get_partners)

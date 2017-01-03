# -*- coding: utf-8 -*-

from openerp import api
from openerp import models


class ResPartnerStripEmail(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def write(self, vals):
        for r in self:
            r.write_one(self, vals)

    @api.multi
    def write_one(self, vals):
        self.ensure_one()
        vals = self._check_email_field(vals)
        return super(ResPartnerStripEmail, self).write(vals)

    @api.model
    def create(self, vals):
        vals = self._check_email_field(vals)
        return super(ResPartnerStripEmail, self).create(vals)

    def _check_email_field(self, vals):
        if vals.get('email'):
            vals['email'] = vals['email'].strip()
        return vals

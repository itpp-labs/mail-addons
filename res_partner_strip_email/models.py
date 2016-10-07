# -*- coding: utf-8 -*-

from openerp import api
from openerp import models


class ResPartnerStripEmail(models.Model):
    _inherit = 'res.partner'

    @api.one
    def write(self, vals):
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

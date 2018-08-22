# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging
from odoo import models, fields, api


_logger = logging.getLogger(__name__)
FIELD_NAME = 'email_multi_website'


class User(models.Model):

    _inherit = ['res.users', 'website_dependent.mixin']
    _name = 'res.users'

    # extra field to detach email field from res.partner
    email = fields.Char(related='email_multi_website', inherited=False)
    email_multi_website = fields.Char(company_dependent=True, website_dependent=True)

    @api.model
    def create(self, vals):
        res = super(User, self).create(vals)
        # make value company independent
        res._force_default(FIELD_NAME, vals.get('email'))
        return res

    @api.multi
    def write(self, vals):
        res = super(User, self).write(vals)

        # TODO: will it work with OCA's partner_firstname module?
        if any(k in vals for k in ('name', 'email')):
            self._update_properties_label(FIELD_NAME)

        return res

# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, api


class IrProperty(models.Model):
    _inherit = 'ir.property'

    @api.multi
    def write(self, vals):
        res = super(IrProperty, self).write(vals)
        field = self.env.ref('base.field_res_users_email')
        self._update_db_value_website_dependent(field)
        return res

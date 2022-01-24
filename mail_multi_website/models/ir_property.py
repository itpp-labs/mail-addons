# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).
from odoo import models


class IrProperty(models.Model):
    _inherit = "ir.property"

    def write(self, vals):
        res = super(IrProperty, self).write(vals)
        field_object_list = [
            self.env.ref("base.field_res_users__email"),
            self.env.ref("mail.field_mail_template__body_html"),
            self.env.ref("mail.field_mail_template__mail_server_id"),
            self.env.ref("mail.field_mail_template__report_template"),
        ]
        for fobj in field_object_list:
            self._update_db_value_website_dependent(fobj)
        return res

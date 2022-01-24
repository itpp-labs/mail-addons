# Copyright 2018,2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
# License OPL-1 (https://www.odoo.com/documentation/user/13.0/legal/licenses/licenses.html#odoo-apps) for derivative work.
from odoo import fields, models


class Message(models.Model):
    _inherit = "mail.message"

    def _default_mail_server_id(self):
        return self.env.website.mail_server_id.id

    mail_server_id = fields.Many2one(default=_default_mail_server_id)

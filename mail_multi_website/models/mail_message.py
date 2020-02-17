# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
from odoo import fields, models


class Message(models.Model):
    _inherit = "mail.message"

    def _default_mail_server_id(self):
        website = self.env.context.get("website_id")
        if not website:
            return
        website = self.env["website"].sudo().browse(website)
        return website.mail_server_id.id

    mail_server_id = fields.Many2one(default=_default_mail_server_id)

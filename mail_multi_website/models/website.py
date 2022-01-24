# Copyright 2017 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    mail_server_id = fields.Many2one(
        "ir.mail_server", "Outgoing Mails", help="Default outgoing mail server"
    )

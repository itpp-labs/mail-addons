# Copyright 2017 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class Website(models.Model):
    _inherit = "website"

    mail_server_id = fields.Many2one('ir.mail_server', 'Outgoing Mails', help='Default outgoing mail server')

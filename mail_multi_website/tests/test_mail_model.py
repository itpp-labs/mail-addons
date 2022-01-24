# Copyright 2018,2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
# License OPL-1 (https://www.odoo.com/documentation/user/13.0/legal/licenses/licenses.html#odoo-apps) for derivative work.
from odoo import fields, models


class MailTest(models.Model):
    _inherit = "mail.test.simple"

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    website_id = fields.Many2one("website", default=lambda self: self.env.website)

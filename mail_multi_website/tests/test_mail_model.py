# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
from odoo import fields, models


class MailTest(models.Model):
    _inherit = "mail.test.simple"

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env["res.company"]._company_default_get(),
    )
    website_id = fields.Many2one(
        "website",
        default=lambda self: self.env["website"].browse(
            self.env.context.get("website_id")
        ),
    )

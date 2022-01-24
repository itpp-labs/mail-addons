# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
from odoo import api, models
from odoo.http import request


class MailComposer(models.TransientModel):

    _inherit = "mail.compose.message"

    @api.model
    def create(self, vals):
        """Workaround for https://github.com/odoo/odoo/pull/26589"""
        if "website_id" not in self.env.context:
            website = (
                request and hasattr(request, "website") and request.website or None
            )
            if not website:
                website = self.env["website"].get_current_website()
            if website:
                self = self.with_context(website_id=website.id)
        return super(MailComposer, self).create(vals)

# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, api
from odoo.http import request


class MailComposer(models.TransientModel):

    _inherit = 'mail.compose.message'

    @api.multi
    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        """Workaround for https://github.com/odoo/odoo/pull/26589"""
        if 'website_id' not in self.env.context:
            website = request and hasattr(request, 'website') and request.website or None
            if not website:
                website = self.env['website'].get_current_website()
            if website:
                self = self.with_context(website_id=website.id)
        return super(MailComposer, self).onchange_template_id(template_id, composition_mode, model, res_id)

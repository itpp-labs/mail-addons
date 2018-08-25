# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import api, models
from odoo.http import request


class MailMail(models.Model):

    _inherit = 'mail.mail'

    @api.multi
    def send_get_mail_body(self, partner=None):
        """Workaround for https://github.com/odoo/odoo/pull/26589"""
        website = request and hasattr(request, 'website') and request.website or None
        if 'website_id' not in self.env.context and website:
            self = self.with_context(website_id=website.id)
        return super(MailMail, self).send_get_mail_body(partner=partner)

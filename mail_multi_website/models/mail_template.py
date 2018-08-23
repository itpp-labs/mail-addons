# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging
from odoo import models, fields, api


_logger = logging.getLogger(__name__)
FIELDS = ['body_html', 'mail_server_id', 'report_template']


class MailTemplate(models.Model):

    _inherit = ['mail.template', 'website_dependent.mixin']
    _name = 'mail.template'

    body_html = fields.Html(company_dependent=True, website_dependent=True)
    mail_server_id = fields.Many2one(string='Outgoing Mail Server (Multi-Website)', company_dependent=True, website_dependent=True)
    report_template = fields.Many2one(string='Optional report to print and attach (Multi-Website)', company_dependent=True, website_dependent=True)

    email_multi_website = fields.Char(company_dependent=True, website_dependent=True)

    @api.model
    def create(self, vals):
        res = super(MailTemplate, self).create(vals)
        # make value company independent
        for f in FIELDS:
            res._force_default(f, vals.get(f))
        return res

    @api.multi
    def write(self, vals):
        res = super(MailTemplate, self).write(vals)

        # TODO: will it work with OCA's partner_firstname module?
        if 'name' in vals:
            fields_to_update = FIELDS
        else:
            fields_to_update = [
                f for f in FIELDS
                if f in vals
            ]
        for f in fields_to_update:
            self._update_properties_label(f)

        return res

    def _auto_init(self):
        for f in FIELDS:
            self._auto_init_website_dependent(f)
        return super(MailTemplate, self)._auto_init()

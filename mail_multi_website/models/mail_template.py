# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
from odoo.tools import pycompat
from odoo.addons.mail.models.mail_template import format_date, format_tz, format_amount

_logger = logging.getLogger(__name__)
FIELDS = ['body_html', 'mail_server_id', 'report_template']

try:
    from odoo.addons.mail.models.mail_template import mako_safe_template_env, mako_template_env
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")


class MailTemplate(models.Model):

    _inherit = ['mail.template', 'website_dependent.mixin']
    _name = 'mail.template'

    body_html = fields.Html(company_dependent=True, website_dependent=True)
    mail_server_id = fields.Many2one(string='Outgoing Mail Server (Multi-Website)', company_dependent=True, website_dependent=True)
    report_template = fields.Many2one(string='Optional report to print and attach (Multi-Website)', company_dependent=True, website_dependent=True)

    @api.model
    def render_template(self, template_txt, model, res_ids, post_process=False):
        """Override to add website to context"""
        multi_mode = True
        if isinstance(res_ids, pycompat.integer_types):
            multi_mode = False
            res_ids = [res_ids]

        results = dict.fromkeys(res_ids, u"")

        # try to load the template
        try:
            mako_env = mako_safe_template_env if self.env.context.get('safe') else mako_template_env
            template = mako_env.from_string(tools.ustr(template_txt))
        except Exception:
            _logger.info("Failed to load template %r", template_txt, exc_info=True)
            return multi_mode and results or results[res_ids[0]]

        # prepare template variables
        records = self.env[model].browse(it for it in res_ids if it)  # filter to avoid browsing [None]
        res_to_rec = dict.fromkeys(res_ids, None)
        for record in records:
            res_to_rec[record.id] = record

        if self.env.context.get('website_id'):
            website = self.env['website'].browse(self.env.context.get('website_id'))
        else:
            website = self.env.user.backend_website_id

        variables = {
            'format_date': lambda date, format=False, context=self._context: format_date(self.env, date, format),
            'format_tz': lambda dt, tz=False, format=False, context=self._context: format_tz(self.env, dt, tz, format),
            'format_amount': lambda amount, currency, context=self._context: format_amount(self.env, amount, currency),
            'user': self.env.user,
            'ctx': self._context,  # context kw would clash with mako internals
            'website': website,
        }
        for res_id, record in res_to_rec.items():
            variables['object'] = record
            try:
                render_result = template.render(variables)
            except Exception:
                _logger.info("Failed to render template %r using values %r" % (template, variables), exc_info=True)
                raise UserError(_("Failed to render template %r using values %r") % (template, variables))
            if render_result == u"False":
                render_result = u""
            results[res_id] = render_result

        if post_process:
            for res_id, result in results.items():
                results[res_id] = self.render_post_process(result)

        return multi_mode and results or results[res_ids[0]]

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

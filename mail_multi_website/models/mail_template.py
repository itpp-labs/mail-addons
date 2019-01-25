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

    @api.multi
    def generate_email(self, res_ids, fields=None):
        """Remove mail_server_id when not set to recompute in _default_mail_server_id in mail.message"""
        multi_mode = True
        if isinstance(res_ids, pycompat.integer_types):
            multi_mode = False
        res = super(MailTemplate, self).generate_email(res_ids, fields=fields)
        if not multi_mode:
            list_of_dict = {0: res}
        else:
            list_of_dict = res

        for _unused, data in list_of_dict.items():
            if 'mail_server_id' in data and not data.get('mail_server_id'):
                del data['mail_server_id']

        return res

    @api.model
    def _render_template(self, template_txt, model, res_ids, post_process=False):
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

        variables = {
            'format_date': lambda date, format=False, context=self._context: format_date(self.env, date, format),
            'format_tz': lambda dt, tz=False, format=False, context=self._context: format_tz(self.env, dt, tz, format),
            'format_amount': lambda amount, currency, context=self._context: format_amount(self.env, amount, currency),
            'user': self.env.user,
            'ctx': self._context,  # context kw would clash with mako internals
        }

        # [NEW] Check website and company context
        company = self.env['res.company']  # empty value

        company_id = self.env.context.get('force_company')
        if company_id:
            company = self.env['res.company'].sudo().browse(company_id)

        if self.env.context.get('website_id'):
            website = self.env['website'].browse(self.env.context.get('website_id'))
        else:
            website = self.env.user.backend_website_id

        for res_id, record in res_to_rec.items():
            record_company = company
            if not record_company:
                if hasattr(record, 'company_id') and record.company_id:
                    record_company = record.company_id

            record_website = website
            if hasattr(record, 'website_id') and record.website_id:
                record_website = record.website_id

            if record_company and record_website \
               and record_website.company_id != company:
                # company and website are incompatible, so keep only website
                record_website = self.env['website']  # empty value

            record_context = dict(force_company=record_company.id, website_id=record_website.id)
            variables['object'] = record.with_context(**record_context)
            variables['website'] = record_website

            try:
                render_result = template.render(variables)
            except Exception:
                _logger.info("Failed to render template %r using values %r" % (template, variables), exc_info=True)
                raise UserError(_("Failed to render template %r using values %r") % (template, variables))
            if render_result == u"False":
                render_result = u""

            if post_process:
                render_result = self.with_context(**record_context).render_post_process(render_result)

            results[res_id] = render_result

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

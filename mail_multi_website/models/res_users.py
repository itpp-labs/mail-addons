# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)
FIELD_NAME = "email_multi_website"
FIELDS = ["signature"]
ALL_FIELDS = [FIELD_NAME] + FIELDS


class User(models.Model):

    _inherit = ["res.users", "website_dependent.mixin"]
    _name = "res.users"

    signature = fields.Html(company_dependent=True, website_dependent=True)

    # extra field to detach email field from res.partner
    email = fields.Char(related="email_multi_website", inherited=False)
    email_multi_website = fields.Char(company_dependent=True, website_dependent=True)

    @api.model
    def create(self, vals):
        res = super(User, self).create(vals)
        # make value company independent
        res._force_default(FIELD_NAME, vals.get("email"))
        for f in FIELDS:
            res._force_default(f, vals.get(f))
        return res

    @api.multi
    def write(self, vals):
        res = super(User, self).write(vals)
        # TODO: will it work with OCA's partner_firstname module?
        if any(k in vals for k in ["name", "email"] + FIELDS):
            for f in ALL_FIELDS:
                self._update_properties_label(f)
        return res

    def _auto_init(self):
        for f in FIELDS:
            self._auto_init_website_dependent(f)
        return super(User, self)._auto_init()

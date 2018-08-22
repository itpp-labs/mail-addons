# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from . import models


def post_init_hook(cr, registry):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    env.cr.execute("ALTER TABLE res_users ADD COLUMN email_multi_website VARCHAR")

    # fill new email column with values from partner
    for user in env['res.users'].with_context(active_test=False).search([]):
        email = user.partner_id.email
        if email:
            user._force_default('email_multi_website', email)


def uninstall_hook(cr, registry):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    # remove properties
    field = env.ref('base.field_res_users_email')
    env['ir.property'].search([('fields_id', '=', field.id)]).unlink()

    # No need to update base module as in ir_config_parameter_multi_company,
    # because email field is related in res.users originally and not needed to be recreated

    # copy emails from partner to user
    cr.execute("SELECT partner_id,email_multi_website FROM res_users")
    for partner_id, default_email in cr.fetchall():
        env['res.partner'].browse(partner_id).email = default_email

    # delete email_multi_website column in user
    cr.execute("ALTER TABLE res_users DROP COLUMN email_multi_website")

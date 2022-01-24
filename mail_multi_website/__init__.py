# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
from . import models
from . import wizard
from .tests import test_mail_model


def post_init_hook(cr, registry):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    env.cr.execute("ALTER TABLE res_users ADD COLUMN email VARCHAR")

    # fill new email column with values from partner
    for user in env["res.users"].with_context(active_test=False).search([]):
        email = user.partner_id.email
        if email:
            user._force_default("email", email)


def uninstall_hook(cr, registry):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    # remove properties
    field_ids = [
        env.ref("base.field_res_users__email").id,
        env.ref("base.field_res_users__signature").id,
        env.ref("mail.field_mail_template__body_html").id,
        env.ref("mail.field_mail_template__mail_server_id").id,
        env.ref("mail.field_mail_template__report_template").id,
    ]
    env["ir.property"].search([("fields_id", "in", field_ids)]).unlink()

    # copy emails from user to partner
    cr.execute("SELECT partner_id,email FROM res_users")
    for partner_id, default_email in cr.fetchall():
        env["res.partner"].browse(partner_id).email = default_email

    # email field is computed (related) and not needed if mail_multi_website is not installed
    env.cr.execute("ALTER TABLE res_users DROP COLUMN email")

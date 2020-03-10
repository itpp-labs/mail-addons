# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, tools


class MailThread(models.AbstractModel):

    _inherit = 'mail.thread'

    @api.model
    def create(self, vals):
        if vals.get("email_from"):
            vals["email_from"] = tools.decode_smtp_header(vals["email_from"])
        return super(MailThread, self).create(vals)

    def _message_post_after_hook(self, message, msg_vals):
        if message.email_from:
            message.email_from = tools.decode_smtp_header(message.email_from)
        super(MailThread, self)._message_post_after_hook(message, msg_vals)

# Copyright 2016 x620 <https://github.com/x620>
# Copyright 2017 Artyom Losev <https://github.com/ArtyomLosev>
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License MIT (https://opensource.org/licenses/MIT).
from odoo import fields, models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    is_private = fields.Boolean(string="Send Internal Message")


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        msg_vals = msg_vals if msg_vals else {}
        return super(MailThread, self)._notify_thread(message, msg_vals)

    def _notify_compute_recipients(self, message, msg_vals):
        recipient_data = super(MailThread, self)._notify_compute_recipients(
            message, msg_vals
        )
        if "is_private" in message._context:
            pids = (
                [x for x in msg_vals.get("partner_ids")]
                if "partner_ids" in msg_vals
                else self.sudo().partner_ids.ids
            )
            recipient_data["partners"] = [
                i for i in recipient_data["partners"] if i["id"] in pids
            ]
        return recipient_data


class MailMessage(models.Model):
    _inherit = "mail.message"

    is_private = fields.Boolean(string="Send Internal Message")

    def send_recepients_for_internal_message(self, model, domain):
        result = []
        default_resource = self.env[model].search(domain)
        follower_ids = default_resource.message_follower_ids
        internal_ids = self.get_internal_users_ids()

        recipient_ids = [r.partner_id for r in follower_ids if r.partner_id]

        for recipient in recipient_ids:
            result.append(
                {
                    "checked": recipient.user_ids.id in internal_ids,
                    "partner_id": recipient.id,
                    "full_name": recipient.name,
                    "name": recipient.name,
                    "email_address": recipient.email,
                    "reason": "Recipient",
                }
            )

        return result

    def get_internal_users_ids(self):
        internal_users_ids = self.env["res.users"].search([("share", "=", False)]).ids
        return internal_users_ids

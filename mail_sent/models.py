from odoo import api, fields, models


class MailMessage(models.Model):
    _inherit = "mail.message"

    sent = fields.Boolean(
        "Sent", compute="_compute_sent", help="Was message sent to someone", store=True
    )

    @api.depends("author_id", "partner_ids")
    def _compute_sent(self):
        for r in self:
            r_sudo = r.sudo()
            sent = (
                len(r_sudo.partner_ids) > 1
                or len(r_sudo.partner_ids) == 1
                and r_sudo.author_id
                and r_sudo.partner_ids[0].id != r_sudo.author_id.id
                or r_sudo.model == "mail.channel"
                and r_sudo.res_id
            )
            r.sent = sent

    @api.multi
    def message_format(self):
        message_values = super(MailMessage, self).message_format()
        message_index = {message["id"]: message for message in message_values}
        for item in self:
            msg = message_index.get(item.id)
            if msg:
                msg["sent"] = item.sent
        return message_values


class MailComposeMessage(models.TransientModel):

    _inherit = "mail.compose.message"
    sent = fields.Boolean("Sent", help="dummy field to fix inherit error")

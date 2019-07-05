from odoo import api, models, fields


class MailMessage(models.Model):
    _inherit = 'mail.message'

    sent = fields.Boolean('Sent', compute="_compute_sent", help='Was message sent to someone', store=True)

    @api.depends('author_id', 'partner_ids', 'channel_ids')
    def _compute_sent(self):
        for r in self:
            r_sudo = r.sudo()
            recipient_ids = r_sudo.partner_ids
            author_id = r_sudo.author_id
            res_id = r_sudo.model and r_sudo.res_id and r_sudo.env[r_sudo.model].browse(r_sudo.res_id)
            sent = author_id and (
                len(recipient_ids) > 1
                or (
                    len(recipient_ids) == 1
                    and recipient_ids[0].id != author_id.id
                )
                or (
                    len(r_sudo.channel_ids)
                )
                or (
                    res_id
                    and len(res_id.message_partner_ids - author_id) > 0
                )
            )
            r.sent = sent

    @api.multi
    def message_format(self):
        message_values = super(MailMessage, self).message_format()
        message_index = {message['id']: message for message in message_values}
        for item in self:
            msg = message_index.get(item.id)
            if msg:
                msg['sent'] = item.sent
        return message_values


class MailComposeMessage(models.TransientModel):

    _inherit = 'mail.compose.message'
    sent = fields.Boolean('Sent', help='dummy field to fix inherit error')

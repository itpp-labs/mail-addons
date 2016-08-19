# -*- coding: utf-8 -*-
from openerp import api, models, fields


class MailMessage(models.Model):
    _inherit = 'mail.message'

    sent = fields.Boolean('Sent', compute="_get_sent", help='Was message sent to someone', store=True)

    @api.one
    @api.depends('author_id', 'partner_ids')
    def _get_sent(self):
        self_sudo = self.sudo()
        self_sudo.sent = len(self_sudo.partner_ids) > 1 \
            or len(self_sudo.partner_ids) == 1 \
            and self_sudo.author_id \
            and self_sudo.partner_ids[0].id != self_sudo.author_id.id

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

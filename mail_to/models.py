# -*- coding: utf-8 -*-
from openerp import api, models, fields


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.multi
    def message_format(self):
        message_values = super(MailMessage, self).message_format()
        message_index = {message['id']: message for message in message_values}
        for item in self:
            msg = message_index.get(item.id)
            if msg:
                # TODO: найти получателей
                msg['recipient'] = 'Recipient'
        return message_values

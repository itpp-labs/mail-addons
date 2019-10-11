# -*- coding: utf-8 -*-
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, api


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.multi
    def message_format(self):
        messages_values = super(MailMessage, self).message_format()
        for i in messages_values:
            if i['channel_ids']:
                i['channel_names'] = self.env['mail.channel'].browse(i['channel_ids']).mapped(
                    lambda r: [r.id, '#' + r.display_name])

        return messages_values

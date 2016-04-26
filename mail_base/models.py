# -*- coding: utf-8 -*-

from openerp import api, models


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.multi
    def write(self, values):
        if values.get('needaction_partner_ids'):
            if not values.get('partner_ids'):
                values['partner_ids'] = []
            for triplet in values.get('needaction_partner_ids'):
                if triplet[0] == 6:
                    for id in triplet[2]:
                        values['partner_ids'].append((4, id, False))
        return super(MailMessage, self).write(values)

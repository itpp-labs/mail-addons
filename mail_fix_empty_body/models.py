# -*- coding: utf-8 -*-
from openerp import models


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def get_mail_values(self, cr, uid, wizard, res_ids, context=None):
        res = super(MailComposeMessage, self).get_mail_values(cr, uid, wizard, res_ids, context)
        for id, d in res.iteritems():
            d['body'] = d.get('body') or ''
        return res

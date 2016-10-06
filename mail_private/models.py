# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class MailComposeMessage(osv.TransientModel):
    _inherit = 'mail.compose.message'

    _columns = {
        'private': fields.boolean('Send Internal Message'),
    }

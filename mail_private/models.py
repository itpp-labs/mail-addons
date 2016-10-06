# -*- coding: utf-8 -*-

from openerp import api
from openerp.osv import osv, fields
from openerp import SUPERUSER_ID


class MailComposeMessage(osv.TransientModel):
    _inherit = 'mail.compose.message'

    _columns = {
        'private': fields.boolean('Send Internal Message'),
    }

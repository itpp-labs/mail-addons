# -*- coding: utf-8 -*-

from openerp import models, fields


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    private = fields.Boolean(string='Send Internal Message')

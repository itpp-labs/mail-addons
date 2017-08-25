# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    is_private = fields.Boolean(string='Send Internal Message')

    @api.multi
    def send_mail(self, auto_commit=False):
        for w in self:
            w.is_log = True if w.is_private else w.is_log
        super(MailComposeMessage, self).send_mail(auto_commit=False)

# -*- coding: utf-8 -*-
from openerp.osv import osv


class mail_mail(osv.Model):
    _inherit = 'mail.mail'

    def _get_partner_access_link(self, cr, uid, mail, partner=None, context=None):
        return None

# -*- coding: utf-8 -*-
# Copyright 2016 manawi <https://github.com/manawi>
# Copyright 2016 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl.html).

from openerp.osv import osv, fields
from openerp import api
from openerp.http import request


class MailComposeMessage(osv.TransientModel):
    _inherit = 'mail.compose.message'

    private = fields.boolean('Send Internal Message')

    @api.model
    def get_internal_users_ids(self, vals):
        cr, uid, context = request.cr, request.uid, request.context
        ids = self.pool['res.users'].search(cr, uid, [('share', '=', False)], context=context)
        return ids

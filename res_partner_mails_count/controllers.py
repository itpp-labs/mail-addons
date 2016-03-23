# -*- coding: utf-8 -*-
from openerp import http

# class ResPartnerMailsCount(http.Controller):
#     @http.route('/res_partner_mails_count/res_partner_mails_count/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/res_partner_mails_count/res_partner_mails_count/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('res_partner_mails_count.listing', {
#             'root': '/res_partner_mails_count/res_partner_mails_count',
#             'objects': http.request.env['res_partner_mails_count.res_partner_mails_count'].search([]),
#         })

#     @http.route('/res_partner_mails_count/res_partner_mails_count/objects/<model("res_partner_mails_count.res_partner_mails_count"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('res_partner_mails_count.object', {
#             'object': obj
#         })
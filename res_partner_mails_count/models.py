# -*- coding: utf-8 -*-

from openerp import models, fields, api

import logging


def getlogger(name):
    filename = 'test.log'
    logger = logging.getLogger(name)
    handler = logging.FileHandler(filename)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s: %(message)s')

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger

logger = getlogger(__name__)


class res_partner(models.Model):
    _inherit = 'res.partner'
    income = fields.Integer(compute="_income")
    sent = fields.Integer(compute="_sent")

    def _search_partner(self):
        return self.env['res.partner'].search([('user_ids', '=', self._uid)])

    def _search_letters(self, partner, param):
        letters = self.env['mail.message'].search([(param, '=', partner.id)])
        # logger.debug('partner.id: %s' % partner.id)
        # logger.debug('Income letters: %s' % letters)
        return letters

    @api.multi
    def _income(self):
        partner = self._search_partner()
        if partner:
            letters = self._search_letters(partner, 'partner_ids')
            partner.income = len(letters)

    @api.multi
    def _sent(self):
        partner = self._search_partner()
        if partner:
            letters = self._search_letters(partner, 'author_id')
            partner.sent = len(letters)


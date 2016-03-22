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
    mails_from = fields.Integer(compute="_mails_from")
    mails_to = fields.Integer(compute="_mails_to")

    @api.one
    def _mails_from(self):
        for r in self:
            letters = self.env['mail.message'].search([('partner_ids', 'in', r.id)])
            self.mails_from = len(letters)

    @api.one
    def _mails_to(self):
        for r in self:
            letters = self.env['mail.message'].search([('author_id', '=', r.id)])
            self.mails_to = len(letters)

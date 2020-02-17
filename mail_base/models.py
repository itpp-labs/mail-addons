# -*- coding: utf-8 -*-
# Copyright 2016 x620 <https://github.com/x620>
# Copyright 2017 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT)

from openerp import api, models


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.multi
    def write(self, values):
        if values.get("needaction_partner_ids"):
            if not values.get("partner_ids"):
                values["partner_ids"] = []
            for triplet in values.get("needaction_partner_ids"):
                if triplet[0] == 6:
                    for i in triplet[2]:
                        values["partner_ids"].append((4, i, False))
        return super(MailMessage, self).write(values)


class MailComposer(models.TransientModel):

    _inherit = "mail.compose.message"

    @api.multi
    def send_mail(self, auto_commit=False):
        res = super(MailComposer, self).send_mail(auto_commit=auto_commit)
        notification = {}
        self.env["bus.bus"].sendone(
            (self._cr.dbname, "mail_base.mail_sent"), notification
        )

        return res

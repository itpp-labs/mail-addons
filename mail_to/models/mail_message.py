# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# Copyright 2019 Eugene Molotov <https://it-projects.info/team/em230418>
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, models


class MailMessage(models.Model):
    _inherit = "mail.message"

    # взято с mail_base
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

    @api.multi
    def message_format(self):
        messages_values = super(MailMessage, self).message_format()
        for i in messages_values:
            if i["channel_ids"]:
                i["channel_names"] = (
                    self.env["mail.channel"]
                    .browse(i["channel_ids"])
                    .mapped(lambda r: [r.id, "#" + r.display_name])
                )

        return messages_values

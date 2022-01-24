# Copyright 2018,2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
# License OPL-1 (https://www.odoo.com/documentation/user/13.0/legal/licenses/licenses.html#odoo-apps) for derivative work.
from odoo import api, models, tools


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def _message_route_process(self, message, message_dict, routes):
        rcpt_tos = ",".join(
            [
                tools.decode_message_header(message, "Delivered-To"),
                tools.decode_message_header(message, "To"),
                tools.decode_message_header(message, "Cc"),
                tools.decode_message_header(message, "Resent-To"),
                tools.decode_message_header(message, "Resent-Cc"),
            ]
        )
        rcpt_tos_websiteparts = [
            e.split("@")[1].lower() for e in tools.email_split(rcpt_tos)
        ]
        website = (
            self.env["website"].sudo().search([("domain", "in", rcpt_tos_websiteparts)])
        )
        company = website.mapped("company_id")
        new_self = self.with_context(
            allowed_website_ids=website.ids, allowed_company_ids=company.ids
        )

        return super(MailThread, new_self)._message_route_process(
            message, message_dict, routes
        )

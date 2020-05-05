# Copyright 2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).

# pylint: disable=sql-injection
from odoo import api, fields, models


class MailMessage(models.Model):
    _inherit = "mail.message"

    sent = fields.Boolean(
        "Sent",
        compute="_compute_sent",
        help="Was message sent to someone",
        store=True,
        index=True,
    )

    @api.depends("author_id", "partner_ids", "channel_ids", "res_id", "model")
    def _compute_sent(self):
        to_check = set(self.ids)
        to_write = set()

        if to_check:
            # len(recipient_ids) > 1
            field = self._fields["partner_ids"]
            self.env.cr.execute(
                """
            SELECT {message_field}
            FROM (
                SELECT {message_field}, count(*) AS partner_count
                FROM {relation_table}
                WHERE {message_field} in %s
                GROUP BY {message_field}
            ) AS tmp WHERE partner_count > 1""".format(
                    message_field=field.column1,
                    partner_field=field.column2,
                    relation_table=field.relation,
                ),
                (tuple(to_check),),
            )
            ids = {r[0] for r in self.env.cr.fetchall()}
            to_check -= ids
            to_write |= ids

        if to_check:
            # (len(recipient_ids) == 1 and recipient_ids[0].id != author_id.id)
            self.env.cr.execute(
                """
            SELECT {message_field}
            FROM {relation_table} rel
                LEFT JOIN mail_message msg ON msg.id = rel.{message_field}
            WHERE rel.{partner_field} != msg.author_id AND rel.{message_field} in %s
            """.format(
                    message_field=field.column1,
                    partner_field=field.column2,
                    relation_table=field.relation,
                ),
                (tuple(to_check),),
            )
            ids = {r[0] for r in self.env.cr.fetchall()}
            to_check -= ids
            to_write |= ids

        if to_check:
            # (len(r_sudo.channel_ids))
            field = self._fields["channel_ids"]
            self.env.cr.execute(
                """
            SELECT {message_field}
            FROM (
                SELECT {message_field}, count(*) AS channel_count
                FROM {relation_table}
                WHERE {message_field} in %s
                GROUP BY {message_field}
            ) AS tmp WHERE channel_count > 0""".format(
                    message_field=field.column1,
                    channel_field=field.column2,
                    relation_table=field.relation,
                ),
                (tuple(to_check),),
            )
            ids = {r[0] for r in self.env.cr.fetchall()}
            to_check -= ids
            to_write |= ids

        self.browse(to_write).update({"sent": True})

    @api.multi
    def message_format(self):
        message_values = super(MailMessage, self).message_format()
        message_index = {message["id"]: message for message in message_values}
        for item in self:
            msg = message_index.get(item.id)
            if msg:
                msg["sent"] = item.sent
        return message_values


class MailComposeMessage(models.TransientModel):

    _inherit = "mail.compose.message"
    sent = fields.Boolean(help="dummy field to fix inherit error", store=False)

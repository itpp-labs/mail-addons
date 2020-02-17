# -*- coding: utf-8 -*-
# Copyright 2016 x620 <https://github.com/x620>
# Copyright 2016 manawi <https://github.com/manawi>
# Copyright 2017 Artyom Losev <https://github.com/ArtyomLosev>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    is_private = fields.Boolean(string="Send Internal Message")

    def get_internal_users_ids(self):
        internal_users_ids = self.env["res.users"].search([("share", "=", False)]).ids
        return internal_users_ids

    @api.multi
    def send_mail(self, auto_commit=False):
        for w in self:
            w.is_log = True if w.is_private else w.is_log
        super(MailComposeMessage, self).send_mail(auto_commit=False)


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.multi
    def _notify(self, force_send=False, send_after_commit=True, user_signature=True):
        self_sudo = self.sudo()
        if (
            "is_private" not in self_sudo._context
            or not self_sudo._context["is_private"]
        ):
            super(MailMessage, self)._notify(
                force_send, send_after_commit, user_signature
            )
        else:
            self._notify_mail_private(force_send, send_after_commit, user_signature)

    @api.multi
    def _notify_mail_private(
        self, force_send=False, send_after_commit=True, user_signature=True
    ):
        """ The method was partially copied from Odoo.
            In the current method, the way of getting channels for a private message is changed.
        """
        # have a sudoed copy to manipulate partners (public can go here with
        # website modules like forum / blog / ...

        # TDE CHECK: add partners / channels as arguments to be able to notify a message with / without computation ??
        self.ensure_one()  # tde: not sure, just for testinh, will see

        partners = self.env["res.partner"] | self.partner_ids
        channels = self.env["mail.channel"] | self.channel_ids

        # update message, with maybe custom values
        message_values = {
            "channel_ids": [(6, 0, channels.ids)],
            "needaction_partner_ids": [(6, 0, partners.ids)],
        }
        if (
            self.model
            and self.res_id
            and hasattr(self.env[self.model], "message_get_message_notify_values")
        ):
            message_values.update(
                self.env[self.model]
                .browse(self.res_id)
                .message_get_message_notify_values(self, message_values)
            )
        self.write(message_values)

        # notify partners and channels
        partners._notify(
            self,
            force_send=force_send,
            send_after_commit=send_after_commit,
            user_signature=user_signature,
        )
        channels._notify(self)

        # Discard cache, because child / parent allow reading and therefore
        # change access rights.
        if self.parent_id:
            self.parent_id.invalidate_cache()

        return True


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.multi
    @api.returns("self", lambda value: value.id)
    def message_post(
        self,
        body="",
        subject=None,
        message_type="notification",
        subtype=None,
        parent_id=False,
        attachments=None,
        content_subtype="html",
        **kwargs
    ):
        if "channel_ids" in kwargs:
            kwargs["channel_ids"] = [(4, pid) for pid in kwargs["channel_ids"]]
        return super(MailThread, self).message_post(
            body,
            subject,
            message_type,
            subtype,
            parent_id,
            attachments,
            content_subtype,
            **kwargs
        )

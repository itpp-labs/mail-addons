# Copyright 2016 x620 <https://github.com/x620>
# Copyright 2016 manawi <https://github.com/manawi>
# Copyright 2017 Artyom Losev <https://github.com/ArtyomLosev>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    is_private = fields.Boolean(string="Send Internal Message")


class MailMessage(models.Model):
    _inherit = "mail.message"

    is_private = fields.Boolean(string="Send Internal Message")

    def send_recepients_for_internal_message(self, model, domain):
        result = {"partners": [], "channels": []}
        default_resource = self.env[model].search(domain)
        follower_ids = default_resource.message_follower_ids

        recipient_ids = [r.partner_id for r in follower_ids if r.partner_id]
        channel_ids = [c.channel_id for c in follower_ids if c.channel_id]

        for recipient in recipient_ids:
            result["partners"].append(
                {
                    "checked": recipient.user_ids.id
                    and not any(recipient.user_ids.mapped("share")),
                    "partner_id": recipient.id,
                    "full_name": recipient.name,
                    "name": recipient.name,
                    "email_address": recipient.email,
                    "reason": "Recipient",
                }
            )

        for channel in channel_ids:
            result["channels"].append(
                {
                    "checked": True,
                    "channel_id": channel.id,
                    "full_name": channel.name,
                    "name": "# " + channel.name,
                    "reason": "Channel",
                }
            )
        return result

    @api.multi
    def _notify(self, force_send=False, send_after_commit=True, user_signature=True):
        self_sudo = self.sudo()
        if not self_sudo.is_private:
            super(MailMessage, self)._notify(
                force_send, send_after_commit, user_signature
            )
        else:
            self._notify_mail_private(force_send, send_after_commit, user_signature)

    @api.multi
    def _notify_mail_private(
        self, force_send=False, send_after_commit=True, user_signature=True
    ):
        """ Compute recipients to notify based on specified recipients and document
        followers. Delegate notification to partners to send emails and bus notifications
        and to channels to broadcast messages on channels """
        # have a sudoed copy to manipulate partners (public can go here with website modules like forum / blog / ... )
        self_sudo = self.sudo()

        self.ensure_one()
        partners_sudo = self_sudo.partner_ids
        channels_sudo = self_sudo.channel_ids

        # remove author from notified partners
        if not self._context.get("mail_notify_author", False) and self_sudo.author_id:
            partners_sudo = partners_sudo - self_sudo.author_id

        # update message, with maybe custom valuesz
        message_values = {}
        if channels_sudo:
            message_values["channel_ids"] = [(6, 0, channels_sudo.ids)]
        if partners_sudo:
            message_values["needaction_partner_ids"] = [(6, 0, partners_sudo.ids)]
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
        if message_values:
            self.write(message_values)

        # notify partners and channels
        # those methods are called as SUPERUSER because portal users posting messages
        # have no access to partner model. Maybe propagating a real uid could be necessary.
        email_channels = channels_sudo.filtered(lambda channel: channel.email_send)
        notif_partners = partners_sudo.filtered(
            lambda partner: "inbox" in partner.mapped("user_ids.notification_type")
        )
        if email_channels or partners_sudo - notif_partners:
            partners_sudo.search(
                [
                    "|",
                    ("id", "in", (partners_sudo - notif_partners).ids),
                    ("channel_ids", "in", email_channels.ids),
                    ("email", "!=", self_sudo.author_id.email or self_sudo.email_from),
                ]
            )._notify(
                self,
                force_send=force_send,
                send_after_commit=send_after_commit,
                user_signature=user_signature,
            )
        channels_sudo._notify(self)

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

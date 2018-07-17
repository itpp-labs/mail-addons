from odoo import models, fields, api


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    is_private = fields.Boolean(string='Send Internal Message')


class MailMessage(models.Model):
    _inherit = 'mail.message'

    is_private = fields.Boolean(string='Send Internal Message')

    def send_recepients_for_internal_message(self, model, domain):
        result = []
        default_resource = self.env[model].search(domain)
        follower_ids = default_resource.message_follower_ids

        recipient_ids = [r.partner_id for r in follower_ids if r.partner_id]
        # channel_ids = [c.channel_id for c in follower_ids if c.channel_id]

        for recipient in recipient_ids:
            result.append({
                'checked': len(recipient.user_ids) > 0,
                'partner_id': recipient.id,
                'full_name': recipient.name,
                'name': recipient.name,
                'email_address': recipient.email,
                'reason': 'Recipient'
            })

        # for channel in channel_ids:
        #     result.append({
        #         'checked': True,
        #         'channel_id': channel.id,
        #         'full_name': channel,
        #         'name': '# '+channel.name,
        #         'reason': 'Channel',
        #     })
        return result

    @api.multi
    def _notify(self, force_send=False, send_after_commit=True, user_signature=True):
        self_sudo = self.sudo()
        if not self_sudo.is_private:
            super(MailMessage, self)._notify(force_send, send_after_commit, user_signature)
        else:
            self._notify_mail_private(force_send, send_after_commit, user_signature)

    @api.multi
    def _notify_mail_private(self, force_send=False, send_after_commit=True, user_signature=True):
        """ Compute recipients to notify based on specified recipients and document
        followers. Delegate notification to partners to send emails and bus notifications
        and to channels to broadcast messages on channels """
        group_user = self.env.ref('base.group_user')
        # have a sudoed copy to manipulate partners (public can go here with website modules like forum / blog / ... )
        self_sudo = self.sudo()

        self.ensure_one()
        partners_sudo = self_sudo.partner_ids
        channels_sudo = self_sudo.channel_ids

        if self_sudo.subtype_id and self.model and self.res_id:
            followers = self_sudo.env['mail.followers'].search([
                ('res_model', '=', self.model),
                ('res_id', '=', self.res_id),
                ('subtype_ids', 'in', self_sudo.subtype_id.id),
            ])
            if self_sudo.subtype_id.internal:
                followers = followers.filtered(lambda fol: fol.channel_id or (fol.partner_id.user_ids and group_user in fol.partner_id.user_ids[0].mapped('groups_id')))
            channels_sudo |= followers.mapped('channel_id')

        # remove author from notified partners
        if not self._context.get('mail_notify_author', False) and self_sudo.author_id:
            partners_sudo = partners_sudo - self_sudo.author_id

        # update message, with maybe custom valuesz
        message_values = {}
        if channels_sudo:
            message_values['channel_ids'] = [(6, 0, channels_sudo.ids)]
        if partners_sudo:
            message_values['needaction_partner_ids'] = [(6, 0, partners_sudo.ids)]
        if self.model and self.res_id and hasattr(self.env[self.model], 'message_get_message_notify_values'):
            message_values.update(self.env[self.model].browse(self.res_id).message_get_message_notify_values(self, message_values))
        if message_values:
            self.write(message_values)

        # notify partners and channels
        # those methods are called as SUPERUSER because portal users posting messages
        # have no access to partner model. Maybe propagating a real uid could be necessary.
        email_channels = channels_sudo.filtered(lambda channel: channel.email_send)
        notif_partners = partners_sudo.filtered(lambda partner: 'inbox' in partner.mapped('user_ids.notification_type'))
        if email_channels or partners_sudo - notif_partners:
            partners_sudo.search([
                '|',
                ('id', 'in', (partners_sudo - notif_partners).ids),
                ('channel_ids', 'in', email_channels.ids),
                ('email', '!=', self_sudo.author_id.email or self_sudo.email_from),
            ])._notify(self, force_send=force_send, send_after_commit=send_after_commit, user_signature=user_signature)
        channels_sudo._notify(self)

        # Discard cache, because child / parent allow reading and therefore
        # change access rights.
        if self.parent_id:
            self.parent_id.invalidate_cache()

        return True

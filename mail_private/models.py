# Copyright 2016 x620 <https://github.com/x620>
# Copyright 2017 Artyom Losev <https://github.com/ArtyomLosev>
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl.html).
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
                'checked': recipient.user_ids.id and not any(recipient.user_ids.mapped('share')),
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
    def _notify(self, record, msg_vals, force_send=False, send_after_commit=True, model_description=False, mail_auto_delete=True):
        self_sudo = self.sudo()
        msg_vals = msg_vals if msg_vals else {}
        if 'is_private' not in self_sudo._context or not self_sudo._context['is_private']:
            return super(MailMessage, self)._notify(record, msg_vals, force_send, send_after_commit, model_description, mail_auto_delete)
        else:
            rdata = self._notify_compute_internal_recipients(record, msg_vals)
            return self._notify_recipients(rdata, record, msg_vals,
                                           force_send=force_send, send_after_commit=send_after_commit,
                                           model_description=model_description, mail_auto_delete=mail_auto_delete)

    @api.multi
    def _notify_compute_internal_recipients(self, record, msg_vals):
        recipient_data = super(MailMessage, self)._notify_compute_recipients(record, msg_vals)
        pids = [x[1] for x in msg_vals.get('partner_ids')] if 'partner_ids' in msg_vals else self.sudo().partner_ids.ids
        recipient_data['partners'] = [i for i in recipient_data['partners'] if i['id'] in pids]
        return recipient_data

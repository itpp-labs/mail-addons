# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    is_private = fields.Boolean(string='Send Internal Message')

    @api.multi
    def send_mail(self, auto_commit=False):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed. """
        for wizard in self:
            # Duplicate attachments linked to the email.template.
            # Indeed, basic mail.compose.message wizard duplicates attachments in mass
            # mailing mode. But in 'single post' mode, attachments of an email template
            # also have to be duplicated to avoid changing their ownership.
            if wizard.attachment_ids and wizard.composition_mode != 'mass_mail' and wizard.template_id:
                new_attachment_ids = []
                for attachment in wizard.attachment_ids:
                    if attachment in wizard.template_id.attachment_ids:
                        new_attachment_ids.append(attachment.copy({'res_model': 'mail.compose.message', 'res_id': wizard.id}).id)
                    else:
                        new_attachment_ids.append(attachment.id)
                    wizard.write({'attachment_ids': [(6, 0, new_attachment_ids)]})

            # Mass Mailing
            mass_mode = wizard.composition_mode in ('mass_mail', 'mass_post')

            Mail = self.env['mail.mail']
            ActiveModel = self.env[wizard.model if wizard.model else 'mail.thread']
            if wizard.template_id:
                # template user_signature is added when generating body_html
                # mass mailing: use template auto_delete value -> note, for emails mass mailing only
                Mail = Mail.with_context(mail_notify_user_signature=False)
                ActiveModel = ActiveModel.with_context(mail_notify_user_signature=False, mail_auto_delete=wizard.template_id.auto_delete)
            if not hasattr(ActiveModel, 'message_post'):
                ActiveModel = self.env['mail.thread'].with_context(thread_model=wizard.model)
            if wizard.composition_mode == 'mass_post':
                # do not send emails directly but use the queue instead
                # add context key to avoid subscribing the author
                ActiveModel = ActiveModel.with_context(mail_notify_force_send=False, mail_create_nosubscribe=True)
            # wizard works in batch mode: [res_id] or active_ids or active_domain
            if mass_mode and wizard.use_active_domain and wizard.model:
                res_ids = self.env[wizard.model].search(safe_eval(wizard.active_domain)).ids
            elif mass_mode and wizard.model and self._context.get('active_ids'):
                res_ids = self._context['active_ids']
            else:
                res_ids = [wizard.res_id]

            batch_size = int(self.env['ir.config_parameter'].sudo().get_param('mail.batch_size')) or self._batch_size
            sliced_res_ids = [res_ids[i:i + batch_size] for i in range(0, len(res_ids), batch_size)]

            if (wizard.composition_mode == 'mass_mail' 
            or wizard.is_log or 
            (wizard.composition_mode == 'mass_post' and not wizard.notify) 
            or wizard.is_private):  # log a note: subtype is False
                subtype_id = False
            elif wizard.subtype_id:
                subtype_id = wizard.subtype_id.id
            else:
                subtype_id = self.sudo().env.ref('mail.mt_comment', raise_if_not_found=False).id

            for res_ids in sliced_res_ids:
                batch_mails = Mail
                all_mail_values = wizard.get_mail_values(res_ids)
                for res_id, mail_values in all_mail_values.iteritems():
                    if wizard.composition_mode == 'mass_mail':
                        batch_mails |= Mail.create(mail_values)
                    else:
                        ActiveModel.browse(res_id).message_post(
                            message_type=wizard.message_type,
                            subtype_id=subtype_id,
                            **mail_values)

                if wizard.composition_mode == 'mass_mail':
                    batch_mails.send(auto_commit=auto_commit)

        return {'type': 'ir.actions.act_window_close'}

# -*- coding: utf-8 -*-
from openerp import api
from openerp import fields
from openerp import models
from openerp.tools import email_split
from openerp.tools.translate import _


class Wizard(models.TransientModel):
    _name = 'mail_move_message.wizard'

    def _model_selection(self):
        selection = []
        config_parameters = self.env['ir.config_parameter']
        model_names = config_parameters.get_param('mail_relocation_models')
        model_names = model_names.split(',') if model_names else []

        if 'default_message_id' in self.env.context:
            message = self.env['mail.message'].browse(self.env.context['default_message_id'])
            if message.model and message.model not in model_names:
                model_names.append(message.model)
            if message.moved_from_model and message.moved_from_model not in model_names:
                model_names.append(message.moved_from_model)
        if model_names:
            selection = [(m.model, m.display_name) for m in self.env['ir.model'].search([('model', 'in', model_names)])]

        return selection

    @api.model
    def default_get(self, fields_list):
        res = super(Wizard, self).default_get(fields_list)

        model_fields = self.fields_get()
        if model_fields['model']['selection']:
            res['model'] = model_fields['model']['selection'] and model_fields['model']['selection'][0][0]

        if 'message_id' in res:
            message = self.env['mail.message'].browse(res['message_id'])
            email_from = message.email_from
            parts = email_split(email_from.replace(' ', ','))
            if parts:
                email = parts[0]
                name = email_from.find(email) != -1 and email_from[:email_from.index(email)].replace('"', '').replace('<', '').strip() or email_from
            else:
                name, email = email_from
            res['message_name_from'] = name
            res['message_email_from'] = email

            res['partner_id'] = message.author_id.id
            if message.author_id and self.env.uid not in [u.id for u in message.author_id.user_ids]:
                res['filter_by_partner'] = True
            if message.author_id and res.get('model'):
                res_id = self.env[res['model']].search([], order='id desc', limit=1)
                res['res_id'] = res_id and res_id[0].id

        config_parameters = self.env['ir.config_parameter']
        res['move_followers'] = config_parameters.get_param('mail_relocation_move_followers')

        res['uid'] = self.env.uid

        return res

    message_id = fields.Many2one('mail.message', string='Message')
    message_body = fields.Html(related='message_id.body', string='Message to move', readonly=True)
    message_from = fields.Char(related='message_id.email_from', string='From', readonly=True)
    message_subject = fields.Char(related='message_id.subject', string='Subject', readonly=True)
    message_moved_by_message_id = fields.Many2one('mail.message', related='message_id.moved_by_message_id', string='Moved with', readonly=True)
    message_moved_by_user_id = fields.Many2one('res.users', related='message_id.moved_by_user_id', string='Moved by', readonly=True)
    message_is_moved = fields.Boolean(string='Is Moved', related='message_id.is_moved', readonly=True)
    parent_id = fields.Many2one('mail.message', string='Search by name', )
    model = fields.Selection(_model_selection, string='Model')
    res_id = fields.Integer(string='Record')
    can_move = fields.Boolean('Can move', compute='get_can_move')
    move_back = fields.Boolean('MOVE TO ORIGIN', help='Move  message and submessages to original place')
    partner_id = fields.Many2one('res.partner', string='Author')
    filter_by_partner = fields.Boolean('Filter Records by partner')
    message_email_from = fields.Char()
    message_name_from = fields.Char()
    # FIXME message_to_read should be True even if current message or any his childs are unread
    message_to_read = fields.Boolean(related='message_id.needaction')
    uid = fields.Integer()
    move_followers = fields.Boolean(
        'Move Followers',
        help="Add followers of current record to a new record.\n"
             "You must use this option, if new record has restricted access.\n"
             "You can change default value for this option at Settings/System Parameters")

    @api.depends('message_id')
    @api.one
    def get_can_move(self):
        # message was not moved before OR message is a top message of previous move
        self.can_move = not self.message_id.moved_by_message_id or self.message_id.moved_by_message_id.id == self.message_id.id

    @api.onchange('move_back')
    def on_change_move_back(self):
        if not self.move_back:
            return
        self.parent_id = self.message_id.moved_from_parent_id
        model = self.message_id.moved_from_model
        if self.message_id.is_moved:
            self.model = model
            self.res_id = self.message_id.moved_from_res_id

    @api.onchange('parent_id', 'res_id', 'model')
    def update_move_back(self):
        model = self.message_id.moved_from_model
        self.move_back = self.parent_id == self.message_id.moved_from_parent_id \
            and self.res_id == self.message_id.moved_from_res_id \
            and (self.model == model or (not self.model and not model))

    @api.onchange('parent_id')
    def on_change_parent_id(self):
        if self.parent_id and self.parent_id.model:
            self.model = self.parent_id.model
            self.res_id = self.parent_id.res_id
        else:
            self.model = None
            self.res_id = None

    @api.onchange('model', 'filter_by_partner', 'partner_id')
    def on_change_partner(self):
        domain = {'res_id': [('id', '!=', self.message_id.res_id)]}
        if self.model and self.filter_by_partner and self.partner_id:
            fields = self.env[self.model].fields_get(False)
            contact_field = False
            for n, f in fields.iteritems():
                if f['type'] == 'many2one' and f['relation'] == 'res.partner':
                    contact_field = n
                    break
            if contact_field:
                domain['res_id'].append((contact_field, '=', self.partner_id.id))
        if self.model:
            res_id = self.env[self.model].search(domain['res_id'], order='id desc', limit=1)
            self.res_id = res_id and res_id[0].id
        else:
            self.res_id = None
        return {'domain': domain}

    @api.one
    def check_access(self):
        cr = self._cr
        uid = self.env.user.id
        operation = 'write'
        context = self._context

        if not (self.model and self.res_id):
            return True
        model_obj = self.pool[self.model]
        mids = model_obj.exists(cr, uid, [self.res_id])
        if hasattr(model_obj, 'check_mail_message_access'):
            model_obj.check_mail_message_access(cr, uid, mids, operation, context=context)
        else:
            self.pool['mail.thread'].check_mail_message_access(cr, uid, mids, operation, model_obj=model_obj, context=context)

    @api.multi
    def open_moved_by_message_id(self):
        message_id = None
        for r in self:
            message_id = r.message_moved_by_message_id.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail_move_message.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [[False, 'form']],
            'target': 'new',
            'context': {'default_message_id': message_id},
        }

    @api.multi
    def move(self):
        for r in self:
            r.check_access()
            if not r.parent_id or not (r.parent_id.model == r.model and
                                       r.parent_id.res_id == r.res_id):
                # link with the first message of record
                parent = self.env['mail.message'].search([('model', '=', r.model), ('res_id', '=', r.res_id)], order='id', limit=1)
                r.parent_id = parent.id or None

            r.message_id.move(r.parent_id.id, r.res_id, r.model, r.move_back, r.move_followers)

        if not (r.model and r.res_id):
            r.message_id.needaction = False
            return {
                'type': 'ir.actions.client',
                'name': 'All messages',
                'tag': 'reload',
            }
        return {
            'name': _('Record'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': r.model,
            'res_id': r.res_id,
            'views': [(False, 'form')],
            'type': 'ir.actions.act_window',
        }

    @api.one
    def delete(self):
        msg_id = self.message_id.id

        # Send notification
        notification = {'id': msg_id}
        self.env['bus.bus'].sendone((self._cr.dbname, 'mail_move_message.delete_message'), notification)

        self.message_id.unlink()
        return {}

    @api.model
    def create_partner(self, message_id, relation, partner_id, message_name_from, message_email_from):
        model = self.env[relation]
        message = self.env['mail.message'].browse(message_id)
        if not partner_id and message_name_from:
            partner_id = self.env['res.partner'].with_context({'update_message_author': True}).create({
                'name': message_name_from,
                'email': message_email_from
            }).id

        context = {'partner_id': partner_id}
        if model._rec_name:
            context.update({'default_%s' % model._rec_name: message.subject})

        fields = model.fields_get()
        contact_field = False
        for n, f in fields.iteritems():
            if f['type'] == 'many2one' and f['relation'] == 'res.partner':
                contact_field = n
                break
        if contact_field:
            context.update({'default_%s' % contact_field: partner_id})
        return context

    @api.one
    def read_close(self):
        self.message_id.set_message_done()
        self.message_id.child_ids.set_message_done()
        return {'type': 'ir.actions.act_window_close'}


class MailMessage(models.Model):
    _inherit = 'mail.message'

    is_moved = fields.Boolean('Is moved')
    moved_from_res_id = fields.Integer('Related Document ID (Original)')
    moved_from_model = fields.Char('Related Document Model (Original)')
    moved_from_parent_id = fields.Many2one('mail.message', 'Parent Message (Original)', ondelete='set null')
    moved_by_message_id = fields.Many2one('mail.message', 'Moved by message', ondelete='set null', help='Top message, that initate moving this message')
    moved_by_user_id = fields.Many2one('res.users', 'Moved by user', ondelete='set null')
    all_child_ids = fields.One2many('mail.message', string='All childs', compute='_get_all_childs', help='all childs, including subchilds')

    @api.one
    def _get_all_childs(self, include_myself=True):
        ids = []
        if include_myself:
            ids.append(self.id)
        while True:
            new_ids = self.search([('parent_id', 'in', ids), ('id', 'not in', ids)]).ids
            if new_ids:
                ids = ids + new_ids
                continue
            break
        moved_childs = self.search([('moved_by_message_id', '=', self.id)]).ids
        self.all_child_ids = ids + moved_childs

    @api.multi
    def move_followers(self, model, ids):
        fol_obj = self.env['mail.followers']
        for message in self:
            followers = fol_obj.sudo().search([('res_model', '=', message.model),
                                               ('res_id', '=', message.res_id)])
            for f in followers:
                self.env[model].browse(ids).message_subscribe([f.partner_id.id], [s.id for s in f.subtype_ids])

    @api.one
    def move(self, parent_id, res_id, model, move_back, move_followers=False):
        if parent_id == res_id:
            return
        vals = {}
        if move_back:
            # clear variables if we move everything back
            vals['is_moved'] = False
            vals['moved_by_user_id'] = None
            vals['moved_by_message_id'] = None

            vals['moved_from_res_id'] = None
            vals['moved_from_model'] = None
            vals['moved_from_parent_id'] = None
        else:
            vals['parent_id'] = parent_id
            vals['res_id'] = res_id
            vals['model'] = model

            vals['is_moved'] = True
            vals['moved_by_user_id'] = self.env.user.id
            vals['moved_by_message_id'] = self.id

        # Update record_name in message
        vals['record_name'] = self._get_record_name(vals)

        for r in self.all_child_ids:
            r_vals = vals.copy()
            if not r.is_moved:
                # moved_from_* variables contain not last, but original
                # reference
                r_vals['moved_from_parent_id'] = r.parent_id.id
                r_vals['moved_from_res_id'] = r.res_id
                r_vals['moved_from_model'] = r.model
            elif move_back:
                r_vals['parent_id'] = r.moved_from_parent_id.id
                r_vals['res_id'] = r.moved_from_res_id
                r_vals['model'] = r.moved_from_model
            # print 'update message', r, r_vals
            if move_followers:
                r.sudo().move_followers(r_vals.get('model'), r_vals.get('res_id'))
            r.sudo().write(r_vals)
            r.attachment_ids.sudo().write({
                'res_id': r_vals.get('res_id'),
                'res_model': r_vals.get('model')
            })

        # Send notification
        notification = {
            'id': self.id,
            'res_id': vals.get('res_id'),
            'model': vals.get('model'),
            'is_moved': vals['is_moved'],
            'record_name': vals['record_name']
        }
        self.env['bus.bus'].sendone((self._cr.dbname, 'mail_move_message'), notification)

    def name_get(self, cr, uid, ids, context=None):
        if not (context or {}).get('extended_name'):
            return super(MailMessage, self).name_get(cr, uid, ids, context=context)
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['record_name', 'model', 'res_id'], context=context)
        res = []
        for record in reads:
            name = record['record_name'] or ''
            extended_name = '   [%s] ID %s' % (record.get('model', 'UNDEF'), record.get('res_id', 'UNDEF'))
            res.append((record['id'], name + extended_name))
        return res

    def _message_read_dict(self, cr, uid, message, parent_id=False, context=None):
        res = super(MailMessage, self)._message_read_dict(cr, uid, message, parent_id, context)
        res['is_moved'] = message.is_moved
        return res

    @api.multi
    def message_format(self):
        message_values = super(MailMessage, self).message_format()
        message_index = {message['id']: message for message in message_values}
        for item in self:
            msg = message_index.get(item.id)
            if msg:
                msg['is_moved'] = item.is_moved
        return message_values


class MailMoveMessageConfiguration(models.TransientModel):
    _name = 'mail_move_message.config.settings'
    _inherit = 'res.config.settings'

    model_ids = fields.Many2many(comodel_name='ir.model', string='Models')
    move_followers = fields.Boolean('Move Followers')

    @api.model
    def get_default_move_message_configs(self, fields):
        config_parameters = self.env['ir.config_parameter']
        model_obj = self.env['ir.model']
        model_names = config_parameters.get_param('mail_relocation_models')
        if not model_names:
            return {}
        model_names = model_names.split(',')
        model_ids = model_obj.search([('model', 'in', model_names)])
        return {
            'model_ids': [m.id for m in model_ids],
            'move_followers': config_parameters.get_param('mail_relocation_move_followers')
        }

    @api.multi
    def set_move_message_configs(self):
        config_parameters = self.env['ir.config_parameter']
        model_names = ''
        for record in self:
            model_names = ','.join([m.model for m in record.model_ids])
            config_parameters.set_param('mail_relocation_models', model_names)
            config_parameters.set_param('mail_relocation_move_followers', record.move_followers or '')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if 'update_message_author' in self.env.context and 'email' in vals:
            mail_message_obj = self.env['mail.message']
            # Escape special SQL characters in email_address to avoid invalid matches
            email_address = (vals['email'].replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_'))
            email_brackets = "<%s>" % email_address
            messages = mail_message_obj.search([
                '|',
                ('email_from', '=ilike', email_address),
                ('email_from', 'ilike', email_brackets),
                ('author_id', '=', False)
            ])
            if messages:
                messages.sudo().write({'author_id': res.id})
        return res

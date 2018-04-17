odoo.define('mail_move_message.relocate', function (require) {
    "use strict";

    var bus = require('bus.bus').bus;
    var chat_manager = require('mail_base.base').chat_manager;
    var thread = require('mail.ChatThread');
    var chatter = require('mail.Chatter');
    var rpc = require('web.rpc');
    var view_dialogs = require('web.view_dialogs');
    var field_utils_format = require('web.field_utils').format;
    var BasicRenderer = require('web.BasicRenderer');
    var core = require('web.core');
    var form_widget = require('web.FormRenderer');
    var session = require('web.Session');
    var FormController = require('web.FormController');
    var FormView = require('web.FormView');

    var _t = core._t;

    thread.include({
        init: function(){
            this._super.apply(this, arguments);
            // Add click reaction in the events of the thread object
            this.events['click .oe_move'] = function(event) {
                var message_id = $(event.currentTarget).data('message-id');
                this.trigger("move_message", message_id);
            };
        },
        on_move_message: function(message_id){
            var action = {
                name: _t('Relocate Message'),
                type: 'ir.actions.act_window',
                res_model: 'mail_move_message.wizard',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: {'default_message_id': message_id}
            };

            this.do_action(action, {
                'on_close': function(){}
            });
        }
    });

    chatter.include({
        start: function() {
            var result = this._super.apply(this, arguments);
            // For show wizard in the form
            var chatter_thread = new thread();
            chatter_thread.on('move_message', this, chatter_thread.on_move_message);
            return $.when(result).done(function() {});
        }
    });

//    var _super_session = session.prototype;
//    session.include({
//        rpc: function(url, params, options){
//            url = url || ''
//            return _super_session.rpc.apply(this, arguments);
//        }
//    });

//    session_super = new session();
//    session_super_rpc = session_super.rpc;
//    session.include({
//        rpc: function(url, params, options){
//            url = url || '';
//            session_super_rpc.apply(this, [url, params, options])
//        }
//    });

//    var session_super_rpc = session.rpc;
//    session.rpc = function(url, params, options){
//        url = url || '';
//        return session_super_rpc(url, params, options);
//    }

    var ChatAction = core.action_registry.get('mail.chat.instant_messaging');
    ChatAction.include({
        start: function() {
            var result = this._super.apply(this, arguments);
            // For show wizard in the channels
            this.thread.on('move_message', this, this.thread.on_move_message);
            return $.when(result).done(function() {});
        }
    });

    // override methods of chat manager
    var chat_manager_super_make_message = chat_manager.make_message;
    chat_manager.make_message = function(data){
        var msg = chat_manager_super_make_message(data);
        // Mark msg as moved after reload
        msg.is_moved = data.is_moved || false;
        return msg;
    };
    var chat_manager_super_on_notification = chat_manager.on_notification;
    chat_manager.on_notification = function(notifications){
        chat_manager_super_on_notification(notifications);
        var self = this;
        _.each(notifications, function (notification) {
            var model = notification[0][1];
            var message_id = notification[1].id;
            var message = chat_manager.get_message(message_id);
            if (model === 'mail_move_message' && message) {
                message.res_id = notification[1].res_id;
                message.model = notification[1].model;
                message.record_name = notification[1].record_name;
                // Mark message as moved after move
                message.is_moved = notification[1].is_moved;
                // Update cache and accordingly message in the thread
                self.add_to_cache(message, []);
                // Call thread.on_update_message(message)
                chat_manager.bus.trigger('update_message', message);
            } else if (model === 'mail_move_message.delete_message') {
                self.remove_from_cache(message, []);
                chat_manager.bus.trigger('update_message', message);
            }
        });
    };

    var field_utils_super_formatMany2one = field_utils_format.many2one;
    field_utils_format.many2one = function(value, field, options) {
        if (value && typeof value === 'number'){
            return '';
        }
        return field_utils_super_formatMany2one(value, field, options)
    }

    form_widget.include({
//        on_click: function(){
//            if(this.node.attrs.special == 'quick_create'){
//                var self = this;
//                var related_field = this.field_manager.fields[this.node.attrs.field];
//                var context_built = $.Deferred();
//                if(this.node.attrs.use_for_mail_move_message) {
//                    var model = new Model(this.view.dataset.model);
//                    var partner_id = self.field_manager.fields.partner_id.get_value();
//                    var message_name_from = self.field_manager.fields.message_name_from.get_value();
//                    var message_email_from = self.field_manager.fields.message_email_from.get_value();
//                    context_built = model.call('create_partner', [
//                            self.view.dataset.context.default_message_id,
//                            related_field.field.relation,
//                            partner_id,
//                            message_name_from,
//                            message_email_from
//                        ]);
//                    //rpc.query({
//                    //    model: 'stock.picking.type',
//                    //    method: 'search_read',
//                    //    args: []
//                    //})
//                }
//                else {
//                    context_built.resolve(this.build_context());
//                }
//                $.when(context_built).pipe(function (context) {
//                    if(self.node.attrs.use_for_mail_move_message) {
//                        self.field_manager.fields.partner_id.set_value(context.partner_id);
//                    }
//                    var dialog = new view_dialogs.FormViewDialog(self, {
//                        res_model: related_field.field.relation,
//                        res_id: false,
//                        context: context,
//                        title: _t("Create new record")
//                    }).open();
//                    dialog.on('closed', self, function () {
//                        self.force_disabled = false;
//                        self.check_disable();
//                    });
//                    dialog.on('create_completed', self, function(id) {
//                        related_field.set_value(id);
//                        if(self.field_manager.fields.filter_by_partner) {
//                            self.field_manager.fields.filter_by_partner.set_value(true);
//                        }
//                    });
//                });
//            }
//            else {
//                this._super.apply(this, arguments);
//            }
//        },
//
        _addOnClickAction: function ($el, node) {
            var self = this;
            if (!this.nodes) {
                this.nodes = [];
            }
            this.nodes.push();
            if (node.attrs && node.attrs.special == 'quick_create') {
                $el.click(function () {
//                    if(self.node.attrs.special == 'quick_create'){
                        //var self = this;
//                        var related_field = self.field_manager.fields[self.node.attrs.field];
                        var related_field = node.attrs.field;
                        var context_built = $.Deferred();
                        if(node.attrs.use_for_mail_move_message) {
console.log(new FormController())
console.log(new FormView())
//                            var model = new Model(self.view.dataset.model);
                            var partner_id = self.field_manager.fields.partner_id.get_value();
                            var message_name_from = self.field_manager.fields.message_name_from.get_value();
                            var message_email_from = self.field_manager.fields.message_email_from.get_value();
//                            context_built = model.call('create_partner', [
//                                    self.view.dataset.context.default_message_id,
//                                    related_field.field.relation,
//                                    partner_id,
//                                    message_name_from,
//                                    message_email_from
//                                ]);
                            context_built = rpc.query({
                                model: 'res.partner',
                                method: 'create_partner',
                                args: [
                                    self.view.dataset.context.default_message_id,
                                    related_field.field.relation,
                                    partner_id,
                                    message_name_from,
                                    message_email_from
                                ]
                            })
                        }
                        else {
//                            context_built.resolve(self.build_context());
                            context_built.resolve();
                        }
                        $.when(context_built).pipe(function (context) {
                            if(node.attrs.use_for_mail_move_message) {
                                self.field_manager.fields.partner_id.set_value(context.partner_id);
                            }
                            var dialog = new view_dialogs.FormViewDialog(self, {
                                res_model: related_field.field.relation,
                                res_id: false,
                                context: context,
                                title: _t("Create new record")
                            }).open();
                            dialog.on('closed', self, function () {
                                self.force_disabled = false;
                                self.check_disable();
                            });
                            dialog.on('create_completed', self, function(id) {
                                related_field.set_value(id);
                                if(self.field_manager.fields.filter_by_partner) {
                                    self.field_manager.fields.filter_by_partner.set_value(true);
                                }
                            });
                        });
//                    }
//                    else {
//                        self._super.apply(self, arguments);
//                    }
                });
            }
        },
    });
});

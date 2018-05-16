odoo.define('mail_move_message.relocate', function (require) {
    "use strict";

    var bus = require('bus.bus').bus;
    var chat_manager = require('mail_base.base').chat_manager;
    var thread = require('mail.ChatThread');
    var chatter = require('mail.Chatter');
    var rpc = require('web.rpc');
    var Basicmodel = require('web.BasicModel');
    var view_dialogs = require('web.view_dialogs');
    var field_utils_format = require('web.field_utils').format;
    var BasicRenderer = require('web.BasicRenderer');
    var core = require('web.core');
    var form_widget = require('web.FormRenderer');
    var session = require('web.Session');
    var FormController = require('web.FormController');
    var FormView = require('web.FormView');
    var registry = require('web.field_registry');

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
            return this.do_action(action);
//            this.do_action(action, {
//                'on_close': function(){}
//            });
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

    Basicmodel.include({
        applyDefaultValues: function (recordID, values, options) {
            console.log('sdsad')
            delete values.model
            return this._super(recordID, values, options)
        }
    });

//    form_widget.extend({
//        _addOnClickAction: function ($el, node) {
//            var self = this;
//            if (!this.nodes) {
//                this.nodes = [];
//            }
//            this.nodes.push();
//            if (node.attrs && node.attrs.special == 'quick_create') {
//                $el.click(function () {
//                    if(self.node.attrs.special == 'quick_create'){
//                        var related_field = self.state.data.model;
//                        var context_built = $.Deferred();
//                        console.log(core)
//                        if(node.attrs.use_for_mail_move_message) {
//                            console.log(registry)
//                            //var model = new Model(self.view.dataset.model);
//                            var partner_id = self.state.data.partner_id;
//                            var message_name_from = self.state.data.message_name_from;
//                            var message_email_from = self.state.data.message_email_from;
//                            context_built = rpc.query({
//                                model: 'res.partner',
//                                method: 'create_partner',
//                                args: [
//                                    self.state.data.message_id.context.default_message_id,
//                                    related_field,
//                                    partner_id.res_id,
//                                    message_name_from,
//                                    message_email_from
//                                ]
//                            });
//                        }
//                        else {
//                            //context_built.resolve(self.build_context());
//                            context_built.resolve();
//                        }
//                        $.when(context_built).pipe(function (context) {
//                            if(node.attrs.use_for_mail_move_message) {
//                                self.field_manager.fields.partner_id.set_value(context.partner_id);
//                            }
//                            var dialog = new view_dialogs.FormViewDialog(self, {
//                                res_model: related_field.field.relation,
//                                res_id: false,
//                                context: context,
//                                title: _t("Create new record")
//                            }).open();
//                            dialog.on('closed', self, function () {
//                                self.force_disabled = false;
//                                self.check_disable();
//                            });
//                            dialog.on('create_completed', self, function(id) {
//                                related_field.set_value(id);
//                                if(self.field_manager.fields.filter_by_partner) {
//                                    self.field_manager.fields.filter_by_partner.set_value(true);
//                                }
//                            });
//                        });
//                    }
//                });
//            }
//            else {
//                self._super.apply($el, node);
//            }
//        },
//    });
});

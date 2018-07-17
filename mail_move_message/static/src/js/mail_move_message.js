/*Copyright 2016 Ildar Nasyrov <https://it-projects.info/team/iledarn>
# Copyright 2016 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2016 Pavel Romanchenko
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */

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
            this.do_action(action, {
                'on_close': function(){}
            });
        }
    });

    chatter.include({
        start: function() {
            var result = this._super.apply(this, arguments);
            // For show wizard in the form
            if (this.fields.thread && this.fields.thread.thread) {
                var thread = this.fields.thread.thread;
                thread.on('move_message', this, thread.on_move_message);
            }
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
                _.each(message.channel_ids, function(ch){
                    self.remove_message_from_channel(ch, message);
                })
                chat_manager.bus.trigger('update_message', message);
            }
        });
    };

    Basicmodel.include({
        applyDefaultValues: function (recordID, values, options) {
            delete values.model
            return this._super(recordID, values, options)
        }
    });
});

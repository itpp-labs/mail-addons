odoo.define('mail_private', function (require) {
'use strict';

var base_obj = require('mail_base.base');

var core = require('web.core');
var Chatter = require('mail.Chatter');
var chat_manager = require('mail.chat_manager');
var session = require('web.session');
var Model = require('web.Model');


    Chatter.include({
        init: function () {
            this._super.apply(this, arguments);
            this.private = false;
            this.events['click .oe_compose_post_private'] = 'on_open_composer_private_message';
        },
//        on_compose_fullmail: function (default_composition_mode) {
//            var self = this;
//            if(!this.do_check_attachment_upload()) {
//                return false;
//            }
//            var recipient_done = $.Deferred();
//            if (this.is_log) {
//                recipient_done.resolve([]);
//            }
//            else {
//                recipient_done = this.check_recipient_partners();
//            }
//            $.when(recipient_done).done(function (partner_ids) {
//                var context = {
//                    'default_parent_id': self.id,
//                    'default_body': mail.ChatterUtils.get_text2html(self.$el ? (self.$el.find('textarea:not(.oe_compact)').val() || '') : ''),
//                    'default_attachment_ids': _.map(self.attachment_ids, function (file) {return file.id;}),
//                    'default_partner_ids': partner_ids,
//                    'default_is_log': self.is_log,
//                    'default_private': self.private,
//                    'mail_post_autofollow': true,
//                    'mail_post_autofollow_partner_ids': partner_ids,
//                    'is_private': self.is_private
//                };
//                if (default_composition_mode != 'reply' && self.context.default_model && self.context.default_res_id) {
//                    context.default_model = self.context.default_model;
//                    context.default_res_id = self.context.default_res_id;
//                }
//
//                var action = {
//                    type: 'ir.actions.act_window',
//                    res_model: 'mail.compose.message',
//                    view_mode: 'form',
//                    view_type: 'form',
//                    views: [[false, 'form']],
//                    target: 'new',
//                    context: context,
//                };
//
//                self.do_action(action, {
//                    'on_close': function(){ !self.parent_thread.options.view_inbox && self.parent_thread.message_fetch(); }
//                });
//                self.on_cancel();
//            });
//
//        },

//        do_send_message_post: function (partner_ids, log) {
//            var self = this;
//            var values = {
//                'body': this.$('textarea').val(),
//                'subject': false,
//                'parent_id': this.context.default_parent_id,
//                'attachment_ids': _.map(this.attachment_ids, function (file) {return file.id;}),
//                'partner_ids': partner_ids,
//                'context': _.extend(this.parent_thread.context, {
//                    'mail_post_autofollow': true,
//                    'mail_post_autofollow_partner_ids': partner_ids,
//                    'default_private': self.private
//                }),
//                'type': 'comment',
//                'content_subtype': 'plaintext',
//            };
//            if (log || self.private) {
//                values.subtype = false;
//            }
//            else {
//                values.subtype = 'mail.mt_comment';
//            }
//            this.parent_thread.ds_thread._model.call('message_post', [this.context.default_res_id], values).done(function (message_id) {
//                var thread = self.parent_thread;
//                var root = thread == self.options.root_thread;
//                if (self.options.display_indented_thread < self.thread_level && thread.parent_message) {
//                    var thread = thread.parent_message.parent_thread;
//                }
//                // create object and attach to the thread object
//                thread.message_fetch([["id", "=", message_id]], false, [message_id], function (arg, data) {
//                    var message = thread.create_message_object( data.slice(-1)[0] );
//                    // insert the message on dom
//                    thread.insert_message( message, root ? undefined : self.$el, root );
//                });
//                self.on_cancel();
//                self.flag_post = false;
//            });
//        },

        on_post_message: function (message) {
        var self = this;
        var options = {model: this.model, res_id: this.res_id};
        chat_manager
            .post_message(message, options)
            .then(function () {
                self.close_composer();
                if (message.partner_ids.length) {
                    self.refresh_followers(); // refresh followers' list
                }
            })
            .fail(function () {
                // todo: display notification
            });
    },

//        on_toggle_quick_composer: function (event) {
//            if (event.target.className == 'oe_compose_post') {
//                this.recipients = [];
//                this.private = false;
//            }
//            this._super.apply(this, arguments);
//        },

        on_open_composer_private_message: function (event) {
            var self = this;
            this.get_recipients_for_internal_message().then(function (data) {
                var private_message = 'private_message';
                self.recipients_for_internal_message = [];
                self.recipients_for_internal_message = data;
                self.open_composer(private_message);
            });
        },

        open_composer: function (options) {
            var self = this;
            this._super.apply(this, arguments)
            if (options === 'private_message') {
                //Clear existing suggested partners

                for (var i=0; i<self.recipients_for_internal_message.length; i++) {
                    this.composer.suggested_partners.push({
                        checked: true,
                        partner_id: self.recipients_for_internal_message[i]['id'],
                        full_name: self.recipients_for_internal_message[i]['name'],
                        name: self.recipients_for_internal_message[i]['name'],
                        email_address: self.recipients_for_internal_message[i]['email'],
                        reason: !_.include(self.recipients_for_internal_message[i]['user_ids'], self.session.uid) ? 'Follower' : 'Partner'
                    });
                }
            }
        },

        get_recipients_for_internal_message: function () {
            var self = this;
            self.result = {};
            return new Model(this.context.default_model).query(
                ['message_follower_ids', 'partner_id']).filter(
                [['id', '=', self.context.default_res_id]])
                .all().then(
                    function (thread) {
                        var follower_ids = thread[0].message_follower_ids;
                        self.result[self.context.default_res_id] = [];
                        self.customer = thread[0].partner_id;
                        // Fetch partner ids
                        return new Model('mail.followers').call(
                            'read', [follower_ids, ['partner_id']]).then(function (res_partners) {
                                console.log(res_partners)
                                var res_partners_filtered = [];
                                // Filter result and push to array
                                _.each(res_partners, function (partner) {
                                    if (partner.partner_id[0] && partner.partner_id[0] !== session.partner_id ) {
                                        res_partners_filtered.push(partner.partner_id[0]);
                                    }
                                });
                                // Add customer
//                                if (self.customer && !res_partners_filtered.includes(self.customer[0])) {
//                                    res_partners_filtered.splice(0, 0, self.customer[0]);
//                                }
                                // Fetch followers data
                                return new Model('res.partner').call(
                                    'read', [res_partners_filtered, ['name', 'email', 'user_ids']]
                                        ).then(function (recipients) {
                                            return recipients;
                                        });
                            });
            });
        }
    });


//    instance.mail.Thread.include({
//        get_recipients_for_internal_message: function(ids, context){
//            var self = this;
//            self.result = {};
//            return new instance.web.Model(context.default_model).call(
//                'read', [ids, ['message_follower_ids', 'partner_id'], context]
//            ).then(function (thread) {
//                for (var i = 0; i < thread.length; i++) {
//                    var res_id = thread[i].id;
//                    var recipient_ids = thread[i].message_follower_ids;
//                    self.result[res_id] = [];
//
//                    // Add customer
//                    self.customer = thread[i].partner_id;
//                    if (self.customer && !recipient_ids.includes(self.customer[0])) {
//                        recipient_ids.splice(0, 0, self.customer[0]);
//                    }
//
//                    return new instance.web.Model('res.partner').call(
//                        'read', [recipient_ids, ['name', 'email', 'user_ids']]
//                    ).then(function (res_partners){
//                        for (var j = 0; j < res_partners.length; j++) {
//                            var partner = res_partners[j];
//                            if (!_.include(partner.user_ids, self.session.uid)){
//                                var reason = 'Follower';
//                                if (self.customer && partner.id == self.customer[0]){
//                                    reason = 'Partner';
//                                }
//                                self.result[res_id].push(
//                                    [partner.id, partner.name + '<' + partner.email + '>', reason]
//                                );
//                            }
//                        }
//                        return self.result;
//                    });
//                }
//                return self.result;
//            });
//        }
//    });



});

odoo.define('mail_private', function (require) {
'use strict';

var base_obj = require('mail_base.base');

var core = require('web.core');
var Chatter = require('mail.Chatter');
var chat_manager = require('mail.chat_manager');
var session = require('web.session');
var Model = require('web.Model');
var utils = require('mail.utils');
var MessageModel = new Model('mail.message', session.user_context);
var ChannelModel = new Model('mail.channel', session.user_context);


    Chatter.include({
        init: function () {
            this._super.apply(this, arguments);
            this.private = false;
            this.events['click .oe_compose_post_private'] = 'on_open_composer_private_message';
        },

        on_post_message: function (message) {
        var self = this;
        if (this.private) {
            message.subtype = false;
            this.private = false;
        }
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

        on_open_composer_private_message: function (event) {
            var self = this;
            this.private = true;
            this.get_recipients_for_internal_message().then(function (data) {
                var private_message = 'private_message';
                self.recipients_for_internal_message = [];
                self.recipients_for_internal_message = data;
                self.open_composer(private_message);
            });
        },

        on_open_composer_new_message: function () {
            this._super.apply(this, arguments);
            this.private = false;
        },

        open_composer: function (options) {
            var self = this;
            this._super.apply(this, arguments);
            if (options === 'private_message') {
                //Clear existing suggested partners
                for (var i=0; i<self.recipients_for_internal_message.length; i++) {
                    this.composer.suggested_partners.push({
                        checked: true,
                        partner_id: self.recipients_for_internal_message[i].id,
                        full_name: self.recipients_for_internal_message[i].name,
                        name: self.recipients_for_internal_message[i].name,
                        email_address: self.recipients_for_internal_message[i].email,
                        reason: !_.include(self.recipients_for_internal_message[i].user_ids, self.session.uid) ? 'Follower' : 'Partner'
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

});

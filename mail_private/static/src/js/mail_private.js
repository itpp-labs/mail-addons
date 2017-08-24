odoo.define('mail_private', function (require) {
'use strict';

var core = require('web.core');
var Chatter = require('mail.Chatter');
var MailComposer = require('mail_base.base').MailComposer;
var chat_manager = require('mail.chat_manager');
var session = require('web.session');
var Model = require('web.Model');
var config = require('web.config');
var utils = require('mail.utils');


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
    }
    var options = {model: this.model, res_id: this.res_id};
    chat_manager.post_message(message, options).then(
        function () {
            self.close_composer();
            if (message.partner_ids.length) {
                self.refresh_followers();
            }
        }).fail(function () {
            // todo: display notification
        });
    },

    on_open_composer_private_message: function (event) {
        var self = this;
        this.private = true;
        this.get_recipients_for_internal_message().then(function (data) {
            self.recipients_for_internal_message = data;
            self.open_composer({is_private: true});
        });
    },

    on_open_composer_new_message: function () {
        this._super.apply(this, arguments);
        this.private = false;
    },

    open_composer: function (options) {

        var self = this;
        var old_composer = this.composer;
        // create the new composer
        this.composer = new MailComposer(this, this.thread_dataset, {
            commands_enabled: false,
            context: this.context,
            input_min_height: 50,
            input_max_height: Number.MAX_VALUE, // no max_height limit for the chatter
            input_baseline: 14,
            is_log: options && options.is_log,
            record_name: this.record_name,
            default_body: old_composer && old_composer.$input && old_composer.$input.val(),
            default_mention_selections: old_composer && old_composer.mention_get_listener_selections(),
            is_private: options && options.is_private,
        });
        this.composer.on('input_focused', this, function () {
            this.composer.mention_set_prefetched_partners(this.mention_suggestions || []);
        });
        this.composer.insertBefore(this.$('.o_mail_thread')).then(function () {
            // destroy existing composer
            if (old_composer) {
                old_composer.destroy();
            }
            if (!config.device.touch) {
                self.composer.focus();
            }
            self.composer.on('post_message', self, self.on_post_message);
            self.composer.on('need_refresh', self, self.refresh_followers);
            self.composer.on('close_composer', null, self.close_composer.bind(self, true));
        });
        this.mute_new_message_button(true);

        if (options && options.is_private) {
            //Clear existing suggested partners
            for (var i=0; i<self.recipients_for_internal_message.length; i++) {
                this.composer.suggested_partners.push({
                    checked: true,
                    partner_id: self.recipients_for_internal_message[i].id,
                    full_name: self.recipients_for_internal_message[i].name,
                    name: self.recipients_for_internal_message[i].name,
                    email_address: self.recipients_for_internal_message[i].email,
                    reason: _.include(self.recipients_for_internal_message[i].user_ids, self.session.uid)
                    ?'Partner'
                    :'Follower'
                });
            }
        }
    },

    get_recipients_for_internal_message: function () {
        var self = this;
        self.result = {};
        return new Model(this.context.default_model).query(
            ['message_follower_ids', 'partner_id']).filter(
            [['id', '=', self.context.default_res_id]]).all().
            then(function (thread) {
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
                            return new Model('res.partner').call(
                                'read', [res_partners_filtered, ['name', 'email', 'user_ids']]
                                    ).then(function (recipients) {
                                        return recipients;
                                    });
                        });
        });
    }
});

MailComposer.include({
    init: function (parent, dataset, options) {
        this._super(parent, dataset, options);
        this.events['click .oe_compose_uncheck'] = 'on_uncheck_recipients';

    },

    on_uncheck_recipients: function () {
        this.$('.o_composer_suggested_partners input:checked').each(function() {
            $(this).prop('checked', false);
        });
    },

    on_open_full_composer: function() {
        if (!this.do_check_attachment_upload()){
            return false;
        }

        var self = this;
        var recipient_done = $.Deferred();
        if (this.options.is_log) {
            recipient_done.resolve([]);
        } else {
            var checked_suggested_partners = this.get_checked_suggested_partners();
            recipient_done = this.check_suggested_partners(checked_suggested_partners);
        }
        recipient_done.then(function (partner_ids) {
            var context = {
                default_parent_id: self.id,
                default_body: utils.get_text2html(self.$input.val()),
                default_attachment_ids: _.pluck(self.get('attachment_ids'), 'id'),
                default_partner_ids: partner_ids,
                default_is_log: self.options.is_log,
                default_is_private: self.options && self.options.is_private,
                mail_post_autofollow: true,
            };

            if (self.context.default_model && self.context.default_res_id) {
                context.default_model = self.context.default_model;
                context.default_res_id = self.context.default_res_id;
            }

            self.do_action({
                type: 'ir.actions.act_window',
                res_model: 'mail.compose.message',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: context,
            }, {
                on_close: function() {
                    self.trigger('need_refresh');
                    var parent = self.getParent();
                    chat_manager.get_messages({model: parent.model, res_id: parent.res_id});
                },
            }).then(self.trigger.bind(self, 'close_composer'));
        });
    }
});

});

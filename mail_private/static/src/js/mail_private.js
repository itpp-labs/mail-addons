/*  Copyright 2016-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
    Copyright 2016 manavi <https://github.com/manawi>
    Copyright 2017-2018 Artyom Losev <https://github.com/ArtyomLosev>
    Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */

odoo.define('mail_private', function (require) {
'use strict';

var core = require('web.core');
var Chatter = require('mail.Chatter');
var ChatterComposer = require('mail.ChatterComposer');
var chat_manager = require('mail_base.base').chat_manager;
var session = require('web.session');

var rpc = require('web.rpc');
var config = require('web.config');
var utils = require('mail.utils');


Chatter.include({
    init: function () {
        this._super.apply(this, arguments);
        this.private = false;
        this.events['click .oe_compose_post_private'] = 'on_open_composer_private_message';
    },

    on_open_composer_private_message: function (event) {
        var self = this;
        this.fetch_recipients_for_internal_message().then(function (data) {
            self._openComposer({
                    is_private: true,
                    suggested_partners: data
                });
        });
    },

    _openComposer: function (options) {
        var self = this;
        var old_composer = this.composer;
        // create the new composer
        this.composer = new ChatterComposer(this, this.record.model, options.suggested_partners || [], {
            commands_enabled: false,
            context: this.context,
            input_min_height: 50,
            input_max_height: Number.MAX_VALUE,
            input_baseline: 14,
            is_log: options && options.is_log,
            record_name: this.record_name,
            default_body: old_composer && old_composer.$input && old_composer.$input.val(),
            default_mention_selections: old_composer && old_composer.mention_get_listener_selections(),
            is_private: options.is_private
        });
        this.composer.on('input_focused', this, function () {
            this.composer.mention_set_prefetched_partners(this.mentionSuggestions || []);
        });
        this.composer.insertAfter(this.$('.o_chatter_topbar')).then(function () {
            // destroy existing composer
            if (old_composer) {
                old_composer.destroy();
            }
            if (!config.device.touch) {
                self.composer.focus();
            }
            self.composer.on('post_message', self, function (message) {
                if (options.is_private) {
                    self.composer.options.is_log = true;
                }
                self.fields.thread.postMessage(message).then(function () {

                    self._closeComposer(true);
                    if (self.postRefresh === 'always' || (self.postRefresh === 'recipients' && message.partner_ids.length)) {
                        self.trigger_up('reload');
                    }
                });
            });
            var toggle_post_private = self.composer.options.is_private || false;
            self.composer.on('need_refresh', self, self.trigger_up.bind(self, 'reload'));
            self.composer.on('close_composer', null, self._closeComposer.bind(self, true));

            self.$el.addClass('o_chatter_composer_active');
            self.$('.o_chatter_button_new_message, .o_chatter_button_log_note, .oe_compose_post_private').removeClass('o_active');
            self.$('.o_chatter_button_new_message').toggleClass('o_active', !self.composer.options.is_log && !self.composer.options.is_private);
            self.$('.o_chatter_button_log_note').toggleClass('o_active', (self.composer.options.is_log && !options.is_private));
            self.$('.oe_compose_post_private').toggleClass('o_active', toggle_post_private);
        });
    },

    fetch_recipients_for_internal_message: function () {
        var self = this;
        self.result = {};
        var follower_ids_domain = [['id', '=', self.context.default_res_id]];
        return rpc.query({
            model: 'mail.message',
            method: 'send_recepients_for_internal_message',
            args: [[], self.context.default_model, follower_ids_domain]
        }).then(function (res) {
            return _.filter(res, function (obj) {
                return obj.partner_id !== session.partner_id;
            });
        });
    },

    get_channels_for_internal_message: function () {
        var self = this;
        self.result = {};
        return new Model(this.context.default_model).query(
            ['message_follower_ids', 'partner_id']).filter(
            [['id', '=', self.context.default_res_id]]).all()
            .then(function (thread) {
                var follower_ids = thread[0].message_follower_ids;
                self.result[self.context.default_res_id] = [];
                self.customer = thread[0].partner_id;

                // Fetch channels ids
                return new Model('mail.followers').call(
                    'read', [follower_ids, ['channel_id']]).then(function (res_channels) {
                        // Filter result and push to array
                        var res_channels_filtered = _.map(res_channels, function (channel) {
                            if (channel.channel_id[0]) {
                                return channel.channel_id[0];
                            }
                        }).filter(function (channel) {
                            return typeof channel !== 'undefined';
                        });

                        return new Model('mail.channel').call(
                            'read', [res_channels_filtered, ['name', 'id']]
                                ).then(function (recipients) {
                                    return recipients;
                                });
                    });
        });
    },

    get_internal_users_ids: function () {
            var ResUser = new Model('mail.compose.message');
            this.users_ids = ResUser.call('get_internal_users_ids', [[]]).then( function (users_ids) {
                return users_ids;
            });
            return this.users_ids;
    },

    get_checked_channels_ids: function () {
        var self = this;
        var checked_channels = [];
        this.$('.o_composer_suggested_channels input:checked').each(function() {
            var full_name = $(this).data('fullname').toString();
            _.each(self.channels_for_internal_message, function(item) {
                if (full_name === item.name) {
                    checked_channels.push(item.id);
                }
            });
        });
        return checked_channels;
    },
});

ChatterComposer.include({
    init: function (parent, model, suggested_partners, options) {
        this._super(parent, model, suggested_partners, options);
        this.events['click .oe_composer_uncheck'] = 'on_uncheck_recipients';
        if (typeof options.is_private === 'undefined') {
            // otherwise it causes an error in context creating function
            options.is_private = false;
        }
    },

    preprocess_message: function () {
        var self = this;
        var def = $.Deferred();
        this._super().then(function (message) {
            message = _.extend(message, {
                subtype: 'mail.mt_comment',
                message_type: 'comment',
                content_subtype: 'html',
                context: self.context,
            });

            // Subtype
            if (self.options.is_log) {
                message.subtype = 'mail.mt_note';
            }

            if (self.options.is_private) {
                message.is_private = true;
                message.channel_ids = self.get_checked_channel_ids();
            }

            // Partner_ids
            if (!self.options.is_log) {
                var checked_suggested_partners = self.get_checked_suggested_partners();
                self.check_suggested_partners(checked_suggested_partners).done(function (partner_ids) {
                    message.partner_ids = (message.partner_ids || []).concat(partner_ids);
                    // update context
                    message.context = _.defaults({}, message.context, {
                        mail_post_autofollow: true,
                    });
                    def.resolve(message);
                });
            } else {
                def.resolve(message);
            }
        });
        return def;
    },

    on_uncheck_recipients: function () {
        this.$('.o_composer_suggested_partners input:checked').each(function() {
            $(this).prop('checked', false);
        });
        this.$('.o_composer_suggested_channels input:checked').each(function() {
            $(this).prop('checked', false);
        });
    },

    preprocess_message: function () {
        var self = this;
        if (self.options.is_private) {
            self.context.is_private = true;
        }
        return this._super();
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
                mail_post_autofollow: true,
                is_private: self.options.is_private,
            };

            if (self.options && self.options.is_private) {
                context.default_is_private = self.options.is_private;
            }

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
    },

    get_checked_suggested_partners: function () {
        var checked_partners = this._super(this, arguments);
        // workaround: odoo code works only when all partners are checked intially,
        // while may select only some of them (internal recepients)
        _.each(checked_partners, function (partner) {
            partner.checked = true;
        });
        checked_partners = _.uniq(_.filter(checked_partners, function (obj) {
            return obj.reason !== 'Channel';
        }));
        this.get_checked_channel_ids();
        return checked_partners;
    },

    get_checked_channel_ids: function () {
        var self = this;
        var checked_channels = [];
        this.$('.o_composer_suggested_partners input:checked').each(function() {
            var full_name = $(this).data('fullname');
            checked_channels = checked_channels.concat(_.filter(self.suggested_partners, function(item) {
                return full_name === item.full_name;
            }));
        });
        checked_channels = _.uniq(_.filter(checked_channels, function (obj) {
            return obj.reason === 'Channel';
        }));
        return _.pluck(checked_channels, 'channel_id');
    }
});

});

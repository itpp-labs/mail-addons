/*  Copyright 2017 Artyom Losev <https://github.com/ArtyomLosev>
    Copyright 2019 Artem Rafailov <https://github.com/Ommo73>
    License LGPL-3.0 (https://www.gnu.org/licenses/lgpl.html). */
odoo.define('mail_base.base', function (require) {
"use strict";

var bus = require('bus.bus').bus;
var utils = require('mail.utils');
var config = require('web.config');
var core = require('web.core');
var data = require('web.data');
var Model = require('web.Model');
var session = require('web.session');
var time = require('web.time');
var web_client = require('web.web_client');

var composer = require('mail.composer');
var config = require('web.config');
var Chatter = require('mail.Chatter');
var form_common = require('web.form_common');

var _t = core._t;
var _lt = core._lt;
var LIMIT = 100;
var preview_msg_max_size = 350;  // optimal for native english speakers
var ODOOBOT_ID = "ODOOBOT";

var MessageModel = new Model('mail.message', session.context);
var ChannelModel = new Model('mail.channel', session.context);
var UserModel = new Model('res.users', session.context);
var PartnerModel = new Model('res.partner', session.context);
var chat_manager = require('mail.chat_manager');

// Private model
//----------------------------------------------------------------------------------
var messages = [];
var channels = [];
var channels_preview_def;
var channel_defs = {};
var chat_unread_counter = 0;
var unread_conversation_counter = 0;
var emojis = [];
var emoji_substitutions = {};
var needaction_counter = 0;
var starred_counter = 0;
var mention_partner_suggestions = [];
var canned_responses = [];
var commands = [];
var discuss_menu_id;
var global_unread_counter = 0;
var pinned_dm_partners = [];  // partner_ids we have a pinned DM with
var client_action_open = false;

bus.on("window_focus", null, function() {
    global_unread_counter = 0;
    web_client.set_title_part("_chat");
});

var channel_seen = _.throttle(function (channel) {
    return ChannelModel.call('channel_seen', [[channel.id]], {}, {shadow: true});
}, 3000);

var ChatAction = core.action_registry.get('mail.chat.instant_messaging');
ChatAction.include({
    init: function(parent, action, options) {
        this._super.apply(this, arguments);
        this.channels_show_send_button = ['channel_inbox'];
        this.channels_display_subject = [];
    },
    start: function() {
        var result = this._super.apply(this, arguments);

        var search_defaults = {};
        var context = this.action ? this.action.context : [];
        _.each(context, function (value, key) {
            var match = /^search_default_(.*)$/.exec(key);
            if (match) {
                search_defaults[match[1]] = value;
            }
        });
        this.searchview.defaults = search_defaults;

        var self = this;
        return $.when(result).done(function() {
            $('.oe_leftbar').toggle(false);
            self.searchview.do_search();
        });
    },
    destroy: function() {
        var result = this._super.apply(this, arguments);
        $('.oe_leftbar .oe_secondary_menu').each(function(){
            if ($(this).css('display') == 'block'){
                if ($(this).children().length > 0) {
                    $('.oe_leftbar').toggle(true);
                }
                return false;
            }
        });
        return result;
    },
    set_channel: function(channel){
        var result = this._super.apply(this, arguments);
        var self = this;
        return $.when(result).done(function() {
            self.$buttons
                .find('.o_mail_chat_button_new_message')
                .toggle(self.channels_show_send_button.indexOf(channel.id) != -1);
        });
    },
    get_thread_rendering_options: function (messages) {
        var options = this._super.apply(this, arguments);
        options.display_subject = options.display_subject || this.channels_display_subject.indexOf(this.channel.id) != -1;
        return options;
    },
    update_message_on_current_channel: function(current_channel_id, message){
        var starred = current_channel_id === "channel_starred" && !message.is_starred;
        var inbox = current_channel_id === "channel_inbox" && !message.is_needaction;
        return starred || inbox;
    },
    on_update_message: function (message) {
        var self = this;
        var current_channel_id = this.channel.id;
        if (this.update_message_on_current_channel(current_channel_id, message)) {
            chat_manager.get_messages({channel_id: this.channel.id, domain: this.domain}).then(function (messages) {
                var options = self.get_thread_rendering_options(messages);
                self.thread.remove_message_and_render(message.id, messages, options).then(function () {
                    self.update_button_status(messages.length === 0);
                });
            });
        } else if (_.contains(message.channel_ids, current_channel_id)) {
            this.fetch_and_render_thread();
        }
    }
});

var MailComposer = composer.BasicComposer.extend({
    template: 'mail.chatter.ChatComposer',

    init: function (parent, dataset, options) {
        this._super(parent, options);
        this.thread_dataset = dataset;
        this.suggested_partners = [];
        this.options = _.defaults(this.options, {
            display_mode: 'textarea',
            record_name: false,
            is_log: false,
        });
        if (this.options.is_log) {
            this.options.send_text = _t('Log');
        }
        this.events = _.extend(this.events, {
            'click .o_composer_button_full_composer': 'on_open_full_composer',
        });
    },

    willStart: function () {
        if (this.options.is_log) {
            return this._super.apply(this, arguments);
        }
        return $.when(this._super.apply(this, arguments), this.message_get_suggested_recipients());
    },

    should_send: function () {
        return false;
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

    /**
    * Send the message on SHIFT+ENTER, but go to new line on ENTER
    */
    prevent_send: function (event) {
        return !event.shiftKey;
    },

    message_get_suggested_recipients: function () {
        var self = this;
        var email_addresses = _.pluck(this.suggested_partners, 'email_address');
        return this.thread_dataset
            .call('message_get_suggested_recipients', [[this.context.default_res_id], this.context])
            .done(function (suggested_recipients) {
                var thread_recipients = suggested_recipients[self.context.default_res_id];
                _.each(thread_recipients, function (recipient) {
                    var parsed_email = utils.parse_email(recipient[1]);
                    if (_.indexOf(email_addresses, parsed_email[1]) === -1) {
                        self.suggested_partners.push({
                            checked: false,
                            partner_id: recipient[0],
                            full_name: recipient[1],
                            name: parsed_email[0],
                            email_address: parsed_email[1],
                            reason: recipient[2],
                        });
                    }
                });
            });
    },

    /**
     * Get the list of selected suggested partners
     * @returns Array() : list of 'recipient' selected partners (may not be created in db)
     **/
    get_checked_suggested_partners: function () {
        var self = this;
        var checked_partners = [];
        this.$('.o_composer_suggested_partners input:checked').each(function() {
            var full_name = $(this).data('fullname');
            checked_partners = checked_partners.concat(_.filter(self.suggested_partners, function(item) {
                return full_name === item.full_name;
            }));
        });
        return checked_partners;
    },

    /**
     * Check the additional partners (not necessary registered partners), and open a popup form view
     * for the ones who informations is missing.
     * @param Array : list of 'recipient' partners to complete informations or validate
     * @returns Deferred resolved with the list of checked suggested partners (real partner)
     **/
    check_suggested_partners: function (checked_suggested_partners) {
        var self = this;
        var check_done = $.Deferred();

        var recipients = _.filter(checked_suggested_partners, function (recipient) { return recipient.checked; });
        var recipients_to_find = _.filter(recipients, function (recipient) { return (! recipient.partner_id); });
        var names_to_find = _.pluck(recipients_to_find, 'full_name');
        var recipients_to_check = _.filter(recipients, function (recipient) { return (recipient.partner_id && ! recipient.email_address); });
        var recipient_ids = _.pluck(_.filter(recipients, function (recipient) { return recipient.partner_id && recipient.email_address; }), 'partner_id');

        var names_to_remove = [];
        var recipient_ids_to_remove = [];

        // have unknown names -> call message_get_partner_info_from_emails to try to find partner_id
        var find_done = $.Deferred();
        if (names_to_find.length > 0) {
            find_done = self.thread_dataset.call('message_partner_info_from_emails', [[this.context.default_res_id], names_to_find]);
        } else {
            find_done.resolve([]);
        }

        // for unknown names + incomplete partners -> open popup - cancel = remove from recipients
        $.when(find_done).pipe(function (result) {
            var emails_deferred = [];
            var recipient_popups = result.concat(recipients_to_check);

            _.each(recipient_popups, function (partner_info) {
                var deferred = $.Deferred();
                emails_deferred.push(deferred);

                var partner_name = partner_info.full_name;
                var partner_id = partner_info.partner_id;
                var parsed_email = utils.parse_email(partner_name);

                var dialog = new form_common.FormViewDialog(self, {
                    res_model: 'res.partner',
                    res_id: partner_id,
                    context: {
                        force_email: true,
                        ref: "compound_context",
                        default_name: parsed_email[0],
                        default_email: parsed_email[1],
                    },
                    title: _t("Please complete partner's informations"),
                    disable_multiple_selection: true,
                }).open();
                dialog.on('closed', self, function () {
                    deferred.resolve();
                });
                dialog.opened().then(function () {
                    dialog.view_form.on('on_button_cancel', self, function () {
                        names_to_remove.push(partner_name);
                        if (partner_id) {
                            recipient_ids_to_remove.push(partner_id);
                        }
                    });
                });
            });
            $.when.apply($, emails_deferred).then(function () {
                var new_names_to_find = _.difference(names_to_find, names_to_remove);
                find_done = $.Deferred();
                if (new_names_to_find.length > 0) {
                    find_done = self.thread_dataset.call('message_partner_info_from_emails', [[self.context.default_res_id], new_names_to_find, true]);
                } else {
                    find_done.resolve([]);
                }
                $.when(find_done).pipe(function (result) {
                    var recipient_popups = result.concat(recipients_to_check);
                    _.each(recipient_popups, function (partner_info) {
                        if (partner_info.partner_id && _.indexOf(partner_info.partner_id, recipient_ids_to_remove) === -1) {
                            recipient_ids.push(partner_info.partner_id);
                        }
                    });
                }).pipe(function () {
                    check_done.resolve(recipient_ids);
                });
            });
        });
        return check_done;
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

Chatter.include({
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
    },
});

var MailTools = core.Class.extend({

    notify_incoming_message: function (msg, options) {
        if (bus.is_odoo_focused() && options.is_displayed) {
            // no need to notify
            return;
        }
        var title = _t('New message');
        if (msg.author_id[1]) {
            title = _.escape(msg.author_id[1]);
        }
        var content = utils.parse_and_transform(msg.body, utils.strip_html).substr(0, preview_msg_max_size);

        if (!bus.is_odoo_focused()) {
            global_unread_counter++;
            var tab_title = _.str.sprintf(_t("%d Messages"), global_unread_counter);
            web_client.set_title_part("_chat", tab_title);
        }

        utils.send_notification(title, content);
    },
    // Message and channel manipulation helpers
    //----------------------------------------------------------------------------------

    // options: channel_id, silent
    add_message: function (data, options) {
        options = options || {};
        var msg = _.findWhere(messages, { id: data.id });

        if (!msg) {
            msg = chat_manager.mail_tools.make_message(data);
            // Keep the array ordered by id when inserting the new message
            messages.splice(_.sortedIndex(messages, msg, 'id'), 0, msg);
            _.each(msg.channel_ids, function (channel_id) {
                var channel = chat_manager.get_channel(channel_id);
                if (channel) {
                    chat_manager.mail_tools.add_to_cache(msg, []);
                    if (options.domain && options.domain !== []) {
                        chat_manager.mail_tools.add_to_cache(msg, options.domain);
                    }
                    if (channel.hidden) {
                        channel.hidden = false;
                        chat_manager.bus.trigger('new_channel', channel);
                    }
                    if (channel.type !== 'static' && !msg.is_author && !msg.is_system_notification) {
                        if (options.increment_unread) {
                            chat_manager.mail_tools.update_channel_unread_counter(channel, channel.unread_counter+1);
                        }
                        if (channel.is_chat && options.show_notification) {
                            if (!client_action_open && config.device.size_class !== config.device.SIZES.XS) {
                                // automatically open chat window
                                chat_manager.bus.trigger('open_chat', channel, { passively: true });
                            }
                            var query = {is_displayed: false};
                            chat_manager.bus.trigger('anyone_listening', channel, query);
                            chat_manager.mail_tools.notify_incoming_message(msg, query);
                        }
                    }
                }
            });
            if (!options.silent) {
                chat_manager.bus.trigger('new_message', msg);
            }
        } else if (options.domain && options.domain !== []) {
            chat_manager.mail_tools.add_to_cache(msg, options.domain);
        }
        return msg;
    },

    property_descr: function (channel, msg, self) {
        return {
            enumerable: true,
            get: function () {
                return _.contains(msg.channel_ids, channel);
            },
            set: function (bool) {
                if (bool) {
                    self.add_channel_to_message(msg, channel);
                } else {
                    msg.channel_ids = _.without(msg.channel_ids, channel);
                }
            }
        };
    },

    get_properties: function(msg){
        return {
            is_starred: chat_manager.mail_tools.property_descr("channel_starred", msg, chat_manager.mail_tools),
            is_needaction: chat_manager.mail_tools.property_descr("channel_inbox", msg, chat_manager.mail_tools)
        };
    },

    set_channel_flags: function(data, msg){
        if (_.contains(data.needaction_partner_ids, session.partner_id)) {
            msg.is_needaction = true;
        }
        if (_.contains(data.starred_partner_ids, session.partner_id)) {
            msg.is_starred = true;
        }
        return msg;
    },

    get_channel_array: function(msg){
        return [ msg.channel_ids, 'channel_inbox', 'channel_starred' ];
    },

    make_message: function (data) {
        var msg = {
            id: data.id,
            author_id: data.author_id,
            body: data.body || "",
            date: moment(time.str_to_datetime(data.date)),
            message_type: data.message_type,
            subtype_description: data.subtype_description,
            is_author: data.author_id && data.author_id[0] === session.partner_id,
            is_note: data.is_note,
            is_system_notification: data.message_type === 'notification' && data.model === 'mail.channel' || data.info === 'transient_message',
            attachment_ids: data.attachment_ids || [],
            subject: data.subject,
            email_from: data.email_from,
            customer_email_status: data.customer_email_status,
            customer_email_data: data.customer_email_data,
            record_name: data.record_name,
            tracking_value_ids: data.tracking_value_ids,
            channel_ids: data.channel_ids,
            model: data.model,
            res_id: data.res_id,
            url: session.url("/mail/view?message_id=" + data.id)
        };

        _.each(_.keys(emoji_substitutions), function (key) {
            var escaped_key = String(key).replace(/([.*+?=^!:${}()|[\]\/\\])/g, '\\$1');
            var regexp = new RegExp("(?:^|\\s|<[a-z]*>)(" + escaped_key + ")(?=\\s|$|</[a-z]*>)", "g");
            msg.body = msg.body.replace(regexp, ' <span class="o_mail_emoji">'+emoji_substitutions[key]+'</span> ');
        });

        Object.defineProperties(msg, chat_manager.mail_tools.get_properties(msg));

        msg = chat_manager.mail_tools.set_channel_flags(data, msg);
        if (msg.model === 'mail.channel') {
            var real_channels = _.without(chat_manager.mail_tools.get_channel_array(msg));
            var origin = real_channels.length === 1 ? real_channels[0] : undefined;
            var channel = origin && chat_manager.get_channel(origin);
            if (channel) {
                msg.origin_id = origin;
                msg.origin_name = channel.name;
            }
        }

        // Compute displayed author name or email
        if ((!msg.author_id || !msg.author_id[0]) && msg.email_from) {
            msg.mailto = msg.email_from;
        } else {
            msg.displayed_author = (msg.author_id === ODOOBOT_ID) && "OdooBot" ||
                                   msg.author_id && msg.author_id[1] ||
                                   msg.email_from || _t('Anonymous');
        }

        // Don't redirect on author clicked of self-posted or OdooBot messages
        msg.author_redirect = !msg.is_author && msg.author_id !== ODOOBOT_ID;

        // Compute the avatar_url
        if (msg.author_id === ODOOBOT_ID) {
            msg.avatar_src = "/mail/static/src/img/odoo_o.png";
        } else if (msg.author_id && msg.author_id[0]) {
            msg.avatar_src = "/web/image/res.partner/" + msg.author_id[0] + "/image_small";
        } else if (msg.message_type === 'email') {
            msg.avatar_src = "/mail/static/src/img/email_icon.png";
        } else {
            msg.avatar_src = "/mail/static/src/img/smiley/avatar.jpg";
        }

        // add anchor tags to urls
        msg.body = utils.parse_and_transform(msg.body, utils.add_link);

        // Compute url of attachments
        _.each(msg.attachment_ids, function(a) {
            a.url = '/web/content/' + a.id + '?download=true';
        });

        return msg;
    },

    add_channel_to_message: function (message, channel_id) {
        message.channel_ids.push(channel_id);
        message.channel_ids = _.uniq(message.channel_ids);
    },

    add_channel: function (data, options) {
        options = typeof options === "object" ? options : {};
        var channel = chat_manager.get_channel(data.id);
        if (channel) {
            if (channel.is_folded !== (data.state === "folded")) {
                channel.is_folded = (data.state === "folded");
                chat_manager.bus.trigger("channel_toggle_fold", channel);
            }
        } else {
            channel = chat_manager.mail_tools.make_channel(data, options);
            channels.push(channel);
            channels = _.sortBy(channels, function (channel) { return _.isString(channel.name) ? channel.name.toLowerCase() : ''; });
            if (!options.silent) {
                chat_manager.bus.trigger("new_channel", channel);
            }
            if (channel.is_detached) {
                chat_manager.bus.trigger("open_chat", channel);
            }
        }
        return channel;
    },

    make_channel: function (data, options) {
        var channel = {
            id: data.id,
            name: data.name,
            server_type: data.channel_type,
            type: data.type || data.channel_type,
            all_history_loaded: false,
            uuid: data.uuid,
            is_detached: data.is_minimized,
            is_folded: data.state === "folded",
            autoswitch: 'autoswitch' in options ? options.autoswitch : true,
            hidden: options.hidden,
            display_needactions: options.display_needactions,
            mass_mailing: data.mass_mailing,
            needaction_counter: data.message_needaction_counter || 0,
            unread_counter: 0,
            last_seen_message_id: data.seen_message_id,
            cache: {'[]': {
                all_history_loaded: false,
                loaded: false,
                messages: []
            }}
        };
        if (channel.type === "channel" && data.public !== "private") {
            channel.type = "public";
        } else if (data.public === "private") {
            channel.type = "private";
        }
        if (_.size(data.direct_partner) > 0) {
            channel.type = "dm";
            channel.name = data.direct_partner[0].name;
            channel.direct_partner_id = data.direct_partner[0].id;
            channel.status = data.direct_partner[0].im_status;
            pinned_dm_partners.push(channel.direct_partner_id);
            bus.update_option('bus_presence_partner_ids', pinned_dm_partners);
        } else if ('anonymous_name' in data) {
            channel.name = data.anonymous_name;
        }
        if (data.last_message_date) {
            channel.last_message_date = moment(time.str_to_datetime(data.last_message_date));
        }
        channel.is_chat = !channel.type.match(/^(public|private|static)$/);
        if (data.message_unread_counter) {
            chat_manager.mail_tools.update_channel_unread_counter(channel, data.message_unread_counter);
        }
        return channel;
    },

    remove_channel: function (channel) {
        if (!channel) { return; }
        if (channel.type === 'dm') {
            var index = pinned_dm_partners.indexOf(channel.direct_partner_id);
            if (index > -1) {
                pinned_dm_partners.splice(index, 1);
                bus.update_option('bus_presence_partner_ids', pinned_dm_partners);
            }
        }
        channels = _.without(channels, channel);
        delete channel_defs[channel.id];
    },

    get_channel_cache: function (channel, domain) {
        var stringified_domain = JSON.stringify(domain || []);
        if (!channel.cache[stringified_domain]) {
            channel.cache[stringified_domain] = {
                all_history_loaded: false,
                loaded: false,
                messages: []
            };
        }
        return channel.cache[stringified_domain];
    },

    invalidate_caches: function (channel_ids) {
        _.each(channel_ids, function (channel_id) {
            var channel = chat_manager.get_channel(channel_id);
            if (channel) {
                channel.cache = { '[]': channel.cache['[]']};
            }
        });
    },

    clear_cache_all_channels: function(){
        _.each(channels, function(channel){
            channel.cache = {
                '[]': {
                all_history_loaded: false,
                loaded: false,
                messages: []
                }
            }
        });
    },

    add_to_cache: function (message, domain) {
        _.each(message.channel_ids, function (channel_id) {
            var channel = chat_manager.get_channel(channel_id);
            if (channel) {
                var channel_cache = chat_manager.mail_tools.get_channel_cache(channel, domain);
                var index = _.sortedIndex(channel_cache.messages, message, 'id');
                if (channel_cache.messages[index] !== message) {
                    channel_cache.messages.splice(index, 0, message);
                }
            }
        });
    },

    remove_from_cache: function(message, domain){
        var self = this;
        _.each(message.channel_ids, function (channel_id) {
            var channel = chat_manager.get_channel(channel_id);
            if (channel) {
                var channel_cache = self.get_channel_cache(channel, domain);
                var index = _.sortedIndex(channel_cache.messages, message, 'id');
                if (channel_cache.messages[index] === message) {
                    channel_cache.messages.splice(index, 1);
                }
            }
        });
    },

    remove_message_from_channel: function (channel_id, message) {
        message.channel_ids = _.without(message.channel_ids, channel_id);
        var channel = _.findWhere(channels, { id: channel_id });
        _.each(channel.cache, function (cache) {
            cache.messages = _.without(cache.messages, message);
        });
    },

    get_domain: function(channel){
        return (channel.id === "channel_inbox") ? [['needaction', '=', true]] :
            (channel.id === "channel_starred") ? [['starred', '=', true]] : false;
    },

    // options: domain, load_more
    fetch_from_channel: function (channel, options) {
        options = options || {};
        var domain = chat_manager.mail_tools.get_domain(channel) || [['channel_ids', 'in', channel.id]];
        var cache = chat_manager.mail_tools.get_channel_cache(channel, options.domain);

        if (options.domain) {
            domain = new data.CompoundDomain(domain, options.domain || []);
        }
        if (options.load_more) {
            var min_message_id = cache.messages[0].id;
            domain = new data.CompoundDomain([['id', '<', min_message_id]], domain);
        }
        return MessageModel.call('message_fetch', [domain], {limit: LIMIT}).then(function (msgs) {
            if (!cache.all_history_loaded) {
                cache.all_history_loaded =  msgs.length < LIMIT;
            }
            cache.loaded = true;

            _.each(msgs, function (msg) {
                chat_manager.mail_tools.add_message(msg, {channel_id: channel.id, silent: true, domain: options.domain});
            });
            var channel_cache = chat_manager.mail_tools.get_channel_cache(channel, options.domain || []);
            return channel_cache.messages;
        });
    },

    // options: force_fetch
    fetch_document_messages: function (ids, options) {
        var loaded_msgs = _.filter(messages, function (message) {
            return _.contains(ids, message.id);
        });
        var loaded_msg_ids = _.pluck(loaded_msgs, 'id');

        options = options || {};
        if (options.force_fetch || _.difference(ids.slice(0, LIMIT), loaded_msg_ids).length) {
            var ids_to_load = _.difference(ids, loaded_msg_ids).slice(0, LIMIT);

            return MessageModel.call('message_format', [ids_to_load]).then(function (msgs) {
                var processed_msgs = [];
                _.each(msgs, function (msg) {
                    processed_msgs.push(chat_manager.mail_tools.add_message(msg, {silent: true}));
                });
                return _.sortBy(loaded_msgs.concat(processed_msgs), function (msg) {
                    return msg.date;
                });
            });
        } else {
            return $.when(loaded_msgs);
        }
    },

    update_channel_unread_counter: function (channel, counter) {
        if (channel.unread_counter > 0 && counter === 0) {
            unread_conversation_counter = Math.max(0, unread_conversation_counter-1);
        } else if (channel.unread_counter === 0 && counter > 0) {
            unread_conversation_counter++;
        }
        if (channel.is_chat) {
            chat_unread_counter = Math.max(0, chat_unread_counter - channel.unread_counter + counter);
        }
        channel.unread_counter = counter;
        chat_manager.bus.trigger("update_channel_unread_counter", channel);
    },

    // Notification handlers
    // ---------------------------------------------------------------------------------
    on_notification: function (notifications) {
        // sometimes, the web client receives unsubscribe notification and an extra
        // notification on that channel.  This is then followed by an attempt to
        // rejoin the channel that we just left.  The next few lines remove the
        // extra notification to prevent that situation to occur.
        var unsubscribed_notif = _.find(notifications, function (notif) {
            return notif[1].info === "unsubscribe";
        });
        if (unsubscribed_notif) {
            notifications = _.reject(notifications, function (notif) {
                return notif[0][1] === "mail.channel" && notif[0][2] === unsubscribed_notif[1].id;
            });
        }
        _.each(notifications, function (notification) {
            var model = notification[0][1];
            if (model === 'ir.needaction') {
                // new message in the inbox
                chat_manager.mail_tools.on_needaction_notification(notification[1]);
            } else if (model === 'mail.channel') {
                // new message in a channel
                chat_manager.mail_tools.on_channel_notification(notification[1]);
            } else if (model === 'res.partner') {
                // channel joined/left, message marked as read/(un)starred, chat open/closed
                chat_manager.mail_tools.on_partner_notification(notification[1]);
            } else if (model === 'bus.presence') {
                // update presence of users
                chat_manager.mail_tools.on_presence_notification(notification[1]);
            } else if (model === 'mail_base.mail_sent') {
                // Delete cache in order to fetch new message

                // TODO find a solution without deleting cache. Currently
                // problem is that on inheriting send_mail in
                // mail.compose.message it's not possible to get id of new
                // message
                chat_manager.mail_tools.clear_cache_all_channels();
            }
        });
    },

    on_needaction_notification: function (message) {
        message = chat_manager.mail_tools.add_message(message, {
            channel_id: 'channel_inbox',
            show_notification: true,
            increment_unread: true
        });
        chat_manager.mail_tools.invalidate_caches(message.channel_ids);
        needaction_counter++;
        _.each(message.channel_ids, function (channel_id) {
            var channel = chat_manager.get_channel(channel_id);
            if (channel) {
                channel.needaction_counter++;
            }
        });
        chat_manager.bus.trigger('update_needaction', needaction_counter);
    },

    on_channel_notification: function (message) {
        var def;
        var channel_already_in_cache = true;
        if (message.channel_ids.length === 1) {
            channel_already_in_cache = !!chat_manager.get_channel(message.channel_ids[0]);
            def = chat_manager.join_channel(message.channel_ids[0], {autoswitch: false});
        } else {
            def = $.when();
        }
        def.then(function () {
            // don't increment unread if channel wasn't in cache yet as its unread counter has just been fetched
            chat_manager.mail_tools.add_message(message, { show_notification: true, increment_unread: channel_already_in_cache });
            chat_manager.mail_tools.invalidate_caches(message.channel_ids);
        });
    },

    on_partner_notification: function (data) {
        if (data.info === "unsubscribe") {
            var channel = chat_manager.get_channel(data.id);
            if (channel) {
                var msg;
                if (_.contains(['public', 'private'], channel.type)) {
                    msg = _.str.sprintf(_t('You unsubscribed from <b>%s</b>.'), channel.name);
                } else {
                    msg = _.str.sprintf(_t('You unpinned your conversation with <b>%s</b>.'), channel.name);
                }
                this.remove_channel(channel);
                chat_manager.bus.trigger("unsubscribe_from_channel", data.id);
                web_client.do_notify(_("Unsubscribed"), msg);
            }
        } else if (data.type === 'toggle_star') {
            chat_manager.mail_tools.on_toggle_star_notification(data);
        } else if (data.type === 'mark_as_read') {
            chat_manager.mail_tools.on_mark_as_read_notification(data);
        } else if (data.type === 'mark_as_unread') {
            chat_manager.mail_tools.on_mark_as_unread_notification(data);
        } else if (data.info === 'channel_seen') {
            chat_manager.mail_tools.on_channel_seen_notification(data);
        } else if (data.info === 'transient_message') {
            chat_manager.mail_tools.on_transient_message_notification(data);
        } else {
            chat_manager.mail_tools.on_chat_session_notification(data);
        }
    },

    on_toggle_star_notification: function (data) {
        _.each(data.message_ids, function (msg_id) {
            var message = _.findWhere(messages, { id: msg_id });
            if (message) {
                chat_manager.mail_tools.invalidate_caches(message.channel_ids);
                message.is_starred = data.starred;
                if (!message.is_starred) {
                    chat_manager.mail_tools.remove_message_from_channel("channel_starred", message);
                    starred_counter--;
                } else {
                    chat_manager.mail_tools.add_to_cache(message, []);
                    var channel_starred = chat_manager.get_channel('channel_starred');
                    channel_starred.cache = _.pick(channel_starred.cache, "[]");
                    starred_counter++;
                }
                chat_manager.bus.trigger('update_message', message);
            }
        });
        chat_manager.bus.trigger('update_starred', starred_counter);
    },

    on_mark_as_read_notification: function (data) {
        _.each(data.message_ids, function (msg_id) {
            var message = _.findWhere(messages, { id: msg_id });
            if (message) {
                chat_manager.mail_tools.invalidate_caches(message.channel_ids);
                chat_manager.mail_tools.remove_message_from_channel("channel_inbox", message);
                chat_manager.bus.trigger('update_message', message);
            }
        });
        if (data.channel_ids) {
            _.each(data.channel_ids, function (channel_id) {
                var channel = chat_manager.get_channel(channel_id);
                if (channel) {
                    channel.needaction_counter = Math.max(channel.needaction_counter - data.message_ids.length, 0);
                }
            });
        } else { // if no channel_ids specified, this is a 'mark all read' in the inbox
            _.each(channels, function (channel) {
                channel.needaction_counter = 0;
            });
        }
        needaction_counter = Math.max(needaction_counter - data.message_ids.length, 0);
        chat_manager.bus.trigger('update_needaction', needaction_counter);
    },

    on_mark_as_unread_notification: function (data) {
        _.each(data.message_ids, function (message_id) {
            var message = _.findWhere(messages, { id: message_id });
            if (message) {
                chat_manager.mail_tools.invalidate_caches(message.channel_ids);
                chat_manager.mail_tools.add_channel_to_message(message, 'channel_inbox');
                chat_manager.mail_tools.add_to_cache(message, []);
            }
        });
        var channel_inbox = chat_manager.get_channel('channel_inbox');
        channel_inbox.cache = _.pick(channel_inbox.cache, "[]");

        _.each(data.channel_ids, function (channel_id) {
            var channel = chat_manager.get_channel(channel_id);
            if (channel) {
                channel.needaction_counter += data.message_ids.length;
            }
        });
        needaction_counter += data.message_ids.length;
        chat_manager.bus.trigger('update_needaction', needaction_counter);
    },

    on_channel_seen_notification: function (data) {
        var channel = chat_manager.get_channel(data.id);
        if (channel) {
            channel.last_seen_message_id = data.last_message_id;
            if (channel.unread_counter) {
                chat_manager.mail_tools.update_channel_unread_counter(channel, 0);
            }
        }
    },

    on_chat_session_notification: function (chat_session) {
        var channel;
        if ((chat_session.channel_type === "channel") && (chat_session.state === "open")) {
            chat_manager.mail_tools.add_channel(chat_session, {autoswitch: false});
            if (!chat_session.is_minimized && chat_session.info !== 'creation') {
                web_client.do_notify(_t("Invitation"), _t("You have been invited to: ") + chat_session.name);
            }
        }
        // partner specific change (open a detached window for example)
        if ((chat_session.state === "open") || (chat_session.state === "folded")) {
            channel = chat_session.is_minimized && chat_manager.get_channel(chat_session.id);
            if (channel) {
                channel.is_detached = true;
                channel.is_folded = (chat_session.state === "folded");
                chat_manager.bus.trigger("open_chat", channel);
            }
        } else if (chat_session.state === "closed") {
            channel = chat_manager.get_channel(chat_session.id);
            if (channel) {
                channel.is_detached = false;
                chat_manager.bus.trigger("close_chat", channel, {keep_open_if_unread: true});
            }
        }
    },

    on_presence_notification: function (data) {
        var dm = chat_manager.get_dm_from_partner_id(data.id);
        if (dm) {
            dm.status = data.im_status;
            chat_manager.bus.trigger('update_dm_presence', dm);
        }
    },
    on_transient_message_notification: function (data) {
        var last_message = _.last(messages);
        data.id = (last_message ? last_message.id : 0) + 0.01;
        data.author_id = data.author_id || ODOOBOT_ID;
        chat_manager.mail_tools.add_message(data);
    }

});

var cls = new MailTools();

// Public interface
//----------------------------------------------------------------------------------
chat_manager.mail_tools = cls;
// we add this function this way in order to make them extendable via MailTools.include({...})
chat_manager.make_message = function(){
    return chat_manager.mail_tools.make_message.apply(chat_manager.mail_tools, arguments);
};
chat_manager.make_channel = function(){
    return chat_manager.mail_tools.make_channel.apply(chat_manager.mail_tools, arguments);
};
chat_manager.post_message = function (data, options) {
        options = options || {};
        var msg = {
            partner_ids: data.partner_ids,
            channel_ids: data.channel_ids,
            body: _.str.trim(data.content),
            attachment_ids: data.attachment_ids
        };
        if ('subject' in data) {
            msg.subject = data.subject;
        }
        if ('channel_id' in options) {
            // post a message in a channel or execute a command
            return ChannelModel.call(data.command ? 'execute_command' : 'message_post', [options.channel_id], _.extend(msg, {
                message_type: 'comment',
                content_subtype: 'html',
                subtype: 'mail.mt_comment',
                command: data.command,
            }));
        }
        if ('model' in options && 'res_id' in options) {
            // post a message in a chatter
            _.extend(msg, {
                content_subtype: data.content_subtype,
                context: data.context,
                message_type: data.message_type,
                subtype: data.subtype,
                subtype_id: data.subtype_id
            });

            if (options.model && options.res_id){
                var model = new Model(options.model);
                return model.call('message_post', [options.res_id], msg).then(function (msg_id) {
                    return MessageModel.call('message_format', [msg_id]).then(function (msgs) {
                        msgs[0].model = options.model;
                        msgs[0].res_id = options.res_id;
                        chat_manager.mail_tools.add_message(msgs[0]);
                    });
                });
            } else {
                options.model = 'mail.compose.message';
                var compose_model = new Model(options.model);
                return compose_model.call('create', [msg, {default_parent_id: options.parent_id}]).then(function(id){
                    return compose_model.call('send_mail_action', [id, {}]);
                });
            }
        }
    };
chat_manager.get_message = function (id) {
        return _.findWhere(messages, {id: id});
    };
chat_manager.get_messages = function (options) {
    var channel;

    if ('channel_id' in options && options.load_more) {
        // get channel messages, force load_more
        channel = this.get_channel(options.channel_id);
        return chat_manager.mail_tools.fetch_from_channel(channel, {domain: options.domain || {}, load_more: true});
    }
    if ('channel_id' in options) {
        // channel message, check in cache first
        channel = this.get_channel(options.channel_id);
        var channel_cache = chat_manager.mail_tools.get_channel_cache(channel, options.domain);
        if (channel_cache.loaded) {
            return $.when(channel_cache.messages);
        } else {
            return chat_manager.mail_tools.fetch_from_channel(channel, {domain: options.domain});
        }
    }
    if ('ids' in options) {
        // get messages from their ids (chatter is the main use case)
        return chat_manager.mail_tools.fetch_document_messages(options.ids, options).then(function(result) {
            chat_manager.mark_as_read(options.ids);
            return result;
        });
    }
    if ('model' in options && 'res_id' in options) {
        // get messages for a chatter, when it doesn't know the ids (use
        // case is when using the full composer)
        var domain = [['model', '=', options.model], ['res_id', '=', options.res_id]];
        MessageModel.call('message_fetch', [domain], {limit: 30}).then(function (msgs) {
            return _.map(msgs, chat_manager.mail_tools.add_message);
        });
    }
};
chat_manager.toggle_star_status = function (message_id) {
    return MessageModel.call('toggle_message_starred', [[message_id]]);
    };
chat_manager.unstar_all = function () {
        return MessageModel.call('unstar_all', [[]], {});
    };
chat_manager.mark_as_read = function (message_ids) {
        var ids = _.filter(message_ids, function (id) {
            var message = _.findWhere(messages, {id: id});
            // If too many messages, not all are fetched, and some might not be found
            return !message || message.is_needaction;
        });
        if (ids.length) {
            return MessageModel.call('set_message_done', [ids]);
        } else {
            return $.when();
        }
    };
chat_manager.mark_all_as_read = function (channel, domain) {
        if ((channel.id === "channel_inbox" && needaction_counter) || (channel && channel.needaction_counter)) {
            return MessageModel.call('mark_all_as_read', [], {channel_ids: channel.id !== "channel_inbox" ? [channel.id] : [], domain: domain});
        }
        return $.when();
    };
chat_manager.undo_mark_as_read = function (message_ids, channel) {
        return MessageModel.call('mark_as_unread', [message_ids, [channel.id]]);
    };
chat_manager.mark_channel_as_seen = function (channel) {
        if (channel.unread_counter > 0 && channel.type !== 'static') {
            chat_manager.mail_tools.update_channel_unread_counter(channel, 0);
            channel_seen(channel);
        }
    };
chat_manager.get_channels = function () {
        return _.clone(channels);
    };
chat_manager.get_channel = function (id) {
        return _.findWhere(channels, {id: id});
    };
chat_manager.get_dm_from_partner_id = function (partner_id) {
        return _.findWhere(channels, {direct_partner_id: partner_id});
    };
chat_manager.all_history_loaded = function (channel, domain) {
        return chat_manager.mail_tools.get_channel_cache(channel, domain).all_history_loaded;
    };
chat_manager.get_mention_partner_suggestions = function (channel) {
        if (!channel) {
            return mention_partner_suggestions;
        }
        if (!channel.members_deferred) {
            channel.members_deferred = ChannelModel
                .call("channel_fetch_listeners", [channel.uuid], {}, {shadow: true})
                .then(function (members) {
                    var suggestions = [];
                    _.each(mention_partner_suggestions, function (partners) {
                        suggestions.push(_.filter(partners, function (partner) {
                            return !_.findWhere(members, { id: partner.id });
                        }));
                    });

                    return [members];
                });
        }
        return channel.members_deferred;
    };
chat_manager.get_commands = function (channel) {
    return _.filter(commands, function (command) {
        return !command.channel_types || _.contains(command.channel_types, channel.server_type);
    });
};
chat_manager.get_canned_responses = function () {
    return canned_responses;
};


chat_manager.get_needaction_counter = function () {
        return needaction_counter;
    };

chat_manager.get_starred_counter = function () {
        return starred_counter;
};

chat_manager.get_chat_unread_counter = function () {
        return chat_unread_counter;
    };
chat_manager.get_unread_conversation_counter = function () {
        return unread_conversation_counter;
    };
chat_manager.get_last_seen_message = function (channel) {
        if (channel.last_seen_message_id) {
            var messages = channel.cache['[]'].messages;
            var msg = _.findWhere(messages, {id: channel.last_seen_message_id});
            if (msg) {
                var i = _.sortedIndex(messages, msg, 'id') + 1;
                while (i < messages.length && (messages[i].is_author || messages[i].is_system_notification)) {
                    msg = messages[i];
                    i++;
                }
                return msg;
            }
        }
    };
chat_manager.get_discuss_menu_id = function () {
        return discuss_menu_id;
    };
chat_manager.detach_channel = function (channel) {
        return ChannelModel.call("channel_minimize", [channel.uuid, true], {}, {shadow: true});
    };
chat_manager.remove_chatter_messages = function (model) {
        messages = _.reject(messages, function (message) {
            return message.channel_ids.length === 0 && message.model === model;
        });
    };
chat_manager.create_channel = function (name, type) {
        var method = type === "dm" ? "channel_get" : "channel_create";
        var args = type === "dm" ? [[name]] : [name, type];

        return ChannelModel
            .call(method, args)
            .then(chat_manager.mail_tools.add_channel);
    };
chat_manager.join_channel = function (channel_id, options) {
        if (channel_id in channel_defs) {
            // prevents concurrent calls to channel_join_and_get_info
            return channel_defs[channel_id];
        }
        var channel = this.get_channel(channel_id);
        if (channel) {
            // channel already joined
            channel_defs[channel_id] = $.when(channel);
        } else {
            channel_defs[channel_id] = ChannelModel
                .call('channel_join_and_get_info', [[channel_id]])
                .then(function (result) {
                    return chat_manager.mail_tools.add_channel(result, options);
                });
        }
        return channel_defs[channel_id];
    };
chat_manager.open_and_detach_dm = function (partner_id) {
        return ChannelModel.call('channel_get_and_minimize', [[partner_id]]).then(chat_manager.mail_tools.add_channel);
    };
chat_manager.open_channel = function (channel) {
        chat_manager.bus.trigger(client_action_open ? 'open_channel' : 'detach_channel', channel);
    };
chat_manager.unsubscribe = function (channel) {
        var def;
        if (_.contains(['public', 'private'], channel.type)) {
            return ChannelModel.call('action_unfollow', [[channel.id]]);
        } else {
            return ChannelModel.call('channel_pin', [channel.uuid, false]);
        }
    };
chat_manager.close_chat_session = function (channel_id) {
        var channel = this.get_channel(channel_id);
        ChannelModel.call("channel_fold", [], {uuid : channel.uuid, state : "closed"}, {shadow: true});
    };
chat_manager.fold_channel = function (channel_id, folded) {
        var args = {
            uuid: this.get_channel(channel_id).uuid
        };
        if (_.isBoolean(folded)) {
            args.state = folded ? 'folded' : 'open';
        }
        return ChannelModel.call("channel_fold", [], args, {shadow: true});
    };
    /**
     * Special redirection handling for given model and id
     *
     * If the model is res.partner, and there is a user associated with this
     * partner which isn't the current user, open the DM with this user.
     * Otherwhise, open the record's form view, if this is not the current user's.
     */
chat_manager.redirect = function (res_model, res_id, dm_redirection_callback) {
        var self = this;
        var redirect_to_document = function (res_model, res_id, view_id) {
            web_client.do_action({
                type:'ir.actions.act_window',
                view_type: 'form',
                view_mode: 'form',
                res_model: res_model,
                views: [[view_id || false, 'form']],
                res_id: res_id
            });
        };
        if (res_model === "res.partner") {
            var domain = [["partner_id", "=", res_id]];
            UserModel.call("search", [domain]).then(function (user_ids) {
                if (user_ids.length && user_ids[0] !== session.uid && dm_redirection_callback) {
                    self.create_channel(res_id, 'dm').then(dm_redirection_callback);
                } else {
                    redirect_to_document(res_model, res_id);
                }
            });
        } else {
            new Model(res_model).call('get_formview_id', [[res_id], session.context]).then(function (view_id) {
                redirect_to_document(res_model, res_id, view_id);
            });
        }
    };
chat_manager.get_channels_preview = function (channels) {
        var channels_preview = _.map(channels, function (channel) {
            var info = _.pick(channel, 'id', 'is_chat', 'name', 'status', 'unread_counter');
            info.last_message = _.last(channel.cache['[]'].messages);
            if (!info.is_chat) {
                info.image_src = '/web/image/mail.channel/'+channel.id+'/image_small';
            } else if (channel.direct_partner_id) {
                info.image_src = '/web/image/res.partner/'+channel.direct_partner_id+'/image_small';
            } else {
                info.image_src = '/mail/static/src/img/smiley/avatar.jpg';
            }
            return info;
        });
        var missing_channels = _.where(channels_preview, {last_message: undefined});
        if (!channels_preview_def) {
            if (missing_channels.length) {
                var missing_channel_ids = _.pluck(missing_channels, 'id');
                channels_preview_def = ChannelModel.call('channel_fetch_preview', [missing_channel_ids], {}, {shadow: true});
            } else {
                channels_preview_def = $.when();
            }
        }
        return channels_preview_def.then(function (channels) {
            _.each(missing_channels, function (channel_preview) {
                var channel = _.findWhere(channels, {id: channel_preview.id});
                if (channel) {
                    channel_preview.last_message = chat_manager.mail_tools.add_message(channel.last_message);
                }
            });
            return _.filter(channels_preview, function (channel) {
                return channel.last_message;  // remove empty channels
            });
        });
    };
chat_manager.get_message_body_preview = function (message_body) {
        return utils.parse_and_transform(message_body, utils.inline);
    };
chat_manager.search_partner = function (search_val, limit) {
        var def = $.Deferred();
        var values = [];
        // search among prefetched partners
        var search_regexp = new RegExp(_.str.escapeRegExp(utils.unaccent(search_val)), 'i');
        _.each(mention_partner_suggestions, function (partners) {
            if (values.length < limit) {
                values = values.concat(_.filter(partners, function (partner) {
                    return session.partner_id !== partner.id && search_regexp.test(partner.name);
                })).splice(0, limit);
            }
        });
        if (!values.length) {
            // extend the research to all users
            def = PartnerModel.call('im_search', [search_val, limit || 20], {}, {shadow: true});
        } else {
            def = $.when(values);
        }
        return def.then(function (values) {
            var autocomplete_data = _.map(values, function (value) {
                return { id: value.id, value: value.name, label: value.name };
            });
            return _.sortBy(autocomplete_data, 'label');
        });
    };

chat_manager.bus.on('client_action_open', null, function (open) {
    client_action_open = open;
});

// In order to extend init use chat_manager.is_ready Derrered object. See example in mail_arhive module
function init () {
    chat_manager.mail_tools.add_channel({
        id: "channel_inbox",
        name: _lt("Inbox"),
        type: "static",
    }, { display_needactions: true });

    chat_manager.mail_tools.add_channel({
        id: "channel_starred",
        name: _lt("Starred"),
        type: "static"
    });

    // unsubscribe and then subscribe to the event, to avoid duplication of new messages
    bus.off('notification');
    bus.on('notification', null, function(){
        chat_manager.mail_tools.on_notification.apply(chat_manager.mail_tools, arguments);
    });

    return session.rpc('/mail/client_action').then(function (result) {
        _.each(result.channel_slots, function (channels) {
            _.each(channels, chat_manager.mail_tools.add_channel);
        });
        needaction_counter = result.needaction_inbox_counter;
        starred_counter = result.starred_counter;
        commands = _.map(result.commands, function (command) {
            return _.extend({ id: command.name }, command);
        });
        mention_partner_suggestions = result.mention_partner_suggestions;
        discuss_menu_id = result.menu_id;

        // Shortcodes: canned responses and emojis
        _.each(result.shortcodes, function (s) {
            if (s.shortcode_type === 'text') {
                canned_responses.push(_.pick(s, ['id', 'source', 'substitution']));
            } else {
                emojis.push(_.pick(s, ['id', 'source', 'substitution', 'description']));
                emoji_substitutions[_.escape(s.source)] = s.substitution;
            }
        });

        bus.start_polling();
    });
}

chat_manager.is_ready = init();
return {
    ODOOBOT_ID: ODOOBOT_ID,
    chat_manager: chat_manager,
    MailTools: MailTools,
    MailComposer: MailComposer
};

});

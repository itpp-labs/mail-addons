odoo.define('mail_archives.archives', function (require) {
"use strict";

var base_obj = require('mail_base.base');

//-------------------------------------------------------------------------------
var bus = require('bus.bus').bus;
var config = require('web.config');
var core = require('web.core');
var data = require('web.data');
var Model = require('web.Model');
var session = require('web.session');
var time = require('web.time');
var web_client = require('web.web_client');

var _t = core._t;
var LIMIT = 100;

var MessageModel = new Model('mail.message', session.context);
//-------------------------------------------------------------------------------
var emojis = [];
var emoji_substitutions = {};
var needaction_counter = 0;
var mention_partner_suggestions = [];
var discuss_ids = {};
//-------------------------------------------------------------------------------

// Inherit class and override methods
base_obj.MailTools.include({
    make_message: function (data) {
        var msg = {
            id: data.id,
            author_id: data.author_id,
            body_short: data.body_short || "",
            body: data.body || "",
            date: moment(time.str_to_datetime(data.date)),
            message_type: data.message_type,
            subtype_description: data.subtype_description,
            is_author: data.author_id && data.author_id[0] === session.partner_id,
            is_note: data.is_note,
            is_system_notification: data.message_type === 'notification' && data.model === 'mail.channel',
            attachment_ids: data.attachment_ids,
            subject: data.subject,
            email_from: data.email_from,
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

        var properties = this.get_properties(msg);
        // Add property to Object
        properties.is_archive = this.property_descr("channel_archive", msg, this);
        Object.defineProperties(msg, properties);

        msg = this.set_channel_flags(data, msg);
        // Set archive flag
        msg.is_archive = true;
        if (msg.model === 'mail.channel') {
            // Add 'channel_archive' to channel_array
            var channel_array = this.get_channel_array(msg).concat('channel_archive');
            var real_channels = _.without(channel_array);
            var origin = real_channels.length === 1 ? real_channels[0] : undefined;
            var channel = origin && base_obj.chat_manager.get_channel(origin);
            if (channel) {
                msg.origin_id = origin;
                msg.origin_name = channel.name;
            }
        }

        if ((!msg.author_id || !msg.author_id[0]) && msg.email_from) {
            msg.mailto = msg.email_from;
        } else {
            msg.displayed_author = msg.author_id && msg.author_id[1] ||
                                   msg.email_from || _t('Anonymous');
        }

        msg.author_redirect = !msg.is_author;

        if (msg.author_id && msg.author_id[0]) {
            msg.avatar_src = "/web/image/res.partner/" + msg.author_id[0] + "/image_small";
        } else if (msg.message_type === 'email') {
            msg.avatar_src = "/mail/static/src/img/email_icon.png";
        } else {
            msg.avatar_src = "/mail/static/src/img/smiley/avatar.jpg";
        }

        msg.body = this.parse_and_transform(msg.body, this.add_link);

        _.each(msg.attachment_ids, function(a) {
            a.url = '/web/content/' + a.id + '?download=true';
        });

        return msg;
    },

    fetch_from_channel: function (channel, options) {
        options = options || {};
        // Add archive domain
        var domain = (channel.id === "channel_archive") ? [] : this.get_domain(channel);
        var cache = this.get_channel_cache(channel, options.domain);

        if (options.domain) {
            domain = new data.CompoundDomain(domain, options.domain || []);
        }
        if (options.load_more) {
            var min_message_id = cache.messages[0].id;
            domain = new data.CompoundDomain([['id', '<', min_message_id]], domain);
        }
        var self = this;
        return MessageModel.call('message_fetch', [domain], {limit: LIMIT}).then(function (msgs) {
            if (!cache.all_history_loaded) {
                cache.all_history_loaded =  msgs.length < LIMIT;
            }
            cache.loaded = true;

            _.each(msgs, function (msg) {
                self.add_message(msg, {channel_id: channel.id, silent: true, domain: options.domain});
            });
            var channel_cache = self.get_channel_cache(channel, options.domain || []);
            return channel_cache.messages;
        });
    },

    start: function(){
        // Add archive channel
        this.add_channel({
            id: "channel_archive",
            name: _t("Archive"),
            type: "static"
        });

        var load_channels = session.rpc('/mail/client_action').then(function (result) {
            _.each(result.channel_slots, function (channels) {
                _.each(channels, cls.add_channel);
            });
            needaction_counter = result.needaction_inbox_counter;
            mention_partner_suggestions = result.mention_partner_suggestions;
        });

        var load_emojis = session.rpc("/mail/chat_init").then(function (result) {
            emojis = result.emoji;
            _.each(emojis, function(emoji) {
                emoji_substitutions[_.escape(emoji.source)] = emoji.substitution;
            });
        });

        var ir_model = new Model("ir.model.data");
        var load_menu_id = ir_model.call("xmlid_to_res_id", ["mail.mail_channel_menu_root_chat"], {}, {shadow: true});
        var load_action_id = ir_model.call("xmlid_to_res_id", ["mail.mail_channel_action_client_chat"], {}, {shadow: true});

        bus.on('notification', null, cls.on_notification);

        return $.when(load_menu_id, load_action_id, load_channels, load_emojis).then(function (menu_id, action_id) {
            discuss_ids = {
                menu_id: menu_id,
                action_id: action_id
            };
            bus.start_polling();
        });
    }
});

// Change chat_manager with override methods
var cls = new base_obj.MailTools(base_obj.chat_manager);
base_obj.chat_manager.is_ready = cls.start();

return base_obj.chat_manager;

});

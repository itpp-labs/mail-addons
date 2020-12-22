/* Copyright 2020 Denis Mudarisov <https://github.com/trojikman>
   License MIT (https://opensource.org/licenses/MIT). */
odoo.define("mail_sent.sent", function (require) {
    "use strict";

    var core = require("web.core");
    var session = require("web.session");
    var chat_manager = require("mail_base.base").chat_manager;

    var _lt = core._lt;

    var ChatAction = core.action_registry.get("mail.chat.instant_messaging");
    ChatAction.include({
        init: function (parent, action, options) {
            this._super.apply(this, arguments);
            var channel_name = "channel_sent";
            // Add channel Sent for show "Send message" button
            this.channels_show_send_button.push(channel_name);
            // Add channel Sent for enable "display_subject" option
            this.channels_display_subject.push(channel_name);
        },

        update_message_on_current_channel: function (current_channel_id, message) {
            var result = this._super.apply(this, arguments);
            var sent = current_channel_id === "channel_sent" && !message.is_sent;
            return sent || result;
        },
    });

    chat_manager.is_ready.then(function () {
        // Inherit class and override methods
        var chat_manager_super = _.clone(chat_manager);
        chat_manager.get_properties = function (msg) {
            var properties = chat_manager_super.get_properties.apply(this, arguments);
            properties.is_sent = this.property_descr("channel_sent", msg, this);
            return properties;
        };

        chat_manager.set_channel_flags = function (data, msg) {
            chat_manager_super.set_channel_flags.apply(this, arguments);
            if (data.sent && data.author_id[0] === session.partner_id) {
                msg.is_sent = true;
            }
            return msg;
        };

        chat_manager.get_channel_array = function (msg) {
            var arr = chat_manager_super.get_channel_array.apply(this, arguments);
            return arr.concat("channel_sent");
        };

        chat_manager.get_domain = function (channel) {
            return channel.id === "channel_sent"
                ? [
                      ["sent", "=", true],
                      ["author_id.user_ids", "in", [session.uid]],
                  ]
                : chat_manager_super.get_domain.apply(this, arguments);
        };

        // Add sent channel
        chat_manager.add_channel({
            id: "channel_sent",
            name: _lt("Sent"),
            type: "static",
        });
        return $.when();
    });

    return chat_manager;
});

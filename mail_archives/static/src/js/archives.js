/* Copyright 2020 Denis Mudarisov <https://github.com/trojikman>
 * License MIT (https://opensource.org/licenses/MIT). */

odoo.define("mail_archives.archives", function (require) {
    "use strict";

    var core = require("web.core");
    var session = require("web.session");
    var chat_manager = require("mail_base.base").chat_manager;

    var _lt = core._lt;

    var ChatAction = core.action_registry.get("mail.chat.instant_messaging");
    ChatAction.include({
        init: function (parent, action, options) {
            this._super.apply(this, arguments);
            var channel_name = "channel_archive";
            // Add channel Archive for enable "display_subject" option
            this.channels_display_subject.push(channel_name);
        },

        update_message_on_current_channel: function (current_channel_id, message) {
            var result = this._super.apply(this, arguments);
            var archive =
                current_channel_id === "channel_archive" && !message.is_archive;
            return archive || result;
        },
    });

    chat_manager.is_ready.then(function () {
        // Inherit class and override methods

        var chat_manager_super = _.clone(chat_manager);

        chat_manager.get_properties = function (msg) {
            var properties = chat_manager_super.get_properties.apply(this, arguments);
            properties.is_archive = this.property_descr("channel_archive", msg, this);
            return properties;
        };

        chat_manager.set_channel_flags = function (data, msg) {
            chat_manager_super.set_channel_flags.apply(this, arguments);
            // Get recipients ids
            var recipients_ids = [];
            for (var i = 0; i < (data.partner_ids || []).length; i++) {
                recipients_ids.push(data.partner_ids[i][0]);
            }

            // If author or recipient
            if (
                data.author_id[0] === session.partner_id ||
                recipients_ids.indexOf(session.partner_id) !== -1
            ) {
                msg.is_archive = true;
            }

            return msg;
        };

        chat_manager.get_channel_array = function (msg) {
            var arr = chat_manager_super.get_channel_array.apply(this, arguments);
            return arr.concat("channel_archive");
        };

        chat_manager.get_domain = function (channel) {
            return channel.id === "channel_archive"
                ? [
                      "|",
                      ["partner_ids", "in", [session.partner_id]],
                      ["author_id", "in", [session.partner_id]],
                  ]
                : chat_manager_super.get_domain.apply(this, arguments);
        };

        chat_manager.add_channel({
            id: "channel_archive",
            name: _lt("Archive"),
            type: "static",
        });
    });

    return chat_manager;
});

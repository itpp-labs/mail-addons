odoo.define("mail_all.all", function(require) {
    "use strict";

    var chat_manager = require("mail_base.base").chat_manager;
    var core = require("web.core");

    var _lt = core._lt;

    var ChatAction = core.action_registry.get("mail.chat.instant_messaging");
    ChatAction.include({
        get_thread_rendering_options: function(messages) {
            var options = this._super.apply(this, arguments);
            options.display_subject =
                options.display_subject || this.channel.id === "channel_all";
            return options;
        },
    });

    // Override methods
    var chat_manager_super = _.clone(chat_manager);

    chat_manager.get_properties = function(msg) {
        var properties = chat_manager_super.get_properties.apply(this, arguments);
        properties.is_all = this.property_descr("channel_all", msg, this);
        return properties;
    };

    chat_manager.set_channel_flags = function(data, msg) {
        chat_manager_super.set_channel_flags.apply(this, arguments);
        msg.is_all = data.author_id !== "ODOOBOT";
        return msg;
    };

    chat_manager.get_channel_array = function(msg) {
        var arr = chat_manager_super.get_channel_array.apply(this, arguments);
        return arr.concat("channel_all");
    };

    chat_manager.get_domain = function(channel) {
        return channel.id === "channel_all"
            ? []
            : chat_manager_super.get_domain.apply(this, arguments);
    };

    chat_manager.is_ready.then(function() {
        // Add all channel
        chat_manager.add_channel({
            id: "channel_all",
            name: _lt("All messages"),
            type: "static",
        });
        return $.when();
    });

    return chat_manager;
});

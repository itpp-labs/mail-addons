odoo.define('mail_sent.sent', function (require) {
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

var _lt = core._lt;
//-------------------------------------------------------------------------------

var ChatAction = core.action_registry.get('mail.chat.instant_messaging');
ChatAction.include({
    init: function(parent, action, options) {
        this._super.apply(this, arguments);
        var channel_name = 'channel_sent';
        // Add channel Sent for show "Send message" button
        this.channels_show_send_button.push(channel_name);
        // Add channel Sent for enable "display_subject" option
        this.channels_display_subject.push(channel_name);
    },

    update_message_on_current_channel: function(current_channel_id, message){
        var result = this._super.apply(this, arguments);
        var sent = current_channel_id === "channel_sent" && !message.is_sent;
        return sent || result;
    }
});

// Inherit class and override methods
base_obj.MailTools.include({
    get_properties: function(msg){
        var properties = this._super.apply(this, arguments);
        properties.is_sent = this.property_descr("channel_sent", msg, this);
        return properties;
    },

    set_channel_flags: function(data, msg){
        this._super.apply(this, arguments);
        if (data.sent && data.author_id[0] == session.partner_id) {
            msg.is_sent = true;
        }
        return msg;
    },

    get_channel_array: function(msg){
        var arr = this._super.apply(this, arguments);
        return arr.concat('channel_sent');
    },

    get_domain: function(channel){
        return (channel.id === "channel_sent") ? [
            ['sent', '=', true],
            ['author_id.user_ids', 'in', [openerp.session.uid]]
        ] : this._super.apply(this, arguments);
    }
});

base_obj.chat_manager.is_ready.then(function(){
        // Add sent channel
        base_obj.chat_manager.mail_tools.add_channel({
            id: "channel_sent",
            name: _lt("Sent"),
            type: "static"
        });

        return $.when();
    });

return base_obj.chat_manager;

});

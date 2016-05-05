odoo.define('mail_all.all', function (require) {
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
    get_thread_rendering_options: function (messages) {
        var options = this._super.apply(this, arguments);
        options.display_subject = options.display_subject || this.channel.id === "channel_all";
        return options;
    }
});

// Inherit class and override methods
base_obj.MailTools.include({
    get_properties: function(msg){
        var properties = this._super.apply(this, arguments);
        properties.is_all = this.property_descr("channel_all", msg, this);
        return properties;
    },

    set_channel_flags: function(data, msg){
        this._super.apply(this, arguments);
        msg.is_all = true;
        return msg;
    },

    get_channel_array: function(msg){
        var arr = this._super.apply(this, arguments);
        return arr.concat('channel_all');
    },

    get_domain: function(channel){
        return (channel.id === "channel_all") ? [] : this._super.apply(this, arguments);
    }
});

base_obj.chat_manager.is_ready.then(function(){
        // Add all channel
        base_obj.chat_manager.mail_tools.add_channel({
            id: "channel_all",
            name: _lt("All messages"),
            type: "static"
        });

        return $.when();
    });

return base_obj.chat_manager;

});

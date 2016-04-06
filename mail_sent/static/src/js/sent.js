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

var _t = core._t;
//-------------------------------------------------------------------------------

// Inherit class and override methods
base_obj.MailTools.include({
    get_properties: function(msg){
        var properties = this._super.apply(this, arguments);
        properties.is_sent = this.property_descr("channel_sent", msg, this);
        return properties;
    },

    set_channel_flags: function(data, msg){
        this._super.apply(this, arguments);
        if (data.sent) {
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
            name: _t("Sent"),
            type: "static"
        });

        return $.when();
    });

return base_obj.chat_manager;

});

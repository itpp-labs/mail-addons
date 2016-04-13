odoo.define('res_partner_mails_count.sent', function (require) {
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
        properties.is_sent_to = this.property_descr("channel_sent_to", msg, this);
        return properties;
    },

    set_channel_flags: function(data, msg){
        this._super.apply(this, arguments);
        msg.is_sent_to = false;
        if (data.sent && data.author_id[0] == session.partner_id) {
            if (data.partner_ids[0] && data.partner_ids[0][0] == 5){
                msg.is_sent_to = true;
            }
        }

        return msg;
    },

    get_channel_array: function(msg){
        var arr = this._super.apply(this, arguments);
        return arr.concat('channel_sent_to');
    },

    get_domain: function(channel){
        return (channel.id === "channel_sent_to") ? [
            ['sent', '=', true],
            ['author_id.user_ids', 'in', [openerp.session.uid]]
        ] : this._super.apply(this, arguments);
    }
});

base_obj.chat_manager.is_ready.then(function(){
    // Add sent channel
    base_obj.chat_manager.mail_tools.add_channel({
        id: "channel_sent_to",
        name: _t("SentTo"),
        type: "static"
    });

    return $.when();
});

return base_obj.chat_manager;

});

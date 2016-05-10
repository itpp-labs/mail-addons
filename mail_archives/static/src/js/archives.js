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

var _lt = core._lt;
//-------------------------------------------------------------------------------

var ChatAction = core.action_registry.get('mail.chat.instant_messaging');
ChatAction.include({
    init: function(parent, action, options) {
        this._super.apply(this, arguments);
        var channel_name = 'channel_archive';
        // Add channel Archive for enable "display_subject" option
        this.channels_display_subject.push(channel_name);
    }
});

// Inherit class and override methods
base_obj.MailTools.include({
    get_properties: function(msg){
        var properties = this._super.apply(this, arguments);
        properties.is_archive = this.property_descr("channel_archive", msg, this);
        return properties;
    },

    set_channel_flags: function(data, msg){
        this._super.apply(this, arguments);
        // Get recipients ids
        var recipients_ids = [];
        for (var i = 0; i < data.partner_ids.length; i++){
            recipients_ids.push(data.partner_ids[i][0]);
        }

        // If author or recipient
        if (data.author_id[0] == session.partner_id || recipients_ids.indexOf(session.partner_id) != -1) {
            msg.is_archive = true;
        }

        return msg;
    },

    get_channel_array: function(msg){
        var arr = this._super.apply(this, arguments);
        return arr.concat('channel_archive');
    },

    get_domain: function(channel){
        return (channel.id === "channel_archive") ? [
            '|', ['partner_ids', 'in', [openerp.session.partner_id]],
            ['author_id.user_ids', 'in', [openerp.session.uid]]
        ] : this._super.apply(this, arguments);
    }
});

base_obj.chat_manager.is_ready.then(function(){
        // Add archive channel
        base_obj.chat_manager.mail_tools.add_channel({
            id: "channel_archive",
            name: _lt("Archive"),
            type: "static"
        });

        return $.when();
    });

return base_obj.chat_manager;

});

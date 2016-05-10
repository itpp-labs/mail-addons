odoo.define('mail_reply.reply', function (require) {
"use strict";

var core = require('web.core');
var base_obj = require('mail_base.base');

var ChatAction = core.action_registry.get('mail.chat.instant_messaging');
ChatAction.include({
    select_message: function(message_id) {
        this._super.apply(this, arguments);
        var message = base_obj.chat_manager.get_message(message_id);
        var subject = '';
        if (message.record_name){
            subject = "Re: " + message.record_name;
        } else if (message.subject){
            subject = "Re: " + message.subject;
        }
        this.extended_composer.set_subject(subject);
    }
});

});

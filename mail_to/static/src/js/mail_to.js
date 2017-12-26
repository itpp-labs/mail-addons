odoo.define('mail_to.MailTo', function (require) {
    "use strict";

var chat_manager = require('mail_base.base').chat_manager;

var make_message_super = chat_manager.make_message;
chat_manager.make_message = function (data) {
    var msg = make_message_super.call(this, data);
    msg.partner_ids = data.partner_ids;
    if (!msg.partner_ids) {
        return msg;
    }
    var more_recipients = '';
    // value which define more recipients
    msg.more_recipients_value = 4;
    for (var i = 0; i < msg.partner_ids.length; i++){
        if (i >= msg.more_recipients_value){
            // append names
            more_recipients += msg.partner_ids[i][1];
            // separate them with semicolon
            if (i < msg.partner_ids.length - 1){
                more_recipients += '; ';
            }
        }
    }
    msg.more_recipients = more_recipients;
    return msg;
}
    return chat_manager;
});

odoo.define('mail_to.MailTo', function (require) {
    "use strict";

    var Thread = require('mail.ChatThread');
    var Model = require('web.Model');

    Thread.include({
        render: function (messages, options) {
            // for(var i = 0; i < messages.length; i++){
            //     var msg = messages[i];
            //     msg.needaction_partner_ids = [3];
            // }
            // console.log('messages:', messages);
            this._super(messages, options);
        }
    });
});

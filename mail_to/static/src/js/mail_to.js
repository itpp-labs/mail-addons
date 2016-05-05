odoo.define('mail_to.MailTo', function (require) {
    "use strict";

    var base_obj = require('mail_base.base');

    base_obj.MailTools.include({
        make_message: function(data){
            var msg = this._super(data);
            msg.partner_ids = data.partner_ids;
            // msg.needaction_partner_ids = data.needaction_partner_ids;

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
    });
});

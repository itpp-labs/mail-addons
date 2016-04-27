odoo.define('mail_to.MailTo', function (require) {
    "use strict";

    var base_obj = require('mail_base.base');

    base_obj.MailTools.include({
        make_message: function(data){
            var msg = this._super(data);
            msg.partner_ids = data.partner_ids;
            // msg.needaction_partner_ids = data.needaction_partner_ids;
            return msg;
        }
    });
});

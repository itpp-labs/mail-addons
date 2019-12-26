/* Copyright 2016 x620 <https://github.com/x620>
 * Copyright 2016-2017 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
 * Copyright 2017 Artyom Losev <https://it-projects.info/>
 * Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */
odoo.define('mail_to.MailTo', function (require) {
    "use strict";

    var MailManager = require("mail.Manager");

    MailManager.include({
        _makeMessage: function(data) {
            var msg = this._super(data);
            msg.partner_names = data.partner_names;
            msg.channel_names = data.channel_names;
            msg.recipients = msg.partner_names.concat(msg.channel_names);

            if (!msg.partner_names && !msg.channel_names) {
                return msg;
            }

            var more_recipients = '';
            // value which define more recipients
            msg.more_recipients_value = 4;
            for (var i = 0; i < msg.recipients.length; i++){
                    if (i >= msg.more_recipients_value){
                        // append names
                        more_recipients += msg.recipients[i][1];
                        // separate them with semicolon
                        if (i < msg.recipients.length - 1){
                            more_recipients += ', ';
                        }
                    }
            }

            msg.more_recipients = more_recipients;

            return msg;
        }
    });

    return MailManager;
});

/*  # Copyright 2016-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
    # Copyright 2017-2018 Artyom Losev <https://it-projects.info/team/ArtyomLosev>
    # Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    # License MIT (https://opensource.org/licenses/MIT). */
odoo.define("mail_all.all", function(require) {
    "use strict";

    var core = require("web.core");
    var Manager = require("mail.Manager");
    var Mailbox = require("mail.model.Mailbox");

    var _t = core._t;

    Manager.include({
        _updateMailboxesFromServer: function(data) {
            var self = this;
            this._super(data);
            if (
                !_.find(this.getThreads(), function(th) {
                    return th.getID() === "mailbox_channel_all";
                })
            ) {
                this._addMailbox({
                    id: "channel_all",
                    name: _t("All Messages"),
                    mailboxCounter: 0,
                });
            }
        },

        _makeMessage: function(data) {
            var message = this._super(data);
            message._addThread("mailbox_channel_all");
            return message;
        },
    });

    Mailbox.include({
        _getThreadDomain: function() {
            if (this._id === "mailbox_channel_all") {
                return [];
            }
            return this._super();
        },
    });

    return {
        Manager: Manager,
        Mailbox: Mailbox,
    };
});

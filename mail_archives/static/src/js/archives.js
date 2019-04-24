odoo.define('mail_archives.archives', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var Manager = require('mail.Manager');
var Mailbox = require('mail.model.Mailbox');

var _t = core._t;

Manager.include({
    _updateMailboxesFromServer: function (data) {
        var self = this;
        this._super(data);
        if (!_.find(this.getThreads(), function(th){
            return th.getID() === 'mailbox_channel_archive';
        })) {
            this._addMailbox({
                id: 'channel_archive',
                name: _t("Archive"),
                mailboxCounter: data.needaction_inbox_counter || 0,
            });
        }
    },

    _makeMessage: function (data) {
        var message = this._super(data);
        message._addThread('mailbox_channel_archive');
        return message;
    },
});

Mailbox.include({
    _getThreadDomain: function () {
        if (this._id === 'mailbox_channel_archive') {
            return ['|',
                ['partner_ids', 'in', [session.partner_id]],
                ['author_id', 'in', [session.partner_id]]
            ];
        }
        return this._super();
    },
});

return {
    'Manager': Manager,
    'Mailbox': Mailbox,
};

});

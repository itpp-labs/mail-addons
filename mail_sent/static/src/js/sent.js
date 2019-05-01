odoo.define('mail_sent.sent', function (require) {
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
            return th.getID() === 'mailbox_channel_sent';
        })) {
            this._addMailbox({
                id: 'channel_sent',
                name: _t("Sent Messages"),
                mailboxCounter: data.needaction_inbox_counter || 0,
            });
        }
    },

    _makeMessage: function (data) {
        var message = this._super(data);
        message._addThread('mailbox_channel_sent');
        return message;
    },
});

Mailbox.include({
    _getThreadDomain: function () {
        if (this._id === 'mailbox_channel_sent') {
            return [
                ['sent', '=', true],
                ['author_id.user_ids', 'in', [session.uid]]
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

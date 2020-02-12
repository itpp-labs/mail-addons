odoo.define("mail_sent.sent", function(require) {
    "use strict";

    var core = require("web.core");
    var session = require("web.session");
    var Manager = require("mail.Manager");
    var Mailbox = require("mail.model.Mailbox");
    var SearchableThread = require("mail.model.SearchableThread");

    var _t = core._t;

    Manager.include({
        _updateMailboxesFromServer: function(data) {
            var self = this;
            this._super(data);
            if (
                !_.find(this.getThreads(), function(th) {
                    return th.getID() === "mailbox_channel_sent";
                })
            ) {
                this._addMailbox({
                    id: "channel_sent",
                    name: _t("Sent Messages"),
                    mailboxCounter: 0,
                });
            }
        },
    });

    SearchableThread.include({
        _fetchMessages: function(pDomain, loadMore) {
            var self = this;
            if (this._id !== "mailbox_channel_sent") {
                return this._super(pDomain, loadMore);
            }

            // This is a copy-paste from super method
            var domain = this._getThreadDomain();
            var cache = this._getCache(pDomain);
            if (pDomain) {
                domain = domain.concat(pDomain || []);
            }
            if (loadMore) {
                var minMessageID = cache.messages[0].getID();
                domain = [["id", "<", minMessageID]].concat(domain);
            }
            return this._rpc({
                model: "mail.message",
                method: "message_fetch",
                args: [domain],
                kwargs: this._getFetchMessagesKwargs(),
            }).then(function(messages) {
                // Except this function. It adds the required thread to downloaded messages
                _.each(messages, function(m) {
                    m.channel_ids.push("mailbox_channel_sent");
                });
                if (!cache.allHistoryLoaded) {
                    cache.allHistoryLoaded = messages.length < self._FETCH_LIMIT;
                }
                cache.loaded = true;
                _.each(messages, function(message) {
                    self.call("mail_service", "addMessage", message, {
                        silent: true,
                        domain: pDomain,
                    });
                });
                cache = self._getCache(pDomain || []);
                return cache.messages;
            });
        },
    });

    Mailbox.include({
        _getThreadDomain: function() {
            if (this._id === "mailbox_channel_sent") {
                return [
                    ["sent", "=", true],
                    ["author_id.user_ids", "in", [session.uid]],
                ];
            }
            return this._super();
        },
    });

    return {
        Manager: Manager,
        Mailbox: Mailbox,
    };
});

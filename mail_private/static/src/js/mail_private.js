/*  Copyright 2016-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
    Copyright 2016 manavi <https://github.com/manawi>
    Copyright 2017-2018 Artyom Losev <https://github.com/ArtyomLosev>
    Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
    License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define("mail_private", function(require) {
    "use strict";

    var core = require("web.core");
    var Chatter = require("mail.Chatter");
    var ChatterComposer = require("mail.composer.Chatter");
    var session = require("web.session");

    var rpc = require("web.rpc");
    var config = require("web.config");
    var mailUtils = require("mail.utils");

    Chatter.include({
        init: function() {
            this._super.apply(this, arguments);
            this.private = false;
            this.events["click .oe_compose_post_private"] =
                "on_open_composer_private_message";
        },

        on_open_composer_private_message: function(event) {
            var self = this;
            this.fetch_recipients_for_internal_message().then(function(data) {
                self._openComposer({
                    is_private: true,
                    suggested_partners: data,
                });
            });
        },

        _openComposer: function(options) {
            var self = this;
            var old_composer = this._composer;
            // Create the new composer
            this._composer = new ChatterComposer(
                this,
                this.record.model,
                options.suggested_partners || [],
                {
                    commandsEnabled: false,
                    context: this.context,
                    inputMinHeight: 50,
                    isLog: options && options.isLog,
                    recordName: this.recordName,
                    defaultBody:
                        old_composer &&
                        old_composer.$input &&
                        old_composer.$input.val(),
                    defaultMentionSelections:
                        old_composer && old_composer.getMentionListenerSelections(),
                    attachmentIds:
                        (old_composer && old_composer.get("attachment_ids")) || [],
                    is_private: options.is_private,
                }
            );
            this._composer.on("input_focused", this, function() {
                this._composer.mentionSetPrefetchedPartners(
                    this._mentionSuggestions || []
                );
            });
            this._composer.insertAfter(this.$(".o_chatter_topbar")).then(function() {
                // Destroy existing composer
                if (old_composer) {
                    old_composer.destroy();
                }
                self._composer.focus();
                self._composer.on("post_message", self, function(messageData) {
                    if (options.is_private) {
                        self._composer.options.isLog = true;
                    }
                    self._discardOnReload(messageData).then(function() {
                        self._disableComposer();
                        self.fields.thread
                            .postMessage(messageData)
                            .then(function() {
                                self._closeComposer(true);
                                if (self._reloadAfterPost(messageData)) {
                                    self.trigger_up("reload");
                                } else if (messageData.attachment_ids.length) {
                                    self._reloadAttachmentBox();
                                    self.trigger_up("reload", {
                                        fieldNames: ["message_attachment_count"],
                                        keepChanges: true,
                                    });
                                }
                            })
                            .fail(function() {
                                self._enableComposer();
                            });
                    });
                });
                var toggle_post_private = self._composer.options.is_private || false;
                self._composer.on(
                    "need_refresh",
                    self,
                    self.trigger_up.bind(self, "reload")
                );
                self._composer.on(
                    "close_composer",
                    null,
                    self._closeComposer.bind(self, true)
                );

                self.$el.addClass("o_chatter_composer_active");
                self.$(
                    ".o_chatter_button_new_message, .o_chatter_button_log_note, .oe_compose_post_private"
                ).removeClass("o_active");
                self.$(".o_chatter_button_new_message").toggleClass(
                    "o_active",
                    !self._composer.options.isLog && !self._composer.options.is_private
                );
                self.$(".o_chatter_button_log_note").toggleClass(
                    "o_active",
                    self._composer.options.isLog && !options.is_private
                );
                self.$(".oe_compose_post_private").toggleClass(
                    "o_active",
                    toggle_post_private
                );
            });
        },

        fetch_recipients_for_internal_message: function() {
            var self = this;
            self.result = {};
            var follower_ids_domain = [["id", "=", self.context.default_res_id]];
            return rpc
                .query({
                    model: "mail.message",
                    method: "send_recepients_for_internal_message",
                    args: [[], self.context.default_model, follower_ids_domain],
                })
                .then(function(res) {
                    return _.filter(res, function(obj) {
                        return obj.partner_id !== session.partner_id;
                    });
                });
        },
    });

    ChatterComposer.include({
        init: function(parent, model, suggestedPartners, options) {
            this._super(parent, model, suggestedPartners, options);
            this.events["click .oe_composer_uncheck"] = "on_uncheck_recipients";
            if (typeof options.is_private === "undefined") {
                // Otherwise it causes an error in context creating function
                options.is_private = false;
            }
        },

        _preprocessMessage: function() {
            var self = this;
            var def = $.Deferred();
            this._super().then(function(message) {
                message = _.extend(message, {
                    subtype: "mail.mt_comment",
                    message_type: "comment",
                    context: _.defaults({}, self.context, session.user_context),
                });

                // Subtype
                if (self.options.isLog) {
                    message.subtype = "mail.mt_note";
                }

                if (self.options.is_private) {
                    message.context.is_private = true;
                    message.channel_ids = self.get_checked_channel_ids();
                }

                // Partner_ids
                if (self.options.isLog) {
                    def.resolve(message);
                } else {
                    var check_suggested_partners = self._getCheckedSuggestedPartners();
                    self._checkSuggestedPartners(check_suggested_partners).done(
                        function(partnerIDs) {
                            message.partner_ids = (message.partner_ids || []).concat(
                                partnerIDs
                            );
                            // Update context
                            message.context = _.defaults({}, message.context, {
                                mail_post_autofollow: true,
                            });
                            def.resolve(message);
                        }
                    );
                }
            });
            return def;
        },

        on_uncheck_recipients: function() {
            this.$(".o_composer_suggested_partners input:checked").each(function() {
                $(this).prop("checked", false);
            });
        },

        _onOpenFullComposer: function() {
            if (!this._doCheckAttachmentUpload()) {
                return false;
            }
            var self = this;
            var recipientDoneDef = $.Deferred();
            this.trigger_up("discard_record_changes", {
                proceed: function() {
                    if (self.options.isLog) {
                        recipientDoneDef.resolve([]);
                    } else {
                        var checkedSuggestedPartners = self._getCheckedSuggestedPartners();
                        self._checkSuggestedPartners(checkedSuggestedPartners).then(
                            recipientDoneDef.resolve.bind(recipientDoneDef)
                        );
                    }
                },
            });
            recipientDoneDef.then(function(partnerIDs) {
                var context = {
                    default_parent_id: self.id,
                    default_body: mailUtils.getTextToHTML(self.$input.val()),
                    default_attachment_ids: _.pluck(self.get("attachment_ids"), "id"),
                    default_partner_ids: partnerIDs,
                    default_is_log: self.options.isLog,
                    mail_post_autofollow: true,
                    is_private: self.options.is_private,
                };

                if (self.options && self.options.is_private) {
                    context.default_is_private = self.options.is_private;
                }

                if (self.context.default_model && self.context.default_res_id) {
                    context.default_model = self.context.default_model;
                    context.default_res_id = self.context.default_res_id;
                }
                var action = {
                    type: "ir.actions.act_window",
                    res_model: "mail.compose.message",
                    view_mode: "form",
                    view_type: "form",
                    views: [[false, "form"]],
                    target: "new",
                    context: context,
                };
                self.do_action(action, {
                    on_close: self.trigger.bind(self, "need_refresh"),
                }).then(self.trigger.bind(self, "close_composer"));
            });
        },

        _getCheckedSuggestedPartners: function() {
            var checked_partners = this._super(this, arguments);
            // Workaround: odoo code works only when all partners are checked intially,
            // while may select only some of them (internal recepients)
            _.each(checked_partners, function(partner) {
                partner.checked = true;
            });
            checked_partners = _.uniq(
                _.filter(checked_partners, function(obj) {
                    return obj.reason !== "Channel";
                })
            );
            this.get_checked_channel_ids();
            return checked_partners;
        },

        get_checked_channel_ids: function() {
            var self = this;
            var checked_channels = [];
            this.$(".o_composer_suggested_partners input:checked").each(function() {
                var full_name = $(this).data("fullname");
                checked_channels = checked_channels.concat(
                    _.filter(self.suggested_partners, function(item) {
                        return full_name === item.full_name;
                    })
                );
            });
            checked_channels = _.uniq(
                _.filter(checked_channels, function(obj) {
                    return obj.reason === "Channel";
                })
            );
            return _.pluck(checked_channels, "channel_id");
        },
    });
});

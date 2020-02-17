/*  Copyright 2016 x620 <https://github.com/x620>
    Copyright 2016 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
    Copyright 2016 manawi <https://github.com/manawi>
    Copyright 2017 Artyom Losev <https://github.com/ArtyomLosev>
    Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
    License MIT (https://opensource.org/licenses/MIT). */
odoo.define("mail_private", function(require) {
    "use strict";

    var Chatter = require("mail.Chatter");
    var MailComposer = require("mail_base.base").MailComposer;
    var chat_manager = require("mail.chat_manager");
    var session = require("web.session");
    var Model = require("web.Model");
    var utils = require("mail.utils");

    Chatter.include({
        init: function() {
            this._super.apply(this, arguments);
            this.private = false;
            this.events["click .oe_compose_post_private"] =
                "on_open_composer_private_message";
        },

        on_post_message: function(message) {
            var self = this;
            if (this.private) {
                message.subtype = false;
                message.channel_ids = this.get_checked_channels_ids();
            }
            var options = {model: this.model, res_id: this.res_id};
            chat_manager
                .post_message(message, options)
                .then(function() {
                    self.close_composer();
                    if (message.partner_ids.length) {
                        self.refresh_followers();
                    }
                })
                .fail(function() {
                    // Todo: display notification
                });
        },

        on_open_composer_private_message: function(event) {
            var self = this;
            this.private = true;
            this.get_recipients_for_internal_message()
                .then(function(data) {
                    self.recipients_for_internal_message = data;
                    return self.get_channels_for_internal_message();
                })
                .then(function(data) {
                    self.channels_for_internal_message = data;
                    self.get_internal_users_ids().then(function(res_ids) {
                        self.open_composer({is_private: true, internal_ids: res_ids});
                    });
                });
        },

        on_open_composer_new_message: function() {
            this._super.apply(this, arguments);
            this.private = false;
            this.context.is_private = false;
        },

        open_composer: function(options) {
            var self = this;
            this._super.apply(this, arguments);
            if (options && options.is_private) {
                self.internal_users_ids = options.internal_ids;
                this.composer.options.is_private = options.is_private;

                _.each(self.recipients_for_internal_message, function(partner) {
                    self.composer.suggested_partners.push({
                        checked:
                            _.intersection(self.internal_users_ids, partner.user_ids)
                                .length > 0,
                        partner_id: partner.id,
                        full_name: partner.name,
                        name: partner.name,
                        email_address: partner.email,
                        reason: _.include(partner.user_ids, self.session.uid)
                            ? "Partner"
                            : "Follower",
                    });
                });

                _.each(self.channels_for_internal_message, function(channel) {
                    self.composer.suggested_channels.push({
                        checked: true,
                        channel_id: channel.id,
                        full_name: channel.name,
                        name: "# " + channel.name,
                    });
                });
            }
        },

        get_recipients_for_internal_message: function() {
            var self = this;
            self.result = {};
            return new Model(this.context.default_model)
                .query(["message_follower_ids", "partner_id"])
                .filter([["id", "=", self.context.default_res_id]])
                .all()
                .then(function(thread) {
                    var follower_ids = thread[0].message_follower_ids;
                    self.result[self.context.default_res_id] = [];
                    self.customer = thread[0].partner_id;

                    // Fetch partner ids
                    return new Model("mail.followers")
                        .call("read", [follower_ids, ["partner_id"]])
                        .then(function(res_partners) {
                            // Filter result and push to array
                            var res_partners_filtered = _.map(res_partners, function(
                                partner
                            ) {
                                if (
                                    partner.partner_id[0] &&
                                    partner.partner_id[0] !== session.partner_id
                                ) {
                                    return partner.partner_id[0];
                                }
                            }).filter(function(partner) {
                                return typeof partner !== "undefined";
                            });

                            return new Model("res.partner")
                                .call("read", [
                                    res_partners_filtered,
                                    ["name", "email", "user_ids"],
                                ])
                                .then(function(recipients) {
                                    return recipients;
                                });
                        });
                });
        },

        get_channels_for_internal_message: function() {
            var self = this;
            self.result = {};
            return new Model(this.context.default_model)
                .query(["message_follower_ids", "partner_id"])
                .filter([["id", "=", self.context.default_res_id]])
                .all()
                .then(function(thread) {
                    var follower_ids = thread[0].message_follower_ids;
                    self.result[self.context.default_res_id] = [];
                    self.customer = thread[0].partner_id;

                    // Fetch channels ids
                    return new Model("mail.followers")
                        .call("read", [follower_ids, ["channel_id"]])
                        .then(function(res_channels) {
                            // Filter result and push to array
                            var res_channels_filtered = _.map(res_channels, function(
                                channel
                            ) {
                                if (channel.channel_id[0]) {
                                    return channel.channel_id[0];
                                }
                            }).filter(function(channel) {
                                return typeof channel !== "undefined";
                            });

                            return new Model("mail.channel")
                                .call("read", [res_channels_filtered, ["name", "id"]])
                                .then(function(recipients) {
                                    return recipients;
                                });
                        });
                });
        },

        get_internal_users_ids: function() {
            var ResUser = new Model("mail.compose.message");
            this.users_ids = ResUser.call("get_internal_users_ids", [[]]).then(function(
                users_ids
            ) {
                return users_ids;
            });
            return this.users_ids;
        },

        get_checked_channels_ids: function() {
            var self = this;
            var checked_channels = [];
            this.$(".o_composer_suggested_channels input:checked").each(function() {
                var full_name = $(this)
                    .data("fullname")
                    .toString();
                _.each(self.channels_for_internal_message, function(item) {
                    if (full_name === item.name) {
                        checked_channels.push(item.id);
                    }
                });
            });
            return checked_channels;
        },
    });

    MailComposer.include({
        init: function(parent, dataset, options) {
            this._super(parent, dataset, options);
            this.events["click .oe_composer_uncheck"] = "on_uncheck_recipients";
            this.suggested_channels = [];
        },

        on_uncheck_recipients: function() {
            this.$(".o_composer_suggested_partners input:checked").each(function() {
                $(this).prop("checked", false);
            });
            this.$(".o_composer_suggested_channels input:checked").each(function() {
                $(this).prop("checked", false);
            });
        },

        preprocess_message: function() {
            var self = this;
            if (self.options.is_private) {
                self.context.is_private = true;
            }
            return this._super();
        },

        on_open_full_composer: function() {
            if (!this.do_check_attachment_upload()) {
                return false;
            }

            var self = this;
            var recipient_done = $.Deferred();
            if (this.options.is_log) {
                recipient_done.resolve([]);
            } else {
                var checked_suggested_partners = this.get_checked_suggested_partners();
                recipient_done = this.check_suggested_partners(
                    checked_suggested_partners
                );
            }
            recipient_done.then(function(partner_ids) {
                var context = {
                    default_parent_id: self.id,
                    default_body: utils.get_text2html(self.$input.val()),
                    default_attachment_ids: _.pluck(self.get("attachment_ids"), "id"),
                    default_partner_ids: partner_ids,
                    default_is_log: self.options.is_log,
                    mail_post_autofollow: true,
                };

                if (self.options && self.options.is_private) {
                    context.default_is_private = self.options.is_private;
                }

                if (self.context.default_model && self.context.default_res_id) {
                    context.default_model = self.context.default_model;
                    context.default_res_id = self.context.default_res_id;
                }

                self.do_action(
                    {
                        type: "ir.actions.act_window",
                        res_model: "mail.compose.message",
                        view_mode: "form",
                        view_type: "form",
                        views: [[false, "form"]],
                        target: "new",
                        context: context,
                    },
                    {
                        on_close: function() {
                            self.trigger("need_refresh");
                            var parent = self.getParent();
                            chat_manager.get_messages({
                                model: parent.model,
                                res_id: parent.res_id,
                            });
                        },
                    }
                ).then(self.trigger.bind(self, "close_composer"));
            });
        },

        get_checked_suggested_partners: function() {
            var checked_partners = this._super(this, arguments);
            // Workaround: odoo code works only when all partners are checked intially,
            // while may select only some of them (internal recepients)
            _.each(checked_partners, function(partner) {
                partner.checked = true;
            });
            return checked_partners;
        },
    });
});

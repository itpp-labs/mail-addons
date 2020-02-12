odoo.define("mail_move_message.relocate", function(require) {
    "use strict";

    var chat_manager = require("mail.chat_manager");
    var base_obj = require("mail_base.base");
    var thread = require("mail.ChatThread");
    var chatter = require("mail.Chatter");
    var Model = require("web.Model");
    var form_common = require("web.form_common");
    var widgets = require("web.form_widgets");
    var core = require("web.core");

    var _t = core._t;

    thread.include({
        init: function() {
            this._super.apply(this, arguments);
            // Add click reaction in the events of the thread object
            this.events["click .oe_move"] = function(event) {
                var message_id = $(event.currentTarget).data("message-id");
                this.trigger("move_message", message_id);
            };
        },
        on_move_message: function(message_id) {
            var action = {
                name: _t("Relocate Message"),
                type: "ir.actions.act_window",
                res_model: "mail_move_message.wizard",
                view_mode: "form",
                view_type: "form",
                views: [[false, "form"]],
                target: "new",
                context: {default_message_id: message_id},
            };

            this.do_action(action, {
                on_close: function() {
                    // Empty
                },
            });
        },
    });

    chatter.include({
        start: function() {
            var result = this._super.apply(this, arguments);
            // For show wizard in the form
            this.thread.on("move_message", this, this.thread.on_move_message);
            return $.when(result).done(function() {
                // TODO: do we need .done(...) part?
            });
        },
    });

    var ChatAction = core.action_registry.get("mail.chat.instant_messaging");
    ChatAction.include({
        start: function() {
            var result = this._super.apply(this, arguments);
            // For show wizard in the channels
            this.thread.on("move_message", this, this.thread.on_move_message);
            return $.when(result).done(function() {
                // TODO: do we need .done(...) part?
            });
        },
    });

    base_obj.MailTools.include({
        make_message: function(data) {
            var msg = this._super(data);
            // Mark msg as moved after reload
            msg.is_moved = data.is_moved || false;
            return msg;
        },
        on_notification: function(notifications) {
            this._super(notifications);
            var self = this;
            _.each(notifications, function(notification) {
                var model = notification[0][1];
                var message_id = notification[1].id;
                var message = base_obj.chat_manager.get_message(message_id);
                if (model === "mail_move_message" && message) {
                    message.res_id = notification[1].res_id;
                    message.model = notification[1].model;
                    message.record_name = notification[1].record_name;
                    // Mark message as moved after move
                    message.is_moved = notification[1].is_moved;
                    // Update cache and accordingly message in the thread
                    self.add_to_cache(message, []);
                    // Call thread.on_update_message(message)
                    chat_manager.bus.trigger("update_message", message);
                } else if (model === "mail_move_message.delete_message") {
                    self.remove_from_cache(message, []);
                    chat_manager.bus.trigger("update_message", message);
                }
            });
        },
    });

    widgets.WidgetButton.include({
        on_click: function() {
            if (this.node.attrs.special === "quick_create") {
                var self = this;
                var related_field = this.field_manager.fields[this.node.attrs.field];
                var context_built = $.Deferred();
                if (this.node.attrs.use_for_mail_move_message) {
                    var model = new Model(this.view.dataset.model);
                    var partner_id = self.field_manager.fields.partner_id.get_value();
                    var message_name_from = self.field_manager.fields.message_name_from.get_value();
                    var message_email_from = self.field_manager.fields.message_email_from.get_value();
                    context_built = model.call("create_partner", [
                        self.view.dataset.context.default_message_id,
                        related_field.field.relation,
                        partner_id,
                        message_name_from,
                        message_email_from,
                    ]);
                } else {
                    context_built.resolve(this.build_context());
                }
                $.when(context_built).pipe(function(context) {
                    if (self.node.attrs.use_for_mail_move_message) {
                        self.field_manager.fields.partner_id.set_value(
                            context.partner_id
                        );
                    }
                    var dialog = new form_common.FormViewDialog(self, {
                        res_model: related_field.field.relation,
                        res_id: false,
                        context: context,
                        title: _t("Create new record"),
                    }).open();
                    dialog.on("closed", self, function() {
                        self.force_disabled = false;
                        self.check_disable();
                    });
                    dialog.on("create_completed", self, function(id) {
                        related_field.set_value(id);
                        if (self.field_manager.fields.filter_by_partner) {
                            self.field_manager.fields.filter_by_partner.set_value(true);
                        }
                    });
                });
            } else {
                this._super.apply(this, arguments);
            }
        },
    });
});

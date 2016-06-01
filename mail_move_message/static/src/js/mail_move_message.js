odoo.define('mail_move_message.relocate', function (require) {
    "use strict";

    var chat_manager = require('mail.chat_manager');
    var base_obj = require('mail_base.base');
    var Model = require('web.Model');
    var form_common = require('web.form_common');
    var core = require('web.core');

    var QWeb = core.qweb;
    var _t = core._t;

    var ChatAction = core.action_registry.get('mail.chat.instant_messaging');
    ChatAction.include({
        start: function() {
            var result = this._super.apply(this, arguments);
            
            this.$buttons = $(QWeb.render("mail.chat.ControlButtons", {}));
            this.$buttons.find('button').css({display:"inline-block"});
            this.$buttons.on('click', '.oe_move', this.on_move_message);

            return $.when(result).done(function() {});
        },

        on_move_message: function(event){
            var self = this;
            var id = $(event.target).data('oe-id');
            var context = {'default_message_id': id};
            var action = {
                name: _t('Relocate Message'),
                type: 'ir.actions.act_window',
                res_model: 'mail_move_message.wizard',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: context
            };

            self.do_action(action, {
                'on_close': function(message){
                    chat_manager.bus.trigger('update_message', message);
                }
            });
        }
    });

    base_obj.MailTools.include({
        make_message: function(data){
            var msg = this._super(data);
            msg.is_moved = data.is_moved || false;
            return msg;
        }
    });

    var widgets = require('web.form_widgets');
    widgets.WidgetButton.include({
        on_click: function(){
            if(this.node.attrs.special == 'quick_create'){
                var self = this;
                var related_field = this.field_manager.fields[this.node.attrs['field']];
                var context_built = $.Deferred();
                if(this.node.attrs.use_for_mail_move_message) {
                    var model = new Model(this.view.dataset.model);
                    var partner_id = self.field_manager.fields['partner_id'].get_value();
                    var message_name_from = self.field_manager.fields['message_name_from'].get_value();
                    var message_email_from = self.field_manager.fields['message_email_from'].get_value();
                    context_built = model.call('create_partner', [
                            self.view.dataset.context.default_message_id,
                            related_field.field.relation,
                            partner_id,
                            message_name_from,
                            message_email_from
                        ]);
                }
                else {
                    context_built.resolve(this.build_context());
                }
                $.when(context_built).pipe(function (context) {
                    if(self.node.attrs.use_for_mail_move_message) {
                        self.field_manager.fields['partner_id'].set_value(context['partner_id']);
                    }
                    var dialog = new form_common.FormViewDialog(self, {
                        res_model: related_field.field.relation,
                        res_id: false,
                        context: context,
                        title: _t("Create new record")
                    }).open();
                    dialog.on('closed', self, function () {
                        self.force_disabled = false;
                        self.check_disable();
                    });
                    dialog.on('create_completed', self, function(id) {
                        related_field.set_value(id);
                        if(self.field_manager.fields['filter_by_partner']) {
                            self.field_manager.fields['filter_by_partner'].set_value(true);
                        }
                    });
                });
            }
            else {
                this._super.apply(this, arguments);
            }
        }
    });
});

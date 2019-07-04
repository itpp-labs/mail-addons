/*  Copyright 2016 x620 <https://github.com/x620>
    Copyright 2016 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
    Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
    License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
openerp.mail_private = function(instance){

    var mail = instance.mail;

    instance.mail.ThreadComposeMessage.include({
        init: function (parent, datasets, options) {
            this._super.apply(this, arguments);
            var self = this;
            this.private = false;
            self.recipients = [];
        },
        on_uncheck_recipients: function () {
            this.$(".oe_recipients")
            .find("input:checked").each(function() {
                $(this).prop("checked", false);
            });
            _.each(this.recipients, function(res) {
                res.checked = false;
            });
        },
        bind_events: function(){
            var self = this;
            this.$('.oe_compose_post_private').on('click', self.on_toggle_quick_composer_private);
            this.$('.oe_composer_uncheck').on('click', self.on_uncheck_recipients);
            this._super.apply(this, arguments);
        },
        on_compose_fullmail: function (default_composition_mode) {
            var self = this;
            if(!this.do_check_attachment_upload()) {
                return false;
            }
            var recipient_done = $.Deferred();
            if (this.is_log) {
                recipient_done.resolve([]);
            }
            else {
                recipient_done = this.check_recipient_partners();
            }
            $.when(recipient_done).done(function (partner_ids) {
                var context = {
                    'default_parent_id': self.id,
                    'default_body': mail.ChatterUtils.get_text2html(self.$el ? (self.$el.find('textarea:not(.oe_compact)').val() || '') : ''),
                    'default_attachment_ids': _.map(self.attachment_ids, function (file) {return file.id;}),
                    'default_partner_ids': partner_ids,
                    'default_is_log': self.is_log,
                    'default_private': self.private,
                    'mail_post_autofollow': true,
                    'mail_post_autofollow_partner_ids': partner_ids,
                    'is_private': self.is_private
                };
                if (default_composition_mode != 'reply' && self.context.default_model && self.context.default_res_id) {
                    context.default_model = self.context.default_model;
                    context.default_res_id = self.context.default_res_id;
                }

                var action = {
                    type: 'ir.actions.act_window',
                    res_model: 'mail.compose.message',
                    view_mode: 'form',
                    view_type: 'form',
                    views: [[false, 'form']],
                    target: 'new',
                    context: context,
                };

                self.do_action(action, {
                    'on_close': function(){ !self.parent_thread.options.view_inbox && self.parent_thread.message_fetch(); }
                });
                self.on_cancel();
            });

        },
        do_send_message_post: function (partner_ids, log) {
            var self = this;
            var values = {
                'body': this.$('textarea').val(),
                'subject': false,
                'parent_id': this.context.default_parent_id,
                'attachment_ids': _.map(this.attachment_ids, function (file) {return file.id;}),
                'partner_ids': partner_ids,
                'context': _.extend(this.parent_thread.context, {
                    'mail_post_autofollow': true,
                    'mail_post_autofollow_partner_ids': partner_ids,
                    'default_private': self.private
                }),
                'type': 'comment',
                'content_subtype': 'plaintext',
            };
            if (log || self.private) {
                values.subtype = false;
            }
            else {
                values.subtype = 'mail.mt_comment';
            }
            this.parent_thread.ds_thread._model.call('message_post', [this.context.default_res_id], values).done(function (message_id) {
                var thread = self.parent_thread;
                var root = thread == self.options.root_thread;
                if (self.options.display_indented_thread < self.thread_level && thread.parent_message) {
                    var thread = thread.parent_message.parent_thread;
                }
                // create object and attach to the thread object
                thread.message_fetch([["id", "=", message_id]], false, [message_id], function (arg, data) {
                    var message = thread.create_message_object( data.slice(-1)[0] );
                    // insert the message on dom
                    thread.insert_message( message, root ? undefined : self.$el, root );
                });
                self.on_cancel();
                self.flag_post = false;
            });
        },
        on_toggle_quick_composer: function (event) {
            if (event.target.className == 'oe_compose_post') {
                this.recipients = [];
                this.private = false;
            }
            this._super.apply(this, arguments);
        },
        on_toggle_quick_composer_private: function (event) {
            this.recipients = [];
            var self = this;
            var $input = $(event.target);
            this.compute_emails_from();
            var email_addresses = _.pluck(this.recipients, 'email_address');
            this.get_internal_users_ids().then(function(res_ids){
                self.internal_users_ids = res_ids;
                var suggested_partners = $.Deferred();

                // if clicked: call for suggested recipients
                if (event.type === 'click') {
                    self.private = $input.hasClass('oe_compose_post_private');
                    self.is_log = false;
                    suggested_partners = self.parent_thread.get_recipients_for_internal_message([self.context.default_res_id], self.context)
                        .done(function (additional_recipients) {
                            var thread_recipients = additional_recipients[self.context.default_res_id];
                            _.each(thread_recipients, function (recipient) {
                                var parsed_email = mail.ChatterUtils.parse_email(recipient[1]);
                                if (_.indexOf(email_addresses, parsed_email[1]) === -1) {
                                    self.recipients.push({
                                        'checked': _.intersection(self.internal_users_ids, recipient[3]).length > 0,
                                        'partner_id': recipient[0],
                                        'full_name': recipient[1],
                                        'name': parsed_email[0],
                                        'email_address': parsed_email[1],
                                        'reason': recipient[2],
                                    });
                                }
                            });
                        });
                }
                else {
                    suggested_partners.resolve({});
                }
                // uncheck partners from compute_emails_from
                _.each(self.recipients, function(r){
                    if (!r.partner_id){
                        r.checked = false;
                    }
                });

                // when call for suggested partners finished: re-render the widget
                $.when(suggested_partners).pipe(function (additional_recipients) {
                    if ((!self.stay_open || (event && event.type === 'click')) && (!self.show_composer || !self.$('textarea:not(.oe_compact)').val().match(/\S+/) && !self.attachment_ids.length)) {
                        self.show_composer = !self.show_composer || self.stay_open;
                        self.reinit();
                    }
                    if (!self.stay_open && self.show_composer && (!event || event.type !== 'blur')) {
                        self.$('textarea:not(.oe_compact):first').focus();
                    }
                });

                return suggested_partners;
            });

        },
        get_internal_users_ids: function () {
            var ResUser = new instance.web.Model('mail.compose.message');
            return ResUser.call('get_internal_users_ids', [[]]).then( function (users_ids) {
                return users_ids;
            });
        }
    });

    instance.mail.Thread.include({
        get_recipients_for_internal_message: function(ids, context){
            var self = this;
            self.result = {};
            return new instance.web.Model(context.default_model).call(
                'read', [ids, ['message_follower_ids', 'partner_id'], context]
            ).then(function (thread) {
                for (var i = 0; i < thread.length; i++) {
                    var res_id = thread[i].id;
                    var recipient_ids = thread[i].message_follower_ids;
                    self.result[res_id] = [];

                    // Add customer
                    self.customer = thread[i].partner_id;
                    if (self.customer && !recipient_ids.includes(self.customer[0])) {
                        recipient_ids.splice(0, 0, self.customer[0]);
                    }

                    return new instance.web.Model('res.partner').call(
                        'read', [recipient_ids, ['name', 'email', 'user_ids']]
                    ).then(function (res_partners){
                        for (var j = 0; j < res_partners.length; j++) {
                            var partner = res_partners[j];
                            if (!_.include(partner.user_ids, self.session.uid)){
                                var reason = 'Follower';
                                if (self.customer && partner.id == self.customer[0]){
                                    reason = 'Partner';
                                }
                                self.result[res_id].push(
                                    [partner.id, partner.name + '<' + partner.email + '>', reason, partner.user_ids]
                                );
                            }
                        }
                        return self.result;
                    });
                }
                return self.result;
            });
        }
    });
};

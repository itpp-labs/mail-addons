odoo.define("mail_recovery", function(require) {
    "use strict";
    var composer = require("mail.composer");

    composer.BasicComposer.include({
        init: function() {
            this._super.apply(this, arguments);
            this.events["focus .o_composer_input textarea"] = "on_focus_textarea";
            this.events["keyup .o_composer_input textarea"] = "on_keyup_textarea";
        },
        on_focus_textarea: function(event) {
            var $input = $(event.target);
            if (!$input.val()) {
                $input.val(window.localStorage.message_storage);
            }
        },
        on_keyup_textarea: function(event) {
            window.localStorage.message_storage = $(event.target).val();
        },
        send_message: function(event) {
            window.localStorage.message_storage = "";
            return this._super(event);
        },
    });
});

import odoo.tests


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_01_mail_all(self):
        # wait till page loaded and then click and wait again
        code = """
            setTimeout(function () {
                var reply_button = $('.o_mail_info:not(:has(.o_document_link))').find(".fa.fa-reply.o_thread_icon.o_thread_message_reply");
                if (reply_button.length === 0) {
                    console.log('error');
                }
                reply_button[0].click();

                setTimeout(function () {
                    var send_button = $(".btn.btn-sm.btn-primary.o_composer_button_send.hidden-xs:visible");
                    if (send_button.length === 0) {
                        console.log('error');
                    }
                    $("textarea.o_input.o_composer_text_field")[1].value = 'test';
                    send_button.click();

                    setTimeout(function () {
                        if ($(".alert.o_mail_snackbar:visible").length === 0) {
                            console.log('error');
                        } else {
                            console.log('ok');
                        }
                    }, 1000);

                }, 3000);

            }, 1000);
        """
        link = '/web#action=%s' % self.ref('mail.mail_channel_action_client_chat')
        self.phantom_js(link, code, "odoo.__DEBUG__.services['mail_reply.reply']", login="admin")

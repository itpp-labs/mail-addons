# -*- coding: utf-8 -*-
import odoo.tests


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_01_mail_all(self):
        # wait till page loaded and then click and wait again
        code = """
            setTimeout(function () {
                $(".fa fa-reply.o_thread_icon.o_thread_message_reply").click();
                setTimeout(function () {
                    $("o_input o_composer_text_field")
                    .val($('o_input o_composer_text_field').val()+ "test");

                    $("btn btn-sm btn-primary o_composer_button_send hidden-xs").click();
                    setTimeout(function () {
                        console.log('ok');
                    }, 3000);   
                }, 3000);
            }, 1000);
        """
        link = '/web#action=%s' % self.ref('mail.mail_channel_action_client_chat')
        self.phantom_js(link, code, "odoo.__DEBUG__.services['mail_reply.reply']", login="admin")

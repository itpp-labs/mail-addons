import odoo.tests


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_01_mail_to(self):
        # checks the presence of an element with a link to the recipient
        # TODO: instead of timeout, try to put $('a.recipient_link') as ready argument of phantom_js (third parameter)
        code = """
            setTimeout(function () {
                $('a.recipient_link')[0].click();
                console.log('ok');
            }, 1000);
        """
        link = '/web#action=%s' % self.ref('mail.mail_channel_action_client_chat')
        self.phantom_js(link, code, "odoo.__DEBUG__.services['mail_to.MailTo']", login="admin")

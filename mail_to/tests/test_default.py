from werkzeug import url_encode

import odoo.tests


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):
    def test_01_mail_to(self):
        # checks the presence of an element with a link to the recipient

        env = self.env
        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        env["ir.module.module"].search(
            [("name", "=", "mail_to")], limit=1
        ).state = "installed"

        # Handle messages in Odoo
        res_users_ids = env["res.users"].search([])
        res_users_ids.write({"notification_type": "inbox"})

        # demo messages
        partner_ids = env["res.partner"].search([])
        msg = env["mail.message"].create(
            {
                "subject": "_Test",
                "body": self._testMethodName,
                "subtype_id": self.ref("mail.mt_comment"),
                "model": "mail.channel",
                "partner_ids": [(6, 0, [i.id for i in partner_ids])],
            }
        )
        # notifications for everyone
        for p in partner_ids.ids:
            env["mail.notification"].create(
                {"res_partner_id": p, "mail_message_id": msg.id, "is_read": False}
            )
        code = """
            setTimeout(function () {
                console.log($('a.recipient_link').length && 'ok' || 'error');
            }, 3000);
        """

        link = "/web#%s" % url_encode({"action": "mail.action_discuss"})
        self.phantom_js(
            link,
            code,
            "odoo.__DEBUG__.services['web_tour.tour'].tours.mail_tour.ready",
            login="admin",
        )

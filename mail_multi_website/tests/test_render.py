# Copyright 2018,2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).
# License OPL-1 (https://www.odoo.com/documentation/user/13.0/legal/licenses/licenses.html#odoo-apps) for derivative work.
import base64

from odoo.addons.test_mail.tests.test_mail_mail import TestMail


class TestRender(TestMail):
    at_install = True
    post_install = True

    def setUp(self):
        super(TestRender, self).setUp()

        self.original_email = self.env.user.email
        self.original_company = self.env.user.company_id
        self.email = "superadmin@second-website.example"
        self.assertNotEqual(self.original_email, self.email)

        self.website = self.env.ref("website.website2")
        self.company = self.env["res.company"].create({"name": "New Test Website"})
        self.website.company_id = self.company
        self.mail_server_id = self.env["ir.mail_server"].create(
            {"name": "mail server", "smtp_host": "mail.example.com"}
        )
        self.website.mail_server_id = self.mail_server_id

        user_admin = self.env.ref("base.user_admin")
        # copy-paste from mail.tests.test_mail_template
        self._attachments = [
            {
                "name": "first.txt",
                "datas": base64.b64encode(b"My first attachment"),
                "res_model": "res.partner",
                "res_id": user_admin.partner_id.id,
            },
            {
                "name": "second.txt",
                "datas": base64.b64encode(b"My second attachment"),
                "res_model": "res.partner",
                "res_id": user_admin.partner_id.id,
            },
        ]

        self.partner_1 = self.env["res.partner"].create({"name": "partner_1"})
        self.partner_2 = self.env["res.partner"].create({"name": "partner_2"})
        self.email_1 = "test1@example.com"
        self.email_2 = "test2@example.com"
        self.email_3 = self.partner_1.email
        self.email_template = self.env["mail.template"].create(
            {
                "model_id": self.env["ir.model"]._get("mail.test").id,
                "name": "Pigs Template",
                "subject": "${website.name}",
                "body_html": "${object.description}",
                "user_signature": False,
                "attachment_ids": [
                    (0, 0, self._attachments[0]),
                    (0, 0, self._attachments[1]),
                ],
                "partner_to": "%s,%s"
                % (self.partner_2.id, self.user_employee.partner_id.id),
                "email_to": "{}, {}".format(self.email_1, self.email_2),
                "email_cc": "%s" % self.email_3,
            }
        )

    def switch_user_website(self):
        # add website to allowed
        self.env.user.write(
            dict(
                backend_website_ids=[(4, self.website.id)],
                backend_website_id=self.website.id,
                company_id=self.company.id,
                company_ids=[(4, self.company.id)],
            )
        )

    def test_website_in_render_variables(self):
        """Mail values are per website"""

        self.env.user.backend_website_id = None
        TestModel = self.env["mail.test"].with_context(
            {"mail_create_nolog": True, "mail_create_nosubscribe": True}
        )
        self.test_pigs = TestModel.create(
            {
                "name": "Pigs",
                "description": "Fans of Pigs, unite !",
                "alias_name": "pigs",
                "alias_contact": "followers",
            }
        )

        # sending without website
        mail_id = self.email_template.send_mail(self.test_pigs.id)
        mail = self.env["mail.mail"].browse(mail_id)
        self.assertEqual(mail.subject, "")
        self.assertFalse(mail.mail_server_id)

        # sending from frontend
        self.test_pigs.company_id = None
        mail_id = self.email_template.with_context(
            wdb=True, allowed_website_ids=self.website.ids
        ).send_mail(self.test_pigs.id)
        mail = self.env["mail.mail"].browse(mail_id)
        self.assertEqual(mail.subject, self.website.name)
        self.assertEqual(mail.mail_server_id, self.mail_server_id)

        # copy-pasted tests
        self.assertEqual(mail.email_to, self.email_template.email_to)
        # for some reason self.email_template.email_cc might return u'False'
        self.assertEqual(
            mail.email_cc or "False", self.email_template.email_cc or "False"
        )
        self.assertEqual(
            mail.recipient_ids, self.partner_2 | self.user_employee.partner_id
        )

        # sending from frontend
        self.switch_user_website()
        mail_id = self.email_template.send_mail(self.test_pigs.id)
        mail = self.env["mail.mail"].browse(mail_id)
        self.assertEqual(mail.subject, self.website.name)

    def _test_message_post_with_template(self):
        # It's deactivated, because workaround is based on checking host value in get_current_website()
        """Simulate sending email on eCommerce checkout"""
        self.switch_user_website()
        self.env.user.email = self.email
        self.env.user.invalidate_cache()
        self.env.user.invalidate_cache()
        self.assertEqual(self.env.user.email, self.email)
        # switch admin user back
        self.env.user.company_id = self.original_company
        self.env.user.invalidate_cache()
        self.assertEqual(self.env.user.email, self.original_email)

        self.test_pigs.with_context(
            allowed_website_ids=self.website.ids
        ).message_post_with_template(self.email_template.id)
        message = self.env["mail.message"].search([], order="id desc", limit=1)
        self.assertIn("<%s>" % self.email, message.email_from)

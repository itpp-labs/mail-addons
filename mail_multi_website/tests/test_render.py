# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import base64

from odoo.addons.mail.tests.common import TestMail


class TestRender(TestMail):
    at_install = True
    post_install = True

    def setUp(self):
        super(TestRender, self).setUp()

        self.original_email = self.env.user.email
        self.original_company = self.env.user.company_id
        self.email = 'superadmin@second-website.example'
        self.assertNotEqual(self.original_email, self.email)

        self.website = self.env.ref('website.website2')
        self.company = self.env['res.company'].create({
            'name': 'New Test Website'
        })
        self.website.company_id = self.company
        self.mail_server_id = self.env['ir.mail_server'].create({
            'name': 'mail server',
            'smtp_host': 'mail.example.com',
        })
        self.website.mail_server_id = self.mail_server_id

        # copy-paste from mail.tests.test_mail_template
        self._attachments = [{
            'name': '_Test_First',
            'datas_fname':
            'first.txt',
            'datas': base64.b64encode(b'My first attachment'),
            'res_model': 'res.partner',
            'res_id': self.user_admin.partner_id.id
        }, {
            'name': '_Test_Second',
            'datas_fname': 'second.txt',
            'datas': base64.b64encode(b'My second attachment'),
            'res_model': 'res.partner',
            'res_id': self.user_admin.partner_id.id
        }]

        self.email_1 = 'test1@example.com'
        self.email_2 = 'test2@example.com'
        self.email_3 = self.partner_1.email
        self.email_template = self.env['mail.template'].create({
            'model_id': self.env['ir.model']._get('mail.test').id,
            'name': 'Pigs Template',
            'subject': '${website.name}',
            'body_html': '${object.description}',
            'user_signature': False,
            'attachment_ids': [(0, 0, self._attachments[0]), (0, 0, self._attachments[1])],
            'partner_to': '%s,%s' % (self.partner_2.id, self.user_employee.partner_id.id),
            'email_to': '%s, %s' % (self.email_1, self.email_2),
            'email_cc': '%s' % self.email_3})

    def switch_user_website(self):
        # add website to allowed
        self.env.user.write(dict(
            backend_website_ids=[(4, self.website.id)],
            backend_website_id=self.website.id,
            company_id=self.company.id,
            company_ids=[(4, self.company.id)]
        ))

    def test_website_in_render_variables(self):
        """Mail values are per website"""

        self.env.user.backend_website_id = None

        # sending without website
        mail_id = self.email_template.send_mail(self.test_pigs.id)
        mail = self.env['mail.mail'].browse(mail_id)
        self.assertEqual(mail.subject, '')
        self.assertFalse(mail.mail_server_id)

        # sending from frontend
        self.test_pigs.company_id = None
        mail_id = self.email_template.with_context(wdb=True, website_id=self.website.id).send_mail(self.test_pigs.id)
        mail = self.env['mail.mail'].browse(mail_id)
        self.assertEqual(mail.subject, self.website.name)
        self.assertEqual(mail.mail_server_id, self.mail_server_id)

        # copy-pasted tests
        self.assertEqual(mail.email_to, self.email_template.email_to)
        self.assertEqual(mail.email_cc, self.email_template.email_cc)
        self.assertEqual(mail.recipient_ids, self.partner_2 | self.user_employee.partner_id)

        # sending from frontend
        self.switch_user_website()
        mail_id = self.email_template.send_mail(self.test_pigs.id)
        mail = self.env['mail.mail'].browse(mail_id)
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

        self.test_pigs.with_context(website_id=self.website.id).message_post_with_template(self.email_template.id)
        message = self.env['mail.message'].search([], order='id desc', limit=1)
        self.assertIn('<%s>' % self.email, message.email_from)

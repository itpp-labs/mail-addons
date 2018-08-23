# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import base64

from odoo.addons.mail.tests.common import TestMail


class TestRender(TestMail):
    at_install = True
    post_install = True

    def setUp(self):
        super(TestRender, self).setUp()
        self.website = self.env.ref('website.website2')
        self.company = self.env['res.company'].create({
            'name': 'New Test Website'
        })
        self.website.company_id = self.company

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
        """Email body must be per-website and per-language"""

        # sending without website
        mail_id = self.email_template.send_mail(self.test_pigs.id)
        mail = self.env['mail.mail'].browse(mail_id)
        self.assertEqual(mail.subject, '')

        # sending from frontend
        mail_id = self.email_template.with_context(website_id=self.website.id).send_mail(self.test_pigs.id)
        mail = self.env['mail.mail'].browse(mail_id)
        self.assertEqual(mail.subject, self.website.name)

        # copy-pasted tests
        self.assertEqual(mail.email_to, self.email_template.email_to)
        self.assertEqual(mail.email_cc, self.email_template.email_cc)
        self.assertEqual(mail.recipient_ids, self.partner_2 | self.user_employee.partner_id)

        # sending from frontend
        self.switch_user_website()
        mail_id = self.email_template.send_mail(self.test_pigs.id)
        mail = self.env['mail.mail'].browse(mail_id)
        self.assertEqual(mail.subject, self.website.name)

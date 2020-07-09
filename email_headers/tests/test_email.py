# No need to translate tests
# pylint: disable=translation-required
from email.message import EmailMessage

import mock

import odoo
from odoo import SUPERUSER_ID
from odoo.tests import TransactionCase

from odoo.addons.base.models.ir_mail_server import IrMailServer

from ..models.mail import (
    MESSAGE_PREFIX,
    encode_msg_id,
    encode_msg_id_legacy,
    random_string,
)


@odoo.tests.tagged("post_install", "-at_install")
class TestEmail(TransactionCase):
    def setUp(self):
        super(TestEmail, self).setUp()

        self.partner = self.env["res.partner"].create({"name": "Test Dude"})
        self.partner2 = self.env["res.partner"].create({"name": "Dudette"})
        self.demo_user = self.env.ref("base.user_demo")
        self.subtype_comment = self.env.ref("mail.mt_comment")
        self.subtype_note = self.env.ref("mail.mt_note")

        self.MailMessage = self.env["mail.message"]
        self.ConfigParam = self.env["ir.config_parameter"]

        # Create server configuration
        self.outgoing_server = self.env["ir.mail_server"].create(
            {
                "name": "Outgoing SMTP Server for Unit Tests",
                "sequence": 1,
                "smtp_host": "localhost",
                "smtp_port": "9999",
                "smtp_encryption": "none",
                "smtp_user": "doesnt",
                "smtp_pass": "exist",
                "reply_to_method": "msg_id",
                "force_email_reply_to_domain": "example.com",
                "force_email_from": "odoo@example.com",
            }
        )

    @staticmethod
    def create_email_message():
        message = EmailMessage()
        message[
            "Content-Type"
        ] = 'multipart/mixed; boundary="===============2590914155756834027=="'
        message["MIME-Version"] = "1.0"
        message[
            "Message-Id"
        ] = "<CAD-eYi=a264_3DcrYSDU5yc_fwYoHonZ3H+{}@mail.gmail.com>".format(
            random_string(6)
        )
        message["Subject"] = "1"
        message["From"] = "Miku Laitinen <miku@avoin.systems>"
        message["Reply-To"] = "YourCompany Eurooppa <sales@avoin.onmicrosoft.com>"
        message["To"] = '"Erik N. French" <ErikNFrench@armyspy.com>'
        message["Date"] = "Mon, 06 May 2019 14:16:38 -0000"
        return message

    def test_reply_to_method_msg_id(self):

        # Make administrator follow the partner
        self.partner.message_subscribe([self.env.user.partner_id.id])

        # Send a message to the followers of the partner
        thread_msg = self.partner.with_user(self.demo_user).message_post(
            body="dummy message.", message_type="comment", subtype="mail.mt_comment"
        )

        # Make sure the message headers look right.. or not
        # mail_msg = thread_msg.notification_ids[0]

        # Get the encoded message address
        encoded_msg_id = encode_msg_id(thread_msg.id, self.env)

        # Try to read an incoming email
        message = self.create_email_message()
        del message["To"]
        message["To"] = '"Erik N. French" <ErikNFrench+{}{}@armyspy.com>'.format(
            MESSAGE_PREFIX, encoded_msg_id
        )

        thread_id = self.env["mail.thread"].message_process(
            model=False, message=message.as_string()
        )
        self.assertEqual(
            thread_msg.res_id,
            thread_id,
            "The incoming email wasn't connected to the correct thread",
        )

        # Make sure the message is a comment
        incoming_msg1 = self.MailMessage.search(
            [("message_id", "=", message["Message-Id"])]
        )
        self.assertEqual(
            incoming_msg1.message_type,
            "email",
            "The incoming message was created as a type {} instead of a email.".format(
                incoming_msg1.message_type
            ),
        )
        self.assertEqual(
            incoming_msg1.subtype_id,
            self.subtype_comment,
            "The incoming message was created as a subtype {} instead of a comment.".format(
                incoming_msg1.subtype_id
            ),
        )

        # Try to read another incoming email
        message = self.create_email_message()
        del message["To"]
        message["To"] = '"Erik N. French" <ErikNFrench+{}HURDURLUR@armyspy.com>'.format(
            MESSAGE_PREFIX
        )
        message["In-Reply-To"] = thread_msg.message_id

        thread_id = self.env["mail.thread"].message_process(
            model=False, message=message.as_string()
        )
        self.assertEqual(
            thread_msg.res_id,
            thread_id,
            "The incoming email wasn't connected to the correct thread",
        )

        # Make sure the message is a comment
        incoming_msg2 = self.MailMessage.search(
            [("message_id", "=", message["Message-Id"])]
        )
        self.assertEqual(
            incoming_msg2.message_type,
            "email",
            "The incoming message was created as a type {} instead of a email.".format(
                incoming_msg2.message_type
            ),
        )
        self.assertEqual(
            incoming_msg2.subtype_id,
            self.subtype_comment,
            "The incoming message was created as a subtype {} instead of a comment.".format(
                incoming_msg2.subtype_id
            ),
        )

    def test_reply_to_method_msg_id_priority(self):
        """
        In this test we will inject the wrong Message-Id to the incoming
        email messages References-header and see if Odoo will prioritize
        the custom Reply-To address over the References-header. It should.
        :return:
        """

        # Make administrator follow the partner
        self.partner.message_subscribe([self.env.user.partner_id.id])

        # Send a message to the followers of the partner
        thread_msg = self.partner.with_user(self.demo_user).message_post(
            body="dummy message X.", message_type="comment", subtype="mail.mt_comment"
        )

        # Get the encoded message address
        encoded_msg_id = encode_msg_id(thread_msg.id, self.env)

        # Send another message to the followers of the partner
        thread_msg2 = self.partner2.with_user(self.demo_user).message_post(
            body="dummy message X.", message_type="comment", subtype="mail.mt_comment"
        )

        # Try to read an incoming email
        message = self.create_email_message()
        del message["To"]
        del message["References"]
        message["To"] = '"Erik N. French" <ErikNFrench+{}{}@armyspy.com>'.format(
            MESSAGE_PREFIX, encoded_msg_id
        )

        # Inject the wrong References
        message["References"] = thread_msg2.message_id

        thread_id = self.env["mail.thread"].message_process(
            model=False, message=message.as_string()
        )
        self.assertEqual(
            thread_msg.res_id,
            thread_id,
            "The incoming email wasn't connected to the correct thread",
        )

    def test_reply_to_method_msg_id_notification(self):

        # Make administrator follow the partner
        self.partner2.message_subscribe([self.env.user.partner_id.id])

        # Send a message to the followers of the partner
        thread_msg = self.partner2.with_user(self.demo_user).message_post(
            body="dummy message 2.", message_type="comment", subtype="mail.mt_note"
        )

        # Get the encoded message address
        encoded_msg_id = encode_msg_id(thread_msg.id, self.env)

        # Try to read an incoming email
        message = self.create_email_message()
        del message["To"]
        message["To"] = '"Erik N. French" <ErikNFrench+{}{}@armyspy.com>'.format(
            MESSAGE_PREFIX, encoded_msg_id
        )

        thread_id = self.env["mail.thread"].message_process(
            model=False, message=message.as_string()
        )
        self.assertEqual(
            thread_msg.res_id,
            thread_id,
            "The incoming email wasn't connected to the correct thread",
        )

        # Make sure the message is a note
        incoming_msg1 = self.MailMessage.search(
            [("message_id", "=", message["Message-Id"])]
        )
        self.assertEqual(
            incoming_msg1.message_type,
            "email",
            "The incoming message was created as a type {} instead of a email.".format(
                incoming_msg1.message_type
            ),
        )
        self.assertEqual(
            incoming_msg1.subtype_id,
            self.subtype_note,
            "The incoming message was created as a subtype {} instead of a note.".format(
                incoming_msg1.subtype_id
            ),
        )

    def test_reply_to_method_msg_id_legacy(self):
        # REMOVE this test when porting to Odoo 14

        # Make administrator follow the partner
        self.partner2.message_subscribe([self.env.user.partner_id.id])

        # Send a message to the followers of the partner
        thread_msg = self.partner2.with_user(self.demo_user).message_post(
            body="dummy message 2.", message_type="comment", subtype="mail.mt_note"
        )

        # Get the encoded message address
        encoded_msg_id = encode_msg_id_legacy(thread_msg.id, self.env)

        # Try to read an incoming email
        message = self.create_email_message()
        del message["To"]
        message["To"] = '"Erik N. French" <ErikNFrench+{}{}@armyspy.com>'.format(
            MESSAGE_PREFIX, encoded_msg_id
        )

        thread_id = self.env["mail.thread"].message_process(
            model=False, message=message.as_string()
        )
        self.assertEqual(
            thread_msg.res_id,
            thread_id,
            "The incoming email wasn't connected to the correct thread",
        )

    def test_reply_to_method_msg_id_lowercase(self):
        # Make administrator follow the partner
        self.partner2.message_subscribe([self.env.user.partner_id.id])

        # Send a message to the followers of the partner
        thread_msg = self.partner2.with_user(self.demo_user).message_post(
            body="dummy message 2.", message_type="comment", subtype="mail.mt_note"
        )

        # Get the encoded message address
        encoded_msg_id = encode_msg_id(thread_msg.id, self.env).lower()

        # Try to read an incoming email
        message = self.create_email_message()
        del message["To"]
        message["To"] = '"Erik N. French" <ErikNFrench+{}{}@armyspy.com>'.format(
            MESSAGE_PREFIX, encoded_msg_id
        )

        thread_id = self.env["mail.thread"].message_process(
            model=False, message=message.as_string()
        )
        self.assertEqual(
            thread_msg.res_id,
            thread_id,
            "The incoming email wasn't connected to the correct thread",
        )

    def test_outgoing_msg_id(self):
        # Make administrator follow the partner
        self.partner2.message_subscribe([SUPERUSER_ID])

        with mock.patch.object(IrMailServer, "send_email") as send_email:
            # Send a message to the followers of the partner
            thread_msg = self.partner2.with_user(self.demo_user).message_post(
                body="dummy message 3.",
                message_type="comment",
                subtype="mail.mt_comment",
            )

            # Get the encoded message address
            encoded_msg_id = encode_msg_id(thread_msg.id, self.env)

            self.assertTrue(
                send_email.called,
                "IrMailServer.send_email wasn't called when sending outgoing email",
            )

            message = send_email.call_args[0][0]

            reply_to_address = "{}{}@{}".format(
                MESSAGE_PREFIX,
                encoded_msg_id,
                self.outgoing_server.force_email_reply_to_domain,
            )

            # Make sure the subaddress is correct in the Reply-To field
            self.assertIn(
                reply_to_address,
                message["Reply-To"],
                "Reply-To address didn't contain the correct subaddress",
            )

            # Make sure the author name is in the Reply-To field
            self.assertIn(
                thread_msg.author_id.name,
                message["Reply-To"],
                "Reply-To address didn't contain the author name",
            )

            self.assertIn(
                self.outgoing_server.force_email_from,
                message["From"],
                "From address didn't contain the configure From-address",
            )

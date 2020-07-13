##############################################################################
#
#    Author: Avoin.Systems
#    Copyright 2018 Avoin.Systems
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import base64
import binascii
import logging
import random
import re
import string
from email.message import Message
from email.utils import formataddr, parseaddr

from Crypto.Cipher import AES

from odoo import api, fields, models, tools
from odoo.tools import frozendict

from odoo.addons.base.models.ir_mail_server import encode_rfc2822_address_header

_logger = logging.getLogger(__name__)


MESSAGE_PREFIX = "msg-"


def random_string(length):
    return "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(length)
    )


def get_key(env):
    return env["ir.config_parameter"].get_param("database.secret", "noneedtobestrong")[
        :16
    ]


def get_cipher(env):
    return AES.new(
        get_key(env).encode("utf-8"), mode=AES.MODE_CBC, iv=b"veryverysecret81"
    )


def encode_msg_id(msg_id, env):
    id_padded = "%016d" % msg_id
    encrypted = get_cipher(env).encrypt(id_padded.encode("utf-8"))
    return base64.b32encode(encrypted).decode("utf-8")


# Remove in Odoo 14
def encode_msg_id_legacy(msg_id, env):
    id_padded = "%016d" % msg_id
    encrypted = get_cipher(env).encrypt(id_padded.encode("utf-8"))
    return base64.urlsafe_b64encode(encrypted).decode("utf-8")


def decode_msg_id(encoded_encrypted_id, env):

    try:
        # Some email clients don't respect the original Reply-To address case
        # and might make them lowercase. Make the encoded ID uppercase.
        encrypted = base64.b32decode(encoded_encrypted_id.encode("utf-8").upper())
    except binascii.Error:
        # Fall back to base64, which was used by the previous versions.
        # This can be removed in Odoo 14.
        try:
            encrypted = base64.urlsafe_b64decode(encoded_encrypted_id.encode("utf-8"))
        except binascii.Error:
            _logger.error(
                "Unable to decode the message ID. The input value "
                "is invalid and cannot be decoded. "
                "Encoded value: {}".format(encoded_encrypted_id)
            )
            raise

    try:
        id_str = get_cipher(env).decrypt(encrypted).decode("utf-8")
    except UnicodeDecodeError:
        _logger.error(
            "Unable to decrypt the message ID. The input value "
            "probably wasn't encrypted with the same key. Encoded "
            "value: {}".format(encoded_encrypted_id)
        )
        raise

    return int(id_str)


class MailServer(models.Model):
    _inherit = "ir.mail_server"

    reply_to_method = fields.Selection(
        [("default", "Odoo Default"), ("alias", "Alias"), ("msg_id", "Message ID")],
        "Reply-To Method",
        default="default",
        help="Odoo Default: Don't add any unique identifiers into the\n"
        "Reply-To address.\n"
        "\n"
        "Alias: Find or generate an email alias for the Reply-To field of\n "
        "every outgoing message so the responses will be automatically \n"
        "routed to the correct thread even if the email client (Yes, \n"
        "I'm looking at you, Microsoft Outlook) decides to drop the \n"
        "References, In-Reply-To and Message-ID fields.\n\n"
        "The alias will then be used to generate a RFC 5233 sub-address\n"
        "using the Force From Address field as a base, eg.\n"
        "odoo@mycompany.fi would become odoo+adf9bacd98732@mycompany.fi\n"
        "\n"
        "Note that this method has a flaw: if the headers have dropped\n"
        "and Odoo can't connect the reply to any message in the thread,\n"
        "it will automatically connect it to the first message in the \n"
        "thread which often is an internal note and the reply will also\n"
        "be marked as an internal note even when it should be a comment."
        "\n\n"
        "Message ID: Include a prefix and the message ID in encrypted\n"
        "and base32 encoded format in the Reply-To\n"
        "address to that Odoo will be able to directly connect the\n"
        "reply to the original message. Note that in this mode the\n"
        "Reply-To address has a priority over References and\n"
        "In-Reply-To headers.",
    )

    force_email_reply_to = fields.Char("Force Reply-To Address",)

    force_email_reply_to_name = fields.Char("Force Reply-To Name",)

    force_email_reply_to_domain = fields.Char("Force Reply-To Domain",)

    force_email_from = fields.Char("Force From Address",)

    force_email_sender = fields.Char("Force Sender Address",)

    prioritize_reply_to_over_msgid = fields.Boolean(
        "Prioritize Reply-To Over Email Headers",
        default=True,
        help="If this field is selected, the unique Reply-To address "
        "generated by the Message ID method will be prioritized "
        "over the email headers (default Odoo behavior) in incoming "
        "emails. This is recommended when the Reply-To method is set to "
        "Message ID.",
    )

    headers_example = fields.Text(
        "Example Headers", compute="_compute_headers_example", store=False,
    )

    # TODO Implement field input validators
    def _get_reply_to_address(self, alias, original_from_name):
        self.ensure_one()

        force_email_from = encode_rfc2822_address_header(self.force_email_from)

        # Split the From address
        from_address = force_email_from.split("@")

        reply_to_addr = "{alias}@{domain}".format(
            alias=alias if alias else from_address[0],
            domain=self.force_email_reply_to_domain or from_address[1],
        )

        if self.force_email_reply_to_name:
            reply_to = formataddr((self.force_email_reply_to_name, reply_to_addr))
        elif original_from_name:
            reply_to = formataddr((original_from_name, reply_to_addr))
        else:
            reply_to = reply_to_addr

        return encode_rfc2822_address_header(reply_to)

    @api.depends(
        "force_email_sender",
        "force_email_reply_to",
        "force_email_reply_to_domain",
        "force_email_from",
        "force_email_reply_to_name",
        "reply_to_method",
    )
    def _compute_headers_example(self):
        for server in self:
            example = []
            if server.force_email_sender:
                example.append("Sender: {}".format(server.force_email_sender))

            if server.force_email_reply_to:
                example.append("Reply-To: {}".format(server.force_email_reply_to))
            elif server.force_email_from and server.reply_to_method != "default":
                reply_to_pair = server.force_email_from.split("@")

                if server.reply_to_method == "alias":
                    token = "{}+1d278g1082bca"
                elif server.reply_to_method == "msg_id":
                    token = "{}+" + MESSAGE_PREFIX + "p2IxKkfEKugl16juheTT0g=="
                else:
                    token = "INVALID"
                    _logger.error(
                        "Invalid reply_to_method found: " + server.reply_to_method
                    )

                # noinspection PyProtectedMember
                reply_to = server._get_reply_to_address(
                    token.format(reply_to_pair[0]), "Original From Person"
                )
                example.append("Reply-To: {}".format(reply_to))
            else:
                example.append("Reply-To: Odoo default")

            if server.force_email_from:
                example.append(
                    "From: {}".format(
                        formataddr(("Original From Person", server.force_email_from))
                    )
                )
            else:
                example.append("From: Odoo default")

            server.headers_example = "\n".join(example)

    @api.model
    def send_email(
        self,
        message,
        mail_server_id=None,
        smtp_server=None,
        smtp_port=None,
        smtp_user=None,
        smtp_password=None,
        smtp_encryption=None,
        smtp_debug=False,
        smtp_session=None,
    ):

        # Get SMTP Server Details from Mail Server
        mail_server = None
        if mail_server_id:
            mail_server = self.sudo().browse(mail_server_id)
        elif not smtp_server:
            mail_server = self.sudo().search([], order="sequence", limit=1)

        # Note that Odoo already has the ability to use a fixed From address
        # by settings "email_from" in the Odoo settings. This is however a
        # secondary option and here email_from always overrides that.
        if mail_server.force_email_from:
            original_from_name = parseaddr(message["From"])[0]
            force_email_from = encode_rfc2822_address_header(
                mail_server.force_email_from
            )
            del message["From"]
            message["From"] = formataddr((original_from_name, force_email_from))

            if mail_server.reply_to_method == "alias":
                # Find or create an email alias
                alias = self.find_or_create_alias(force_email_from.split("@"))
                # noinspection PyProtectedMember
                reply_to = mail_server._get_reply_to_address(alias, original_from_name,)
                del message["Reply-To"]
                message["Reply-To"] = reply_to

            elif mail_server.reply_to_method == "msg_id":
                odoo_msg_id = message.get("Message-Id")
                if odoo_msg_id:
                    # The message_id isn't unique. Prefer the one that has a
                    # model set and only pick the first record. Odoo does
                    # almost the same thing in mail.thread.message_route().
                    odoo_msg = (
                        self.sudo()
                        .env["mail.message"]
                        .search(
                            [("message_id", "=", odoo_msg_id)], order="model", limit=1
                        )
                    )

                    encrypted_id = encode_msg_id(odoo_msg.id, self.env)
                    # noinspection PyProtectedMember
                    reply_to = mail_server._get_reply_to_address(
                        "{}+{}{}".format(
                            force_email_from.split("@")[0], MESSAGE_PREFIX, encrypted_id
                        ),
                        original_from_name,
                    )

                    _logger.info(
                        'Generated a new reply-to address "{}" for '
                        'Message-Id "{}".'.format(reply_to, odoo_msg_id)
                    )

                    del message["Reply-To"]
                    message["Reply-To"] = reply_to
                else:
                    _logger.warning(
                        "Couldn't get Message-Id from the message {}. The "
                        "reply might not find its way to the correct thread.".format(
                            message.as_string()
                        )
                    )

        if mail_server.force_email_reply_to:
            del message["Reply-To"]
            message["Reply-To"] = encode_rfc2822_address_header(
                mail_server.force_email_reply_to
            )

        if mail_server.force_email_sender:
            del message["Sender"]
            message["Sender"] = encode_rfc2822_address_header(
                mail_server.force_email_sender
            )

        return super(MailServer, self).send_email(
            message,
            mail_server_id,
            smtp_server,
            smtp_port,
            smtp_user,
            smtp_password,
            smtp_encryption,
            smtp_debug,
            smtp_session,
        )

    def find_or_create_alias(self, from_address):

        record_id, record_model_name = self.resolve_record()
        if not record_id or not record_model_name:
            # Can't create an alias if we don't know the related record
            return False

        if record_model_name not in self.env:
            _logger.error(
                "Unable to find or create an alias for outgoing "
                "email: invalid_model name {}.".format(record_model_name)
            )
            return False

        # Find an alias
        alias_model_id = (
            self.env["ir.model"].search([("model", "=", record_model_name)]).id
        )
        # noinspection PyPep8Naming
        Alias = self.env["mail.alias"]
        existing_aliases = Alias.search(
            [
                ("alias_model_id", "=", alias_model_id),
                (
                    "alias_name",
                    "like",
                    "{from_address}+".format(from_address=from_address[0]),
                ),
                ("alias_force_thread_id", "=", record_id),
                ("alias_contact", "=", "everyone"),  # TODO: check from record
            ]
        )

        if existing_aliases:
            return existing_aliases[0].alias_name

        # Create a new alias
        alias = Alias.create(
            {
                "alias_model_id": alias_model_id,
                "alias_name": "{from_address}+{random_string}".format(
                    from_address=from_address[0], random_string=random_string(8)
                ),
                "alias_force_thread_id": record_id,
                "alias_contact": "everyone",
            }
        )

        return alias.alias_name

    def resolve_record(self):
        ctx = self.env.context
        # Don't ever use active_id or active_model from the context here.
        # It might not be the one that you expect. Go ahead and try, open
        # a sales order, go to the related purchase order and send the PO.
        record_id = ctx.get("default_res_id")
        record_model_name = ctx.get("default_model")

        # If incoming_routes isn't enough, we can use ctx['incoming_to'] to
        # find a alias directly without active_id and active_model_name.
        routes = ctx.get("incoming_routes", [])
        if (not record_id or not record_model_name) and routes and len(routes) > 0:
            route = routes[0]
            record_model_name = route[0]
            record_id = route[1]

        return record_id, record_model_name

    @api.model
    def encrypt_message_id(self, message_id):
        """
        A helper encryption method for debugging mail delivery issues.
        :param message_id: The id of the `mail.message`
        :return: The id of the `mail.message` encrypted and base64 encoded
        """
        return encode_msg_id(message_id, self.env)

    @api.model
    def decrypt_message_id(self, encrypted_id):
        """
        A helper decryption method for debugging mail delivery issues.
        :param encrypted_id: The encrypted and base64 encoded id of
                             the `mail.message` to be decrypted
        :return: The id of the `mail.message`
        """
        return decode_msg_id(encrypted_id, self.env)


class MailThread(models.AbstractModel):

    _inherit = "mail.thread"

    """
    The process for incoming emails goes something like this:
    1. message_process (processing the incoming message)
        2. message_parse (parsing the email message)
        3. message_route (decides how to route the email)
        4. message_route_process (executes the route)
            5. message_post (posts the message to a thread)
    """

    @api.model
    def message_parse(self, message, save_original=False):
        email_to = tools.decode_message_header(message, "To")
        email_to_localpart = (tools.email_split(email_to) or [""])[0].split("@", 1)[0]

        config_params = self.env["ir.config_parameter"].sudo()

        # Check if the To part contains the prefix and a base32/64 encoded string
        # Remove the "24," part when migrating to Odoo 14.
        prefix_in_to = email_to_localpart and re.search(
            r".*" + MESSAGE_PREFIX + "(?P<odoo_id>.{24,32}$)", email_to_localpart
        )

        prioritize_replyto_over_headers = config_params.get_param(
            "email_headers.prioritize_replyto_over_headers", "True"
        )
        prioritize_replyto_over_headers = (
            True if prioritize_replyto_over_headers != "False" else False
        )

        # If the msg prefix part is found in the To part, find the parent
        # message and inject the Message-Id to the In-Reply-To part and
        # remove References because it by default takes priority over
        # In-Reply-To. We want the unique Reply-To address have the priority.
        if prefix_in_to and prioritize_replyto_over_headers:
            message_id_encrypted = prefix_in_to.group("odoo_id")
            try:
                message_id = decode_msg_id(message_id_encrypted, self.env)
                parent_id = self.env["mail.message"].browse(message_id)
                if parent_id:
                    # See unit test test_reply_to_method_msg_id_priority
                    del message["References"]
                    del message["In-Reply-To"]
                    message["In-Reply-To"] = parent_id.message_id
                else:
                    _logger.warning(
                        "Received an invalid mail.message database id in incoming "
                        "email sent to {}. The email type (comment, note) might "
                        "be wrong.".format(email_to)
                    )
            except UnicodeDecodeError:
                _logger.warning(
                    "Unique Reply-To address of an incoming email couldn't be "
                    "decrypted. Falling back to default Odoo behavior."
                )

        res = super(MailThread, self).message_parse(message, save_original)

        strip_message_id = config_params.get_param(
            "email_headers.strip_mail_message_ids", "True"
        )
        strip_message_id = True if strip_message_id != "False" else False

        if not strip_message_id == "True":
            return res

        # When Odoo compares message_id to the one stored in the database when determining
        #  whether or not the incoming message is a reply to another one, the message_id search
        #  parameter is stripped before the search. But Odoo does not do anything of the sort when
        #  a message is created, meaning if some email software (for example Outlook,
        #  for no particular reason) includes anything strippable at the start of the Message-Id,
        #  any replies to that message in the future will not find their way correctly, as the
        #  search yields nothing.
        #
        # Example of what happened before. The first one is the original Message-Id, and thus also
        #  the ID that gets stored on the mail.message as the `message_id`
        #   '\r\n <AM6PR05MB4933DE6BCAD68A037185EBCFFBAF0@AM6PR05MB4933.eurprd05.prod.outlook.com>'
        #  But when trying to find this message, Odoo takes the above message_id and strips it,
        #  which results in:
        #   '<AM6PR05MB4933DE6BCAD68A037185EBCFFBAF0@AM6PR05MB4933.eurprd05.prod.outlook.com>'
        #  And then the search is done for an exact match, which will fail.
        #
        # Odoo doesn't, so we must strip the message_ids before they are stored in the database
        mail_message_id = res.get("message_id", "")
        if mail_message_id:
            mail_message_id = mail_message_id.strip()
            res["message_id"] = mail_message_id
        return res

    @api.model
    def message_route_process(self, message, message_dict, routes):
        ctx = self.env.context.copy()
        ctx["incoming_routes"] = routes
        ctx["incoming_to"] = message_dict.get("to")
        self.env.context = frozendict(ctx)
        return super(MailThread, self).message_route_process(
            message, message_dict, routes
        )

    @api.model
    def message_route(
        self, message, message_dict, model=None, thread_id=None, custom_values=None
    ):

        # NOTE! If you're going to backport this module to Odoo 11 or Odoo 10,
        # you will have to create the mail_bounce_catchall email template
        # because it was introduced only in Odoo 12.

        if not isinstance(message, Message):
            raise TypeError("message must be an " "email.message.Message at this point")

        try:
            route = super(MailThread, self).message_route(
                message, message_dict, model, thread_id, custom_values
            )
        except ValueError:

            # If the headers that connect the incoming message to a thread in
            # Odoo have disappeared at some point and the message was sent to
            # the catchall address (with a sub-addressing suffix), we will
            # skip the default catchall check and perform it here for
            # mail.catchall.alias.custom. We do this because the alias check
            # if done AFTER the catchall check by default and it may cause
            # Odoo to send a bounce message to the sender who sent the email to
            # the correct thread-specific address.

            catchall_alias = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("mail.catchall.alias.custom")
            )

            email_to = tools.decode_message_header(message, "To")
            email_to_localpart = (
                (tools.email_split(email_to) or [""])[0].split("@", 1)[0].lower()
            )

            message_id = message.get("Message-Id")
            email_from = tools.decode_message_header(message, "From")

            # check it does not directly contact catchall
            if catchall_alias and catchall_alias in email_to_localpart:
                _logger.info(
                    "Routing mail from %s to %s with Message-Id %s: "
                    "direct write to catchall, bounce",
                    email_from,
                    email_to,
                    message_id,
                )
                body = self.env.ref("mail.mail_bounce_catchall").render(
                    {"message": message}, engine="ir.qweb"
                )
                self._routing_create_bounce_email(
                    email_from, body, message, reply_to=self.env.user.company_id.email
                )
                return []
            else:
                raise

        return route

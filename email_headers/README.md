# Robust Mails

This module is used to improve email deliverability and make sure that replies find
their way to the correct thread in Odoo.

Options:

- Force the `From` and `Reply-To` addresses of outgoing email
- Generate a thread-specific `Reply-To` address for outgoing emails so that losing the
  headers used to identify the correct thread won't be a problem any more.

## Gotcha

To make the automatic bounce message work when using thread-specific `Reply-To`
addresses, you should define the actual catchall alias in a system parameter called
`mail.catchall.alias.custom` and change the `mail.catchall.alias` to something
completely random that will never be used, or alternatively remove it.

The reason is this: when Odoo is looking for a route for an incoming email that has lost
its headers, it won't check whether the email was sent to `catchall@whatever.com` but
instead it will see if the local part of that address contains the word `catchall`. And
this isn't a good thing when the address is something like
`catchall+123abc@whatever.com`. That's why we had to skip the default catchall
evaluation and redo it in a later phase.

## Database-specific Settings

| Setting                                       | Purpose                                                                                                                                                | Default value             |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------- |
| email_headers.strip_mail_message_ids          | Office 365 emails may add whitespaces before the Message-Id's. This feature removes them.                                                              | "True"                    |
| email_headers.prioritize_replyto_over_headers | When "True", Odoo will prioritize the (unique) Reply-To address of an incoming email and only then look at the `References` and `In-Reply-To` headers. | "True"                    |
| mail.catchall.alias                           | The default catchall alias. See "Gotcha" for more information.                                                                                         | "catchall"                |
| mail.catchall.alias.custom                    | The new catchall alias setting. See "Gotcha" for more information. Will be set automatically upon module installation.                                 | mail.catchall.alias value |

## Debugging

### Decode and decrypt a message id

```python
from odoo.addons.email_headers.models.mail import decode_msg_id
decode_msg_id(<encrypted and base32/64 encoded message database id>, self.env)
```

### Encrypt and encode a message id

```python
from odoo.addons.email_headers.models.mail import encode_msg_id
encode_msg_id(<message database id>, self.env)
```

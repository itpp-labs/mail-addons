# -*- coding: utf-8 -*-
{
    "name": """Popup Attachments""",
    "summary": """Open attached mail images in popup""",
    "category": "Extra Tools",
    "version": "1.0.0",
    "images": ['images/popup_image.png'],

    "author": "IT-Projects LLC, Dinar Gabbasov",
    "support": "apps@it-projects.info",
    'website': "https://twitter.com/gabbasov_dinar",
    "license": "GPL-3",
    "price": "50.0",
    "currency": "EUR",

    "depends": [
        "mail",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/mail_attachment_popup_template.xml",
    ],
    "qweb": [
        "static/src/xml/mail_attachment_popup.xml",
    ],

    "installable": True,
    'auto_install': False,
}

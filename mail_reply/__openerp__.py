# -*- coding: utf-8 -*-
{
    "name": """Show reply button""",
    "summary": """Got a message out of a Form? Now you can reply to it too!""",
    "category": "Discuss",
    "images": [],
    "version": "1.0.0",

    "author": "IT-Projects LLC, Pavel Romanchenko",
    "website": "https://it-projects.info",
    "license": "LGPL-3",
    #"price": 9.00,
    #"currency": "EUR",

    "depends": [
        "mail_base",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'templates.xml'
    ],
    "qweb": [
        "static/src/xml/reply_button.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}

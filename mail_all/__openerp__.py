# -*- coding: utf-8 -*-
{
    "name": "Show all messages",
    "summary": """Checkout all messages where you have access""",
    "category": "Discuss",
    "images": ['images/1.jpg'],
    "version": "1.0.0",

    "author": "IT-Projects LLC, Pavel Romanchenko",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info",
    "license": "LGPL-3",
    'price': 40.00,
    'currency': 'EUR',

    "depends": [
        "mail_base"
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/templates.xml",
    ],
    "qweb": [
        "static/src/xml/menu.xml",
    ],
    "demo": [],
    'installable': True,
    "auto_install": False,
}

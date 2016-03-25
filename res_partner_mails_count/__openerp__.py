# -*- coding: utf-8 -*-
{
    "name": """Partner mails count""",
    "summary": """Displays mails amount from and to customers.""",
    "category": "Sales Management",
    "images": ['images/1.png'],
    "version": "1.0.0",

    "author": "IT-Projects LLC",
    "website": "https://it-projects.info",
    "license": "GPL-3",
    "price": 10.00,
    "currency": "EUR",

    "depends": [
        'base',
        'mail' ,
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'views/res_partner_mails_count.xml',
        'templates.xml',
    ],
    "demo": [
    ],
    "installable": True,
    "auto_install": False,
}
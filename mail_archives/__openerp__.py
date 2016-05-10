# -*- coding: utf-8 -*-
{
    "name": "Mail archives",
    "summary": """Adds menu to find old messages""",
    "category": "Discuss",
    "images": ['images/1.jpg'],
    "version": "1.0.0",

    "author": "IT-Projects LLC, Pavel Romanchenko",
    "website": "https://it-projects.info",
    "license": "LGPL-3",
    'price': 40.00,
    'currency': 'EUR',

    "depends": [
        "mail_base",
    ],

    "data": [
        "views/templates.xml",
    ],
    "qweb": [
        "static/src/xml/menu.xml",
    ],
    'installable': True,
}

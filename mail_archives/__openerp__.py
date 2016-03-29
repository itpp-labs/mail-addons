# -*- coding: utf-8 -*-
{
    "name": "mail_archives",
    "summary": """Create archive channel""",
    "category": "Uncategorized",
    "images": [],
    "version": "1.0.0",

    "author": "IT-Projects LLC, Pavel Romanchenko",
    "website": "http://www.it-projects.info",
    "license": "LGPL-3",

    "depends": [
        "base",
        "mail"
    ],

    "data": [
        "views/views.xml",
        "views/templates.xml",
    ],
    "qweb": [
        "static/src/xml/menu.xml",
    ],
    'installable': True,
}

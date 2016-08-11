# -*- coding: utf-8 -*-
{
    "name": """Internal Messaging""",
    "summary": """Allows you to send private messages to specified recipients only no matter who are in followers list.""",
    "category": "Social Network",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Pavel Romanchenko",
    "website": "https://it-projects.info",
    "license": "GPL-3",
    #"price": 9.00,
    #"currency": "EUR",

    "depends": [
        "mail",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'template.xml',
        'view.xml',
    ],
    "qweb": [
        'static/src/xml/mail_private.xml',
    ],
    "demo": [],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}

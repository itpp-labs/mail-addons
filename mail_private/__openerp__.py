# -*- coding: utf-8 -*-
# Copyright 2016 x620 <https://github.com/x620>
# Copyright 2016 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2016 Ilmir Karamov <https://it-projects.info/team/ilmir-k>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl.html).
{
    "name": """Internal Messaging""",
    "summary": """Send private messages to specified recipients, regardless of who are in followers list.""",
    "category": "Discuss",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=8.0",
    "images": [],
    "version": "8.0.1.1.1",
    "application": False,

    "author": "IT-Projects LLC, Pavel Romanchenko",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/",
    "license": "LGPL-3",
    "price": 50.00,
    "currency": "EUR",

    "depends": [
        "mail"
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'template.xml',
    ],
    "demo": [
    ],
    "qweb": [
        'static/src/xml/mail_private.xml',
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,

    # "demo_title": "{MODULE_NAME}",
    # "demo_addons": [
    # ],
    # "demo_addons_hidden": [
    # ],
    # "demo_url": "DEMO-URL",
    # "demo_summary": "{SHORT_DESCRIPTION_OF_THE_MODULE}",
    # "demo_images": [
    #    "images/MAIN_IMAGE",
    # ]
}

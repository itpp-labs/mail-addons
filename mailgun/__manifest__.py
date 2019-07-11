# Copyright 2018 Ildar Nasyrov <https://it-projects.info/team/iledarn>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": """Mailgun""",
    "summary": """Setup the outgoing and incoming mail flow easily by using Mailgun""",
    "category": "Discuss",
    # "live_test_url": "http://apps.it-projects.info/shop/product/mailgun?version=11.0",
    "images": ["images/mailgun_main.png"],
    "version": "11.0.1.1.0",
    "application": False,

    "author": "IT-Projects LLC, Ildar Nasyrov",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/iledarn",
    "license": "LGPL-3",
    "price": 389.00,
    "currency": "EUR",

    "depends": [
        "mail",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'data/ir_cron_data.xml',
    ],
    "demo": [
    ],
    "qweb": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,

    "demo_title": "Mailgun",
    "demo_addons": [],
    "demo_addons_hidden": [],
    "demo_url": "mailgun",
    "demo_summary": "Easy to send outgoing and fetch incoming messages by using Mailgun",
    "demo_images": [
        "images/mailgun_main.png",
    ]
}

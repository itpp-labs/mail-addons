# Copyright 2016-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2017-2018 Artyom Losev <https://it-projects.info/team/ArtyomLosev>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).
{
    "name": "Show all messages",
    "summary": """Checkout all messages where you have access""",
    "category": "Discuss",
    # "live_test_url": "",
    "images": ["images/1.jpg"],
    "version": "12.0.1.0.1",
    "application": False,
    "author": "IT-Projects LLC, Pavel Romanchenko",
    "support": "apps@itpp.dev",
    "website": "https://it-projects.info",
    "license": "Other OSI approved licence",  # MIT
    "price": 40.00,
    "currency": "EUR",
    "depends": ["mail"],
    "external_dependencies": {"python": [], "bin": []},
    "data": ["views/templates.xml"],
    "qweb": ["static/src/xml/menu.xml"],
    "demo": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,
    "installable": True,
    "auto_install": False,
}

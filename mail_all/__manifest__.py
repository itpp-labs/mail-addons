# Copyright 2020 Denis Mudarisov <https://github.com/trojikman>
# License MIT (https://opensource.org/licenses/MIT).
{
    "name": "Show all messages",
    "summary": """Checkout all messages where you have access""",
    "category": "Discuss",
    # "live_test_url": "",
    "images": ["images/1.jpg"],
    "version": "11.0.1.0.1",
    "application": False,
    "author": "IT-Projects LLC, Pavel Romanchenko",
    "support": "apps@itpp.dev",
    "website": "https://twitter.com/OdooFree",
    "license": "Other OSI approved licence",  # MIT
    "price": 40.00,
    "currency": "EUR",
    "depends": ["mail_base"],
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

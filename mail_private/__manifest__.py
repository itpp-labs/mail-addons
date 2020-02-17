# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License MIT (https://opensource.org/licenses/MIT).
{
    "name": """Internal Messaging""",
    "summary": """Send private messages to specified recipients, regardless of who are in followers list.""",
    "category": "Discuss",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=12.0",
    "images": ["images/mail_private_image.png"],
    "version": "12.0.1.1.2",
    "application": False,
    "author": "IT-Projects LLC, Pavel Romanchenko",
    "support": "apps@itpp.dev",
    "website": "https://it-projects.info/",
    "license": "Other OSI approved licence",  # MIT
    "price": 50.00,
    "currency": "EUR",
    "depends": ["mail"],
    "external_dependencies": {"python": [], "bin": []},
    "data": ["template.xml", "full_composer_wizard.xml"],
    "demo": [],
    "qweb": ["static/src/xml/mail_private.xml"],
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

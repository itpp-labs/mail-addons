# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License MIT (https://opensource.org/licenses/MIT).
{
    "name": """Internal Messaging""",
    "summary": """Send private messages to specified recipients, regardless of who are in followers list.""",
    "category": "Discuss",
    "images": [],
    "version": "13.0.1.1.0",
    "application": False,
    "author": "IT-Projects LLC, Pavel Romanchenko",
    "support": "help@itpp.dev",
    "website": "https://twitter.com/OdooFree",
    "license": "Other OSI approved licence",  # MIT
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
}

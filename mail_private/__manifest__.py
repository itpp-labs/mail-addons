# Copyright 2016 x620 <https://github.com/x620>
# Copyright 2016 Ilmir Karamov <https://it-projects.info/team/ilmir-k>
# Copyright 2016 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2017 Artyom Losev <https://github.com/ArtyomLosev>
# Copyright 2018 Ruslan Ronzhin <https://it-projects.info/team/rusllan/>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License MIT (https://opensource.org/licenses/MIT).
{
    "name": """Internal Messaging""",
    "summary": """Send private messages to specified recipients, regardless of who are in followers list.""",
    "category": "Discuss",
    "images": ["images/mail_private_image.png"],
    "version": "11.0.1.2.0",
    "application": False,
    "author": "IT-Projects LLC, Pavel Romanchenko",
    "support": "apps@itpp.dev",
    "website": "https://it-projects.info",
    "license": "Other OSI approved licence",  # MIT
    "price": 50.00,
    "currency": "EUR",
    "depends": ["mail", "base", "mail_base"],
    "external_dependencies": {"python": [], "bin": []},
    "data": ["template.xml", "full_composer_wizard.xml"],
    "qweb": ["static/src/xml/mail_private.xml"],
    "demo": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "auto_install": False,
    "installable": True,
}

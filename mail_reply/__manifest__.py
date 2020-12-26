# -*- coding: utf-8 -*-
{
    "name": """Always show reply button""",
    "summary": """Got a message out of a Record? Now you can reply to it too!""",
    "category": "Discuss",
    "images": ["images/mail_reply.jpg"],
    "vesion": "10.0.1.0.0",
    "author": "IT-Projects LLC, Pavel Romanchenko",
    "support": "apps@itpp.dev",
    "website": "https://it-projects.info",
    "license": "Other OSI approved licence",  # MIT
    "depends": ["mail_base"],
    "external_dependencies": {"python": [], "bin": []},
    "data": ["templates.xml"],
    "qweb": ["static/src/xml/reply_button.xml"],
    "demo": [],
    "installable": True,
    "auto_install": False,
}

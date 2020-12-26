# -*- coding: utf-8 -*-
{
    "name": "Mail relocation",
    "version": "10.0.1.0.6",
    "author": "IT-Projects LLC, Ivan Yelizariev, Pavel Romanchenko",
    "license": "Other OSI approved licence",  # MIT
    "category": "Discuss",
    "images": ["images/m1.png"],
    "support": "apps@itpp.dev",
    "website": "https://twitter.com/yelizariev",
    "depends": ["mail_all", "web_polymorphic_field"],
    "data": ["mail_move_message_views.xml", "data/mail_move_message_data.xml"],
    "qweb": ["static/src/xml/mail_move_message_main.xml"],
    "installable": True,
}

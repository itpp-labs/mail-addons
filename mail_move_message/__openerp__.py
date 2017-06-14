# -*- coding: utf-8 -*-
{
    'name': 'Mail relocation',
    'version': '1.0.5',
    'author': 'IT-Projects LLC, Ivan Yelizariev, Pavel Romanchenko',
    'license': 'LGPL-3',
    'category': 'Discuss',
    'images': ['images/m1.png'],
    "support": "apps@it-projects.info",
    'website': 'https://twitter.com/yelizariev',
    'price': 100.00,
    'currency': 'EUR',
    'depends': ['mail_all', 'web_polymorphic_field'],
    'data': [
        'mail_move_message_views.xml',
        'data/mail_move_message_data.xml',
    ],
    'qweb': [
        'static/src/xml/mail_move_message_main.xml',
    ],
    'installable': True,
}

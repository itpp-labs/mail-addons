# -*- coding: utf-8 -*-
{
    'name': 'Outgoing mails menu',
    'version': '1.0.0',
    'author': 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'GPL-3',
    "category": "Discuss",
    'website': 'https://yelizariev.github.io',
    'description': """
        Allows to check outgoing mails, i.e. failed or delayed.
    """,
    'depends': ['mail'],
    'data': [
        'security/mail_outgoing.xml',
        'security/ir.model.access.csv',
        'mail_outgoing_views.xml',
    ],
    'installable': True
}

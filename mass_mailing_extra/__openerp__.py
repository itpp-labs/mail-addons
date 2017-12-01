# -*- coding: utf-8 -*-
{
    'name': 'Improvements for mass mailing',
    'version': '1.0.0',
    'author': 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'GPL-3',
    "category": "Discuss",
    'website': 'https://yelizariev.github.io',
    'description': """
        Modules adds:

        * partners info in mail.mail.statistics tree
        * partners info in mail.mail.statistics form
    """,
    'depends': ['mass_mailing'],
    'data': [
        'views.xml',
    ],
    'installable': True
}

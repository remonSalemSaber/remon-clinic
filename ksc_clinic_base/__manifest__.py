# -*- coding: utf-8 -*-
{
    'name': "Clinic",
    'author': "OmerAhmed1994,",
    'website': "http://www.github.com/OmerAhmed1994",
    'category': 'Clinic',
    'version': '14.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['contacts','portal','account'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/views.xml',
        'views/assets.xml',
        'views/appointment.xml',
        'views/payment.xml',
        'views/evaluation_view.xml',
        'wizard/wizard.xml',


        'views/menu_item.xml',
    ],
}

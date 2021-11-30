# -*- coding: utf-8 -*-
{
    'name': "radiology",
    'author': "OmerAhmed1994,",
    'website': "http://www.github.com/OmerAhmed1994",
    'category': 'Clinic',
    'version': '14.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['ksc_clinic_base'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/res_config.xml',
        'views/appointment.xml',
        'views/menu_item.xml',
    ],
}

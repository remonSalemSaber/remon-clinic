# -*- coding: utf-8 -*-
{
    'name': "Dental",
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
        'views/dental_view.xml',
        'views/menu_item.xml',


        'views/templates.xml',
       
        'data/dental_data.xml',
        'data/teeth_code.xml',
        'data/child_teeth_code.xml',

        'reports/planned_operation.xml',
        'reports/treatment_plan_details.xml',
        'reports/ortho_plan.xml',
    ],
    'qweb': [
        'static/src/xml/perio_base.xml',
        'static/src/xml/child_dental_chart.xml',
    ],
}

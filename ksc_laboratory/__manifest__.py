# -*- coding: utf-8 -*-
{ 
    'name': 'Laboratory Management',
    'summary': 'Manage Lab requests, Lab tests, Invoicing and related history for hospital.',
    'description': """
        This module add functionality to manage Laboratory flow. laboratory management system
        Hospital Management lab tests laboratory invoices laboratory test results 
    """,
    'author': "OmerAhmed1994,",
    'website': "http://www.github.com/OmerAhmed1994",
    'category': 'Clinic',
    'version': '14.0.0.0.1',
    'depends': ['stock','ksc_clinic_base'],
    'data': [
        # 'security/security.xml',
        'security/ir.model.access.csv',

        'report/report_ksc_lab_prescription.xml',
        'report/lab_report.xml',

        'data/mail_template.xml',
        'data/laboratory_data.xml',
        'data/lab_uom_data.xml',
        'data/lab_sample_type_data.xml',
        'views/lab_uom_view.xml',
        'views/laboratory_request_view.xml',
        'views/laboratory_view.xml',
        'views/laboratory_test_view.xml',
        'views/laboratory_sample_view.xml',
        'views/hms_base_view.xml',
        'views/res_config.xml',
        'views/templates_view.xml',
        'views/menu_item.xml',
    ],
    'installable': True,
    'application': True,
}
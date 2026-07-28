# Copyright 2026 Open2Bizz <info@open2bizz.nl>
# License LGPL-3

{
    'name': 'Management System Default Data',
    'summary': 'Default data templates for Management System fields',
    'version': '19.0.1.0.0',
    'category': 'Management System',
    'website': 'https://www.open2bizz.nl/',
    'author': 'Open2Bizz',
    'license': 'LGPL-3',
    'installable': True,
    'depends': [
        'default_data',
        'mgmtsystem_info_security_manual_nen7510',
    ],
    'data': [
        'views/mgmtsystem_action_views.xml',
        'views/mgmtsystem_root_cause_analysis_views.xml',
    ],
}

{
    'name': "purchase re",
    'author': "vote company",
    'category': '',
    'version': '16.0.0.1.0',
    'depends': ['base', 'sale_management', 'account', 'mail','stock','purchase','web_gantt'
                ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/base_menu.xml',
        'views/request_view.xml',
        'views/res_config_settings_views.xml',
        'views/purchase_order_view.xml',
        'reports/purchase_request_report.xml',
        'wizard/partner_id_wizard_view.xml',
    ],
    'application': True,
}

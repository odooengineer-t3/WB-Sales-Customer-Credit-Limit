# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Wan Buffer Solution (<https://wanbuffer.com/>).
#
#    For Module Support : info@wanbuffer.com  or Call : +91 9638442270
#
##############################################################################

{
    'name': 'Sales Customer Credit Limit',
    'version': '19.0.1.0.0',
    'category': 'sales',
    'summary': 'Implementation of Customer Credit Limit in Sales Module.',
    'description': """
        - The Customer Credit Limit module helps control customer credit and reduce financial risk.
        - It ensures sales orders do not exceed predefined credit limits by checking receivables and payables in real time.
        - Credit Limit, Total Receivables, and Total Payables are clearly visible to sales users.
        - Authorized users can approve over-credit orders via the Credit Approver tab.
        - The module integrates with Sales and Accounting, improving cash flow monitoring and credit management.
        - Overall, it streamlines the sales process while enforcing credit policies effectively.

    """,
    'author': 'Wan Buffer Services',
    'depends': ['sale_pdf_quote_builder','sale_management', 'account'],
    'data': [
        'security/credit_limit_security.xml',
        'security/ir.model.access.csv',
        'data/credit_limit_groups.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/res_config_settings_view.xml',
        'views/credit_limit_menu.xml',
        'views/credit_limit_request_views.xml',
        'views/res_users_view.xml',
        'wizard/credit_limit_approval_wizard_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'wb_sale_customer_credit_limit/static/src/css/credit_limit.css',
        ],
    },
    "images": ["static/description/background.png", ],
    
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    "website": "https://wanbuffer.com",
    "maintainer": "Wan Buffer Services",
    "support": "info@wanbuffer.com",
}


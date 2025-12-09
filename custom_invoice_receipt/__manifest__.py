{
    'name': 'Custom Invoice & Sales Receipt',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Print invoice and sales order in receipt format',
    'description': 'Generate small-format receipt printout for invoice and sales order (thermal printer style)',
    'author': 'Yayan Dev',
    'depends': ['base', 'sale', 'account', 'stock', 'hr'],
    'data': [
        'report/report_action.xml',
        'report/invoice_receipt_template.xml',
        'report/sales_receipt_template.xml',
        'report/do_reports_views.xml',
        'views/sales_order_line.xml',
        'wizard/do_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
}

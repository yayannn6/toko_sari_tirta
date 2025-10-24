{
    'name': 'Custom Invoice & Sales Receipt',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Print invoice and sales order in receipt format',
    'description': 'Generate small-format receipt printout for invoice and sales order (thermal printer style)',
    'author': 'Yayan Dev',
    'depends': ['base', 'sale', 'account'],
    'data': [
        'report/report_action.xml',
        'report/invoice_receipt_template.xml',
        'report/sales_receipt_template.xml',
    ],
    'installable': True,
    'application': False,
}

from odoo import models

class CustomReceipt(models.AbstractModel):
    _name = 'report.custom_invoice_receipt.report_receipt_invoice'
    _description = 'Custom Receipt for Invoice'

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        return {'docs': docs}

class CustomSalesReceipt(models.AbstractModel):
    _name = 'report.custom_invoice_receipt.report_receipt_sale'
    _description = 'Custom Receipt for Sales Order'

    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        return {'docs': docs}

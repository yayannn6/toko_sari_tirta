from odoo import models, fields, api

class TrukBelanjaWizard(models.TransientModel):
    _name = 'truk.belanja.wizard'
    _description = 'Wizard Print Truk Belanja'

    sale_order_ids = fields.Many2many('sale.order', string="Sales Orders (Optional)")

    def action_print(self):
        return self.env.ref(
            'custom_invoice_receipt.action_truk_belanja_report'
        ).report_action(self)

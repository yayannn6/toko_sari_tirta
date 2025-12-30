from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount_amount = fields.Monetary(
        string='Discount Amount',
        currency_field='currency_id',
        digits='Product Price',
        store=True,
    )

    @api.onchange('discount_amount', 'product_uom_qty', 'price_unit')
    def _onchange_discount_amount(self):
        for line in self:
            discount = line.discount_amount or 0.0
            after_discount_price = line.price_unit * line.product_uom_qty - discount
            line.price_subtotal = after_discount_price


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_print_receipt(self):
        """
        Print Sales Order Receipt (80mm)
        """
        self.ensure_one()
        return self.env.ref(
            'custom_invoice_receipt.action_report_receipt_sale'
        ).report_action(self)

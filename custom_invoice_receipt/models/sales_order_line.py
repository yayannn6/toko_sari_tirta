from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount_amount = fields.Monetary(
        string='Discount Amount',
        currency_field='currency_id',
        digits='Product Price',
        store=True,
    )


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_discount_amount = fields.Monetary(
        string='Total Discount Amount',
        currency_field='currency_id',
        digits='Product Price',
        compute='_compute_total_discount_amount',
        store=True,
    )

    @api.depends('order_line.discount_amount')
    def _compute_total_discount_amount(self):
        for order in self:
            order.total_discount_amount = sum(
                order.order_line.mapped('discount_amount')
            )

    @api.depends(
        'order_line.price_subtotal',
        'order_line.discount_amount',
        'currency_id'
    )
    def _compute_amounts(self):
        super()._compute_amounts()

        for order in self:
            discount = sum(order.order_line.mapped('discount_amount'))

            # kurangi untaxed dengan discount
            order.amount_untaxed -= discount

            # total = untaxed + tax
            order.amount_total = order.amount_untaxed + order.amount_tax

    def action_print_receipt(self):
        """
        Print Sales Order Receipt (80mm)
        """
        self.ensure_one()
        return self.env.ref(
            'custom_invoice_receipt.action_report_receipt_sale'
        ).report_action(self)

# sale_discount_amount/models/sale_order_line.py
from odoo import models, fields, api, _
from collections import defaultdict

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # New field: discount amount per line (monetary, stored)
    discount_amount = fields.Monetary(
        string='Discount Amount',
        currency_field='currency_id',
        store=True,
        digits='Product Price',
        help='Discount amount for this line (currency).',
    )

    # Keep discount (%) field (existing), but we will compute it from discount_amount
    # Override compute of amounts so percent is derived from amount, keeping tax code intact.

    @api.depends('product_id', 'product_uom_id', 'product_uom_qty',
                 'price_unit', 'discount_amount', 'order_id.pricelist_id', 'order_id.currency_id')
    def _compute_amount(self):
        """
        Override to ensure computed subtotal / taxes use discount (percent)
        which we set from discount_amount. This keeps tax computations in core working.
        """
        for line in self:
            # compute discount percent from discount_amount
            try:
                qty = line.product_uom_qty or 0.0
                unit = line.price_unit or 0.0
                line_total_before = unit * qty
                if line_total_before:
                    # discount percent is the proportion of discount_amount over line_total_before
                    line.discount = (line.discount_amount / line_total_before) * 100.0
                else:
                    line.discount = 0.0
            except Exception:
                line.discount = 0.0

        # Call super to let taxes and price_subtotal, price_tax be computed normally
        super(SaleOrderLine, self)._compute_amount()

        # After super, ensure price_subtotal reflects line.discount_amount exactly (avoid rounding mismatch)
        # price_subtotal computed by super uses discount percent. We can optionally recalc to be safe.
        for line in self:
            qty = line.product_uom_qty or 0.0
            unit = line.price_unit or 0.0
            line_total_before = unit * qty
            # Desired subtotal after discount amount:
            desired_subtotal = max(0.0, line_total_before - (line.discount_amount or 0.0))
            # taxes are computed by super based on discount percent. We keep them as-is,
            # but adjust price_subtotal if there is small mismatch due to rounding.
            # NOTE: don't forcibly overwrite price_tax here; leave tax computation to Odoo.
            # Only adjust price_subtotal if significant difference:
            if abs((line.price_subtotal or 0.0) - desired_subtotal) > 0.0001:
                line.price_subtotal = desired_subtotal

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_discount_amount(self):
        """
        Compute discount_amount from pricelist logic:
        - If pricelist applies and changes price, set discount_amount = (base_price - pricelist_price) * qty
        - Otherwise keep discount_amount as 0.0 (or existing value if manually set).
        This method will **not** overwrite discount_amount if user already set one manually;
        but it's useful to have automatic calculation similar to your percent logic.
        """
        # We don't replace core's _compute_discount; instead create our own compute helper
        # and call it from a scheduled place or adapt accordingly. But for simplicity,
        # we compute discount_amount here if it's zero and pricelist gives different price.
        for line in self:
            # default do not override user-provided discount_amount
            if line.display_type:
                line.discount_amount = 0.0
                continue

            # If order has pricelist and it's without_discount (core policy) then we derive amount
            pricelist = line.order_id.pricelist_id
            if not pricelist or pricelist.discount_policy != 'without_discount':
                # do nothing automatic; user can set discount_amount manually
                continue

            # We try to mimic the logic: get base price and applied pricelist price
            try:
                # Ensure with company context for currency / company specific
                l = line.with_company(line.company_id)
                pricelist_price = l._get_pricelist_price()
                base_price = l._get_pricelist_price_before_discount()
                qty = line.product_uom_qty or 0.0
                # compute amount = (base_price - pricelist_price) * qty
                if base_price is None or pricelist_price is None:
                    continue
                amount = (base_price - pricelist_price) * qty
                # only set when meaningful (avoid negative surcharges showing as discount)
                if (amount > 0 and base_price > 0) or (amount < 0 and base_price < 0):
                    line.discount_amount = amount
                else:
                    line.discount_amount = 0.0
            except Exception:
                # fallback: do not set
                continue

    # We want discount_amount to be computed when pricelist rules change etc.
    # So attach depends/decorators to onchange to keep it responsive:
    @api.onchange('product_id', 'product_uom', 'product_uom_qty', 'price_unit')
    def _onchange_compute_discount_amount(self):
        for line in self:
            # don't override manual adjustments
            if line.display_type:
                line.discount_amount = 0.0
                continue
            # If discount_amount is set manually (nonzero), keep it.
            if line.discount_amount:
                continue
            # compute automatically if pricelist policy requires it
            pricelist = line.order_id.pricelist_id
            if not pricelist or pricelist.discount_policy != 'without_discount':
                continue
            # compute similar to _compute_discount_amount
            try:
                l = line.with_company(line.company_id)
                pricelist_price = l._get_pricelist_price()
                base_price = l._get_pricelist_price_before_discount()
                qty = line.product_uom_qty or 0.0
                if base_price is None or pricelist_price is None:
                    continue
                amount = (base_price - pricelist_price) * qty
                if (amount > 0 and base_price > 0) or (amount < 0 and base_price < 0):
                    line.discount_amount = amount
                else:
                    line.discount_amount = 0.0
            except Exception:
                continue

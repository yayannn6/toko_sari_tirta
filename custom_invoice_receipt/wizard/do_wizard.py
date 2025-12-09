from odoo import models, fields, api

class TrukBelanjaWizard(models.TransientModel):
    _name = 'truk.belanja.wizard'
    _description = 'Wizard Print Truk Belanja'

    sale_order_ids = fields.Many2many('sale.order', string="Sales Orders")
    driver_id = fields.Many2one('hr.employee', string="Driver")

    def action_print(self):
        # --- update driver di stock.picking ---
        domain = [('state', '=', 'assigned')]

        if self.sale_order_ids:
            so_names = self.sale_order_ids.mapped('name')
            domain.append(('origin', 'in', so_names))

        pickings = self.env['stock.picking'].search(domain)

        # Update driver
        if self.driver_id:
            pickings.write({'driver_id': self.driver_id.id})

        return self.env.ref(
            'custom_invoice_receipt.action_truk_belanja_report'
        ).report_action(self)

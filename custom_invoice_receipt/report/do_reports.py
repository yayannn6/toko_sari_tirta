from odoo import models, api
from collections import defaultdict

class ReportTrukBelanja(models.AbstractModel):
    _name = 'report.custom_invoice_receipt.truk_belanja_template'
    _description = 'Report Truk Belanja'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['truk.belanja.wizard'].browse(docids)

        domain = [('state', '=', 'assigned')]

        # Filter DO berdasarkan origin = SO.name
        if wizard.sale_order_ids:
            so_names = wizard.sale_order_ids.mapped('name')
            domain.append(('origin', 'in', so_names))

        pickings = self.env['stock.picking'].search(domain)

        product_totals = defaultdict(float)

        for picking in pickings:
            for ml in picking.move_line_ids:
                product_totals[ml.product_id] += ml.quantity or 0

        lines = [{
            'product_name': p.name,
            'qty': int(qty)
        } for p, qty in product_totals.items()]

        return {
            'doc_ids': docids,
            'doc_model': 'truk.belanja.wizard',
            'docs': wizard,
            'lines': lines,
        }

from odoo import models, api
from collections import defaultdict

class ReportTrukBelanja(models.AbstractModel):
    _name = 'report.custom_invoice_report.truk_belanja_template'
    _description = 'Report Truk Belanja'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['truk.belanja.wizard'].browse(docids)

        # cari DO siap (assigned)
        domain = [('state', '=', 'assigned')]

        if wizard.sale_order_ids:
            domain.append(('group_id', 'in', wizard.sale_order_ids.mapped('procurement_group_id').ids))

        pickings = self.env['stock.picking'].search(domain)

        product_totals = defaultdict(float)

        for picking in pickings:
            for ml in picking.move_line_ids:
                product_totals[ml.product_id] += ml.qty_done or 0.0

        # mapping ke list untuk template
        lines = [{
            'product_name': p.name,
            'qty': qty
        } for p, qty in product_totals.items()]

        return {
            'doc_ids': docids,
            'doc_model': 'truk.belanja.wizard',
            'docs': wizard,
            'lines': lines,
        }

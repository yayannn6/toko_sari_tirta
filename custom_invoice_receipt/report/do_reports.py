from odoo import models, api
from collections import defaultdict

class ReportTrukBelanja(models.AbstractModel):
    _name = 'report.custom_invoice_receipt.truk_belanja_template'
    _description = 'Report Truk Belanja'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['truk.belanja.wizard'].browse(docids)

        # ================================
        # AMBIL DO (Stock Picking)
        # ================================
        domain = [('state', '=', 'assigned')]

        # Jika wizard memilih driver → filter DO yang punya driver tsb
        if wizard.driver_id:
            domain.append(('driver_id', '=', wizard.driver_id.id))

        pickings = self.env['stock.picking'].search(domain)
        for picking in pickings:
            picking.with_context(skip_backorder=False, cancel_backorder=False).button_validate()


        # ================================
        # KUMPULKAN SO DARI DO (origin)
        # ================================
        so_names = list({
            p.origin for p in pickings
        })

        # ================================
        # Hitungan Produk
        # ================================
        product_totals = defaultdict(float)
        total_qty = 0
        total_weight = 0
        total_price = 0

        for picking in pickings:
            for ml in picking.move_line_ids:
                qty = ml.quantity or ml.qty_done or 0
                product_totals[ml.product_id] += qty

                total_qty += qty
                total_weight += (ml.product_id.weight or 0) * qty
                total_price += (ml.product_id.list_price or 0) * qty

        # Lines produk
        lines = [{
            'product_name': p.name,
            'qty': int(qty),
            'weight': (p.weight or 0) * qty,
            'price': (p.list_price or 0) * qty,
        } for p, qty in product_totals.items()]

        return {
            'doc_ids': docids,
            'doc_model': 'truk.belanja.wizard',
            'docs': wizard,

            'lines': lines,
            'total_qty': total_qty,
            'total_weight': total_weight,
            'total_price': total_price,

            'driver_name': wizard.driver_id.name if wizard.driver_id else '',
            'total_so': len(so_names),
            'so_names': so_names,
        }

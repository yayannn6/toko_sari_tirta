# sale_discount_amount/models/sale_order_line.py
from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    driver_id = fields.Many2one('hr.employee', string='Driver', help='Driver responsible for this delivery order.')
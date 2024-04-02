
from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = ['purchase.order']

    purchase_request_id = fields.Many2one('purchase.re', string="Source Document", readonly=1)

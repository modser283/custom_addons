from odoo import models, api, fields

class PartnerWizard(models.TransientModel):
    _name="partner.wizard"

    partner_id = fields.Many2one('res.partner')

    def partner_name(self):
        purchase_request = self.env['purchase.re'].browse(self._context.get("active_id"))
        mylist = []
        for request_line in purchase_request.request_line:
             mylist.append((0,0, {'product_id': request_line.product_id.id, 'price_unit':0,'product_qty':request_line.quantity,}))
        self.env['purchase.order'].create({"partner_id":self.partner_id.id,'purchase_request_id':purchase_request.id, "order_line":mylist})
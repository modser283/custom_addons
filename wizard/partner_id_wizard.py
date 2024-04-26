from odoo import models, api, fields

class PartnerWizard(models.TransientModel):
    _name="partner.wizard"

    request_number = fields.Many2one('purchase.re')
    partner_id = fields.Many2one('res.partner')
    request_Date = fields.Datetime(default=fields.Datetime.now())
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    requested_by = fields.Many2one( comodel_name="res.users",required=True,copy=False,tracking=True,default=_get_default_requested_by)

    def partner_name(self):
        purchase_request = self.env['purchase.re'].browse(self._context.get("active_id"))
        mylist = []
        for request_line in purchase_request.request_line:
             mylist.append((0,0, {'product_id': request_line.product_id.id, 'price_unit':request_line.expected_price,'product_qty':request_line.quantity}))
        self.env['purchase.order'].create({"partner_id":self.partner_id.id,'purchase_request_id':purchase_request.id,
                                           'payment_term_id':purchase_request.payment_term.id,'user_id':purchase_request.request_for.id,"order_line":mylist})
from odoo import models, fields, api, _
from xdg.Exceptions import ValidationError
from odoo.exceptions import ValidationError


class PurchaseReq(models.Model):
    _name = 'purchase.re'
    _description = 'requests Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'ref'
    ref = fields.Char(readonly=1, string="Reference", default='New',)
    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    requested_by = fields.Many2one( comodel_name="res.users",required=True,copy=False,tracking=True,default=_get_default_requested_by)
    request_line = fields.One2many('request.line', 'request_id', string="Request", required=1)
    request_date = fields.Datetime(default=fields.Datetime.now() , tracking=1, required=1)
    order_id =fields.Many2one('purchase.order')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('confirm', 'Confirm'),
        ('received', 'Received'),
    ], default='draft', tracking=1, string="Status")

    purchase_lines = fields.Many2many(
        comodel_name="purchase.order.line",
        string="Purchase Order Lines",
        readonly=True,
        copy=False,
    )
    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_submit(self):
        for rec in self:
           self.env["mail.activity"].create({
               "res_id": self.id,
               "res_model_id": self.env.ref("purchase_re.model_purchase_re").id,
               "summary": "Check Confirmation",
               "date_deadline": fields.Date.today(),
               "user_id": 2,
               "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
           })
           rec.state = 'submit'

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'



    def action_open_related_rfq(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        lines = self.mapped("request_line.purchase_lines.order_id")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = lines.id
        return action


    def action_purchase_order(self):

        return {'type': 'ir.actions.act_window',
                'res_model': 'partner.wizard',
                'view_mode': 'form',
                'target': 'new'}
        # mylist = []
        # for request_line in self.request_line:
        #      mylist.append((0,0, {'product_id': request_line.product_id.id, 'price_unit':0,'product_qty':request_line.quantity,}))
        # self.env['purchase.order'].create({"partner_id":1,'purchase_request_id':self.id, "order_line":mylist})


    @api.model
    def create(self, vals):
        res = super(PurchaseReq, self).create(vals)
        if res.ref == 'New':
             res.ref = self.env['ir.sequence'].next_by_code('purchase.seq')
        return res


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for rec in self:
            rec.purchase_id.purchase_request_id.state= 'received'
        return res



    # def action_view_stock_picking(self):
    #     action = self.env["ir.actions.actions"]._for_xml_id(
    #         "stock.action_picking_tree_all"
    #     )
    #     # remove default filters
    #     action["context"] = {}
    #     lines = self.mapped(
    #         "line_ids.purchase_request_allocation_ids.stock_move_id.picking_id"
    #     )
    #     if len(lines) > 1:
    #         action["domain"] = [("id", "in", lines.ids)]
    #     elif lines:
    #         action["views"] = [(self.env.ref("stock.view_picking_form").id, "form")]
    #         action["res_id"] = lines.id
    #     return action


class RequestLine(models.Model):
    _name = 'request.line'

    request_id = fields.Many2one('purchase.re', tracking=1)
    product_id = fields.Many2one('product.product', required=1)
    description = fields.Text(tracking=1)
    quantity = fields.Integer(tracking=1, default=1, string="Quantity")
    expected_date = fields.Datetime()

    @api.constrains('quantity')
    def _check_quantity_greater_zero(self):
        for rec in self:
            if rec.quantity == 0:
                raise ValidationError(_("Please Add Valid Number Of Quantity"))








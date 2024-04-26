from odoo import models, fields, api, _
from xdg.Exceptions import ValidationError
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import requests


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
    request_date = fields.Datetime(default=fields.Datetime.now())
    order_id =fields.Many2one('purchase.order')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('confirm', 'Confirm'),
        ('received', 'Received'),
    ], default='draft', tracking=1, string="Status")

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], string="Priority")

    purchase_ids = fields.One2many('purchase.order', 'purchase_request_id')
    request_for = fields.Many2one('res.users')
    request_company = fields.Many2one('res.company', string="Request Company")

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    payment_term = fields.Many2one('account.payment.term')


    def create_partner(self):
        response = requests.get('https://randomuser.me/api')

        first_name = response.json()['results'][0]['name']['first']
        address = response.json()['results'][0]['location']['street']
        phone = response.json()['results'][0]['phone']
        email = response.json()['results'][0]['email']

        self.env['res.partner'].sudo().create({'name': first_name, 'street': address, 'phone': phone, 'email': email})


    @api.ondelete(at_uninstall=False)
    def _check_appointment(self):
        for rec in self:
            if rec.request_line:
                raise ValidationError(_("You cannot delete a request with products"))

    def create_history_record(self, old_state, new_state):
        for rec in self:
            rec.env['purchase.re.history'].create({
                'user_id': rec.env.uid,
                'request_id': rec.id,
                'old_state': old_state,
                'new_state': new_state,
            })



    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError('You cannot delete a purchase request which is not draft.')

        return super(PurchaseReq, self).unlink()

    def action_draft(self):
        for rec in self:
            rec.create_history_record(rec.state, 'draft')
            rec.state = 'draft'

    def action_submit(self):
        for rec in self:
            rec.create_history_record(rec.state, 'submit')
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
            rec.create_history_record(rec.state, 'confirm')
            rec.state = 'confirm'
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Successful, Please wait The managment',
                'type':'rainbow_man'}
        }



    def action_open_related_rfq(self):
        return {
            'name': _('Request for Qutation'),
            'res_model': 'purchase.order',
            'view_mode':'list ',
            'context': {},
            # 'domain': [('order_id', '=', 'self.id')],
            'target': 'current',
            'type': 'ir.actions.act_window',
        }


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
    expected_price = fields.Float( string='Expected Price',related='product_id.list_price')
    expected_date = fields.Datetime()
    currency_id = fields.Many2one('res.currency', related='request_id.currency_id')
    subtotal = fields.Monetary(string='Subtotal', compute='_compute_subtotal')

    @api.depends('expected_price', 'quantity')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.expected_price * rec.quantity

    @api.constrains('quantity')
    def _check_quantity_greater_zero(self):
        for rec in self:
            if rec.quantity == 0:
                raise ValidationError(_("Please Add Valid Number Of Quantity"))








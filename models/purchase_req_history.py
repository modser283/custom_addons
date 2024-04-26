from odoo import models, fields, api, _
from xdg.Exceptions import ValidationError
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import requests


class PurchaseReqHistory(models.Model):
    _name = 'purchase.re.history'
    _description = 'requests History Record'

    user_id = fields.Many2one('res.users')
    request_id = fields.Many2one('purchase.re')
    old_state = fields.Char()
    new_state = fields.Char()
    date_change = fields.Datetime(default=fields.Datetime.now(), string='Chane Time')

# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    request_date = fields.Datetime(string='Request Date', config_parameter='purchase_re.request_date')

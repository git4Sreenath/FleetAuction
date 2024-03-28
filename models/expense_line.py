# -*- coding: utf-8 -*-

from odoo import fields, models


class ExpenseLine(models.Model):
    _name = "expense.line"
    _description = "Expenses Line"

    expense_product_id = fields.Many2one('product.product',
                                         straction_confirming="Expense")
    expense_amount = fields.Float(string="Price",
                                  related="expense_product_id.list_price")
    expense_id = fields.Many2one(comodel_name='fleet.auction',)

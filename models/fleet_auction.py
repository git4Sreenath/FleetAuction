# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models
from odoo.exceptions import ValidationError


class FleetAuction(models.Model):
    _name = "fleet.auction"
    _description = "Fleet Auction"
    _inherit = 'mail.thread'

    name = fields.Char(copy=False, string="Sequence", help="sequence",
                       readonly=True)
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle",
                                 help="Choose the vehicle", required=True)
    brand_id = fields.Many2one('fleet.vehicle.model.brand',
                               related="vehicle_id.brand_id", string="Brand",
                               help="Brand of the vehicle")
    start_date = fields.Date(help="choose the start date", string="Start Date")
    end_date = fields.Date(help="Choose the start date", string="End Date")
    user_id = fields.Many2one('res.users', string="Responsible",
                              default=lambda self: self.env.user,
                              help="responsible person")
    active = fields.Boolean(default=True, string="Active", help="active")
    state = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("ongoing", "Ongoing"),
        ("success", "Success"),
        ("cancelled", "Cancelled"), ], default='draft', tracking=True,
        string="State", help="state")
    description = fields.Html(string="Description", help="Add description")
    image = fields.Binary(string="Image", help="add image here")
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.company.id,
                                 string="Company", help="Company")
    currency_id = fields.Many2one('res.currency',
                                  default=lambda
                                  self: self.company_id.currency_id.id,
                                  string="Currency",
                                  help="Currency")
    start_price = fields.Monetary(string="Start Price", copy=False,
                                  help="Starting price is here")
    won_price = fields.Monetary(string="Won price", copy=False,
                                help="Won price")
    partner_id = fields.Many2one('res.partner', string="Customer",
                                 help="Choose the customer",
                                 readonly=True)
    partner_email = fields.Char(string="Email", related="partner_id.email",
                                help="email id")
    partner_phone = fields.Char(string="Phone", related="partner_id.phone",
                                help="phone number")
    tag_ids = fields.Many2many(comodel_name='crm.tag', string="Tags")
    confirmed_bid_ids = fields.One2many('auction.bid',
                                        inverse_name="auction_id",
                                        string="confirmed bid",
                                        domain=[('state', '!=', 'draft')])
    total_auction_bid_ids = fields.One2many('auction.bid',
                                            inverse_name="auction_id",
                                            string="total_bid")
    bids_count = fields.Integer(compute="_compute_bid_count")
    expense_ids = fields.One2many('expense.line',
                                  inverse_name="expense_id")
    total_expense = fields.Monetary(compute="_compute_total_expense",
                                    String="Total", store=True)
    auction_invoice_id = fields.Many2one('account.move', )
    payment_state_after_register_payment = fields.Char(
        compute="_compute_payment_state")
    invoice_or_not = fields.Boolean()

    @api.constrains('end_date', 'start_date')
    def date_constrains(self):
        """validation for start and end dates, ensuring the start date precedes
         the end date."""
        for rec in self:
            if rec.end_date and rec.start_date:
                if rec.end_date < rec.start_date:
                    raise ValidationError(
                        'Error, End Date Must be greater Than Start Date...')
            else:
                raise ValidationError(
                    'Error, please choose End Date and Start Date...')

    def action_confirm_auction(self):
        """'Confirm Auction' button; when clicked, change the state to
        'confirmed.'"""
        self.state = 'confirmed'

    def action_cancel_auction(self):
        """'Cancel Auction' button; when clicked, change the state to
        # 'canceled.'"""
        user = self.env.user

        if user.has_group('fleet_auction.fleet_auction_manager_rights'):
            self.state = 'cancelled'

        elif user.has_group('fleet_auction.fleet_auction_user_access'):
            return {
                'name': 'AuctionCanceledWizard',
                'view_mode': 'form',
                'res_model': 'auction.canceled.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new'
            }

    def action_end_auction(self):
        """'end Auction' button; when clicked, change the state to
        'success.'"""
        self.state = 'success'

    @api.model_create_multi
    def create(self, vals):
        """Generate sequences for each record"""
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code(
                'fleet_auction_sequence_code')
        return super().create(vals)

    def action_stop_auction(self):
        """find out the highest bid and updated the customer"""
        highest = 0
        for bid in self.confirmed_bid_ids:
            price = bid.bid_price
            if price > highest:
                highest = price
                self.partner_id = bid.partner_id
        self.won_price = highest
        self.state = 'success'
        mail_template = (
            self.env.ref('fleet_auction.congratulation_email_template'))
        mail_template.send_mail(self.id, force_send=True)
        print('stop', self.id)

    def _compute_bid_count(self):
        """count of all bids created under the auction."""
        for res in self:
            total_len = len(self.total_auction_bid_ids)
            res.bids_count = total_len

    def action_bids_count(self):
        """button for total number of bids in an auction"""
        return {
            'name': 'bid',
            'view_mode': 'tree',
            'res_model': 'auction.bid',
            'type': 'ir.actions.act_window',
            'domain': [('auction_id', '=', self.name)]
        }

    @api.depends('expense_ids.expense_amount')
    def _compute_total_expense(self):
        """To compute total expense"""
        for record in self:
            record.total_expense = sum(
                line.expense_amount for line in record.expense_ids)

    def action_create_invoice(self):
        """invoice of auction """
        for record in self:
            invoice_line_commands = []  # single line --> use list comprehension
            for expense in record.expense_ids:
                invoice_line_commands.append(
                    Command.create({
                        'product_id': expense.expense_product_id.id,
                        'quantity': 1,
                    })
                )
            auction_invoice = self.env['account.move'].create(
                {
                    'move_type': 'out_invoice',
                    'invoice_date': fields.Date.context_today(record),
                    'partner_id': record.partner_id.id,
                    'amount_total': self.total_expense,
                    'invoice_line_ids': invoice_line_commands,
                },
            )
            self.auction_invoice_id = auction_invoice.id
            self.invoice_or_not = True
        return {
            'name': 'AccountMove',
            'view_mode': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'res_id': auction_invoice.id
        }

    def action_view_invoice(self):
        """smart button for invoice  auction"""
        return {
            'name': 'AccountMove',
            'view_mode': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'res_id': self.auction_invoice_id.id
        }

    @api.depends("auction_invoice_id")
    def _compute_payment_state(self):
        """to get payment state from invoice record"""
        for record in self:
            record.payment_state_after_register_payment = (
                record.auction_invoice_id.payment_state)

    def action_date(self):
        """automatically start and end the auction
         based on the start and end date """
        start_date_records = self.search([
            ('start_date', '=', fields.Date.today())])
        for rec in start_date_records:
            if rec.state == 'confirmed':
                if rec.start_date <= fields.Date.today():
                    rec.state = 'ongoing'
        end_date_records = self.search(
            [('end_date', '=', fields.Date.today())])
        for reco in end_date_records:
            if reco.state != 'success':
                if reco.end_date == fields.Date.today():
                    highest = 0
                    for bid in reco.confirmed_bid_ids:
                        if bid.partner_id:
                            price = bid.bid_price
                            if price > highest:
                                highest = price
                                reco.partner_id = bid.partner_id
                        mail_template = (
                            self.env.ref(
                                'fleet_auction.congratulation_email_template'))
                        mail_template.send_mail(reco.id, force_send=True)
                    reco.won_price = highest
                    reco.state = 'success'

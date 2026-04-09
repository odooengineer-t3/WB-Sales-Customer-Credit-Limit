# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Wan Buffer Solution (<https://wanbuffer.com/>).
#
#    For Module Support : info@wanbuffer.com  or Call : +91 9638442270
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_credit_limit = fields.Monetary(string="Customer Credit Limit",
                                          related='partner_id.credit_limit_amount',
                                          readonly=True, store=True, currency_field='currency_id')
    partner_total_receivables = fields.Monetary(string="Total Receivables",
                                                related='partner_id.total_receivables',
                                                readonly=True, store=True, currency_field='currency_id')
    exceeded_amount = fields.Monetary(string="Exceeded Amount", compute='_compute_exceeded_amount',
                                      store=True, currency_field='currency_id')
    credit_approved = fields.Boolean(string="Credit Approved", default=False)
    credit_approval_request_id = fields.Many2one('credit.limit.request', string="Credit Approval Request")
    allow_credit_check = fields.Boolean(string="Allow Credit Check",
                                         related='partner_id.allow_credit_check', readonly=True, store=True)

    remaining_credit = fields.Monetary(
        string="Remaining Credit",
        compute="_compute_remaining_credit",
        store=True,
        currency_field='currency_id'
    )

    @api.depends('partner_credit_limit', 'partner_total_receivables', 'amount_total')
    def _compute_remaining_credit(self):
        for order in self:
            if not order.partner_id.allow_credit_check:
                order.remaining_credit = 0.0
                continue

            # If no credit limit is configured for this customer, treat it as 0.0
            # so the UI can explicitly show "Customer Credit Limit is ₹ 0.00" in red.
            if not order.partner_credit_limit:
                order.remaining_credit = 0.0
                continue

            order.remaining_credit = order.partner_credit_limit - order.amount_total

    @api.depends('partner_id','amount_total')
    def _compute_exceeded_amount(self):
        for order in self:
            order.exceeded_amount = 0.0
            partner = order.partner_id
            if not partner or not partner.allow_credit_check or not partner.credit_limit_amount:
                continue
            outstanding = partner.total_receivables or 0.0
            # calculate new outstanding if this order is confirmed
            new_total = outstanding + (order.amount_total or 0.0)
            if new_total > partner.credit_limit_amount:
                order.exceeded_amount = new_total - partner.credit_limit_amount
            else:
                order.exceeded_amount = 0.0

    def action_request_credit_approval(self):
        """Create or open a credit.limit.request for this order."""
        self.ensure_one()
        if self.allow_credit_check == False:
            raise UserError(_("Credit limit check is disabled for this customer."))
        if self.remaining_credit >= 0:
            raise UserError(_("Customer is not exceeding credit limit. No approval needed."))
        return {
            'name': _('Credit Approval Request'),
            'type': 'ir.actions.act_window',
            'res_model': 'credit.limit.approval.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
            }
        }

    def action_confirm(self):
        # block confirmation if exceeded and not approved
        for order in self:
            if order.partner_id.allow_credit_check and order.remaining_credit < 0 and not order.credit_approved:
                raise ValidationError(_(
                    "Cannot confirm order because customer '%s' exceeds their credit limit by %s. "
                    "Please request credit approval."
                ) % (order.partner_id.name, abs(order.remaining_credit)))
        return super().action_confirm()

    

    

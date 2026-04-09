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
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_limit_amount = fields.Monetary(
        string="Credit Limit Amount",
        currency_field='company_currency_id',
        help="Maximum credit allowed for this customer"
    )
    allow_credit_check = fields.Boolean(string="Enable Credit Limit", default=False)
    total_receivables = fields.Monetary(string="Total Receivables", compute='_compute_totals', store=True,
                                       currency_field='company_currency_id')
    total_payables = fields.Monetary(string="Total Payables", compute='_compute_totals', store=True,
                                     currency_field='company_currency_id')
    credit_approver_id = fields.Many2one('res.users', string="Credit Approver",
                                         help="User who can approve credit exceptions for this customer")
    company_currency_id = fields.Many2one('res.currency',
                                          string="Currency", default=lambda self: self.env.company.currency_id)

    def _compute_totals(self):
        Account = self.env['account.move']
        for partner in self:
            # Receivables: customer invoices (out_invoice) not fully paid
            invoices_recv = Account.search([
                ('partner_id', '=', partner.id),
                ('move_type', '=', 'out_invoice'),
                ('state', 'in', ['draft', 'posted']),
                ('payment_state', 'in', ['not_paid', 'partial'])
            ])
            partner.total_receivables = sum(invoices_recv.mapped('amount_residual') or [0.0])

            # Payables: supplier invoices (in_invoice) not fully paid
            invoices_pay = Account.search([
                ('partner_id', '=', partner.id),
                ('move_type', '=', 'in_invoice'),
                ('state', 'in', ['draft', 'posted']),
                ('payment_state', 'in', ['not_paid', 'partial'])
            ])
            partner.total_payables = sum(invoices_pay.mapped('amount_residual') or [0.0])

    @api.constrains('credit_limit_amount')
    def _check_credit_limit_non_negative(self):
        for p in self:
            if p.credit_limit_amount < 0:
                raise ValidationError(_("Credit Limit cannot be negative."))

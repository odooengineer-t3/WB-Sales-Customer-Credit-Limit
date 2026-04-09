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

class CreditLimitRequest(models.Model):
    _name = 'credit.limit.request'
    _description = 'Credit Limit Approval Request'
    _rec_name = 'reference'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reference = fields.Char(string="Reference", compute='_compute_reference', store=True)
    sale_order_id = fields.Many2one('sale.order', string="Sale Order", required=True)
    partner_id = fields.Many2one('res.partner', string="Customer", required=True)
    requested_by = fields.Many2one('res.users', string="Requested By", default=lambda self: self.env.uid)
    approver_id = fields.Many2one('res.users', string="Approver")
    amount_exceeded = fields.Monetary(string="Amount Exceeded", currency_field='company_currency_id')
    state = fields.Selection([('draft', 'Draft'), ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                             string="Status", default='draft')
    company_currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    

    @api.depends('sale_order_id')
    def _compute_reference(self):
        for rec in self:
            rec.reference = rec.sale_order_id.name or _("Request")

    def action_approve(self):
        for rec in self:
            if not self.env.user.has_group('sale_customer_credit_limit.group_credit_limit_approver'):
                raise UserError(_("You don't have permission to approve credit requests."))
            rec.state = 'approved'
            # mark sale order approved
            if rec.sale_order_id:
                rec.sale_order_id.credit_approved = True
                rec.sale_order_id.message_post(body=_("Credit approved by %s" % self.env.user.name))
            rec.message_post(body=_("Request approved by %s" % self.env.user.name))

    def action_reject(self):
        for rec in self:
            if not self.env.user.has_group('sale_customer_credit_limit.group_credit_limit_approver'):
                raise UserError(_("You don't have permission to reject credit requests."))
            rec.state = 'rejected'
            rec.message_post(body=_("Request rejected by %s" % self.env.user.name))

# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Wan Buffer Solution (<https://wanbuffer.com/>).
#
#    For Module Support : info@wanbuffer.com  or Call : +91 9638442270
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CreditLimitApprovalWizard(models.TransientModel):
    _name = 'credit.limit.approval.wizard'
    _description = 'Credit Limit Approval Wizard'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", required=True, readonly=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='sale_order_id.currency_id',
        store=True,
        readonly=True,
    )

    
    partner_id = fields.Many2one('res.partner', string="Customer", related="sale_order_id.partner_id", readonly=True)
    remaining_credit = fields.Monetary(string="Remaining Credit", related="sale_order_id.remaining_credit", readonly=True,currency_field='currency_id')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        sale_order_id = self.env.context.get('default_sale_order_id')
        if sale_order_id:
            order = self.env['sale.order'].browse(sale_order_id)
            # Force recompute in case it's a computed field (not stored)
            order._compute_remaining_credit()
            res['remaining_credit'] = order.remaining_credit
        return res

    def action_confirm_credit(self):
        """Approve the credit and mark sale order as approved."""
        self.ensure_one()
        order = self.sale_order_id

        if not self.env.user.has_group('wb_sale_customer_credit_limit.group_credit_limit_approver'):
            raise UserError(_("You do not have permission to approve credit requests."))

        # Approve credit
        order.credit_approved = True
        order.message_post(body=_("Credit approval confirmed by %s.") % self.env.user.name)
        # If the order is still a quotation, allow it to proceed by confirming it now that credit is approved.
        # This matches the expected flow where approval immediately unblocks invoicing.
        if order.state == 'draft':
            order.action_confirm()

        # Re-open the sales order so the UI refreshes (and "Create Invoice" becomes visible when applicable).
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales Order'),
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': order.id,
            'target': 'current',
        }
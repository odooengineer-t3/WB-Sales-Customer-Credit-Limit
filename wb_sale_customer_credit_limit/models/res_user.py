# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Wan Buffer Solution (<https://wanbuffer.com/>).
#
#    For Module Support : info@wanbuffer.com  or Call : +91 9638442270
#
##############################################################################

from odoo import api, fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    # Boolean helper to identify credit approver role
    is_credit_approver = fields.Boolean(
        string="Credit Approver",
        compute='_compute_is_credit_approver',
        inverse='_inverse_is_credit_approver',
        store=True
    )

    # Optional: company-dependent credit limit

    @api.depends('groups_id')
    def _compute_is_credit_approver(self):
        group = self.env.ref('wb_sale_customer_credit_limit.group_credit_limit_approver', raise_if_not_found=False)
        for user in self:
            user.is_credit_approver = group in user.groups_id if group else False

    def _inverse_is_credit_approver(self):
        """Toggle group membership when checkbox is changed."""
        credit_group = self.env.ref('wb_sale_customer_credit_limit.group_credit_limit_approver', raise_if_not_found=False)
        if not credit_group:
            return
        for user in self:
            if user.is_credit_approver:
                user.groups_id = [(4, credit_group.id)]  # Add group
            else:
                user.groups_id = [(3, credit_group.id)]  # Remove group
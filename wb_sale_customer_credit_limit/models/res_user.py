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

    def _compute_is_credit_approver(self):
        for user in self:
            user.is_credit_approver = user.has_group('wb_sale_customer_credit_limit.group_credit_limit_approver')

    def _inverse_is_credit_approver(self):
        """Toggle group membership when checkbox is changed."""
        credit_group = self.env.ref('wb_sale_customer_credit_limit.group_credit_limit_approver', raise_if_not_found=False)
        if not credit_group:
            return
        for user in self:
            if user.is_credit_approver:
                credit_group.user_ids = [(4, user.id)]  # Add user to group
            else:
                credit_group.user_ids = [(3, user.id)]  # Remove user from group
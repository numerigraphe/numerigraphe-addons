# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2014 Numérigraphe SARL. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv

class AccountBudgetPosition (osv.osv):
    """Add purchase orders to budget positions"""
    _inherit = 'account.budget.post'
    
    PURCHASE_SIGNS = [
        ('+', 'Positive'),
        ('-', 'Negative'),
    ]
    
    _columns = {
        'include_purchase': fields.boolean('Include Purchase Orders',
            help="Check this box to take Purchase orders into account.\n"
                 "If unchecked, only the Accounting Entries will be "
                 "taken into account.\n"
                 "This field lets managers make more realistic Budgets "
                 "when dealing with suppliers who send their invoices late "
                 "(i.e. monthly invoices after reception).\n"
             ),
        'purchase_sign': fields.selection(PURCHASE_SIGNS, "Sign",
            help="If you select 'Positive', the sum of all the "
                 "lines of Purchase Orders already confirmed but not yet "
                 "Invoiced will be added to the 'real amount' of all the "
                 "Budget Lines that use this Budgetary position.\n"
                 "If you select 'Negative', it will be substracted "
                 "instead.\n"
                 ),
    }
AccountBudgetPosition()

class BudgetLine(osv.osv):
    """Adapt the computation of the Real amount"""
    
    _inherit = "crossovered.budget.lines"
    
    def _prac(self, cr, uid, ids, name, args, context=None):
        """Optionally add/substract the amount of the Purchase Order Lines"""
        # FIXME
        pass
BudgetLine()


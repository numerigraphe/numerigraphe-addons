# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2013 Numérigraphe SARL. All Rights Reserved.
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

import time

import netsvc
from osv import fields, osv
from tools.translate import _

class PurchaseOrder (osv.osv):
    """Display a warning when confirming a Purchase if the budget is too low"""
    _inherit = 'purchase.order'
     
    # Initialization (no context)
    
    def __init__(self, pool, cr):
        """Add a new state value"""
        super(PurchaseOrder, self).STATE_SELECTION.append(('over_budget', 'Over Budget'))
        return super(PurchaseOrder, self).__init__(pool, cr)
     
    # Workflow Action methods (no context)
    
    def wkf_over_budget(self, cr, uid, ids):
        """Change the Purchase Order's state to 'Over Budget'"""
        self.write(cr, uid, ids, {'state': 'over_budget'})
        return True
    
    # Model methods (optional context, no context when called by the Workflow Engine)
    
    def exhausted_budget_lines(self, cr, uid, ids, context=None):
        """
        Find the Budget Line which do not have enough funds left to pay the Purchase Orders
        
        @return: IDs of the Budget Lines"""
        
        if not isinstance(ids, list):
            ids = [ids]
        
        # FIXME should sum all the similar purchase order lines
        budget_line_ids = set()
        b_line_obj = self.pool.get('crossovered.budget.lines')
        today = time.strftime('%Y-%m-%d')
        for id in ids:
            for ol in self.browse(cr, uid, id, context=context).order_line:
                if ol.account_analytic_id:
                    # FIXME should check sub-accounts too
                    bl_ids = b_line_obj.search(cr, uid,
                        [('analytic_account_id', '=', ol.account_analytic_id.id),
                         ('date_from', '<=', today),
                         ('date_to', '>=', today) ],
                        context=context)
                    budget_line_ids.update(
                        [l.id for l in b_line_obj.browse(cr, uid,
                                                         bl_ids,
                                                         context=context)
                         if l.crossovered_budget_id.state == 'validate'
                         and l.practical_amount - ol.price_subtotal < l.theoritical_amount]
                   )
        return list(budget_line_ids)
    
    def button_confirm(self, cr, uid, ids, context=None):
        """Advance the workflow instance and pop up a message if the state changes to 'Over Budget'.
        
        @return: True if all orders are OK, or an client action dictionary to open a confirmation wizard if any order is over-budget.
        """
        
        if context is None:
            context = {}
        if not isinstance(ids, list):
            ids = [ids]
        
        # Send the workflow signal on every purchase order
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_validate(uid, self._name, id, 'purchase_confirm', cr)
        
        # Return True or an Action dictionary
        orders_ok = all([o.state != 'over_budget' for o in self.browse(cr, uid, ids, context=context)])
        
        action_ctx = context.copy()
        action_ctx.update({'active_model': 'purchase.order',
                           'active_ids': ids,
                           'active_id': ids[0]})
        return orders_ok or {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.budget.wizard',
            'name': _("Budget warning"),
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy': True,
            'context': action_ctx
        }
PurchaseOrder()

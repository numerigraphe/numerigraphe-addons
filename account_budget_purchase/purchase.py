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
        
        @return: IDs of the Budget Line"""
        
        # FIXME not implemented
        return [1, 2]
    
    def button_confirm(self, cr, uid, ids, context=None):
        """Advance the workflow instance and pop up a message if the state changes to 'Over Budget'.
        
        @return: True if all orders are OK, or an client action dictionary to open a confirmation wizard if any order is over-budget.
        """
        
        # Send the workflow signal on every purchase order
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_validate(uid, self._name, id, 'purchase_confirm', cr)
        
        orders_ok = all([o.state != 'over_budget' for o in self.browse(cr, uid, ids, context=context)])
        return orders_ok or {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.budget.wizard',
            'name': _("Budget warning"),
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy': True,
            'context': context
        }
PurchaseOrder()

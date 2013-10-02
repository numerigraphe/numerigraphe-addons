# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2013 Numérigraphe SARL. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv

class stock_inventory(osv.osv):

    _inherit = 'stock.inventory'

    def inventory_lines(self, inventory):
        """ Generator of lines of inventories and sub-inventories
        
        This lets the valuation method compute the total of the whole inventory and sub-inventories"""
        for line in super(stock_inventory, self).inventory_lines(inventory):
            yield line
        for inv_id in inventory.inventory_ids:
            for line in self.inventory_lines(inv_id):
                yield line

    def action_confirm(self, cr, uid, ids, context=None):
        """ Do not compute valuation on inventories which have parents"""
        # Create a context without valuation
        if context is None:
            context = {}
        ctx_wo_valuation = context.copy()
        ctx_wo_valuation['valuation'] = False
        
        # Process non-root inventories, with valuation disabled
        branch_ids = self.search(cr, uid,
           [('id', 'in', ids), ('parent_id', '!=', False)], context=context)
        if branch_ids:
            res = super(stock_inventory, self).action_confirm(cr, uid, branch_ids, context=ctx_wo_valuation)
        
        # Process root inventories
        root_ids = [i for i in ids if i not in branch_ids]
        if root_ids:
            res = super(stock_inventory, self).action_confirm(cr, uid, root_ids, context=context)
        
        return res



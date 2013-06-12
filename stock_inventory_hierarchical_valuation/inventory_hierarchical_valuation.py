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

from osv import osv

class inventory_hierarchical_valuation(osv.osv):

    _inherit = 'stock.inventory'

    def inventory_lines(self, inventory):
        """ Browse lines of inventories and sub inventories """
        for line in super(inventory_hierarchical_valuation, self).inventory_lines(inventory):
            yield line
        for inv_id in inventory.inventory_ids:
            for line in self.inventory_lines(inv_id):
                yield line

    def action_confirm(self, cr, uid, ids, context=None):
        """ Block inventory valuation if the inventory have parents (parent_id field not empty)"""
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.parent_id:
                context['valuation'] = False
        return super(inventory_hierarchical_valuation, self).action_confirm(cr, uid, ids, context=context)

inventory_hierarchical_valuation()

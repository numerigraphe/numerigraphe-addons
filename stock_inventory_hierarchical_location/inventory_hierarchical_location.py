# -*- encoding: utf-8 -*-
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
from tools.translate import _


class inventory_hierarchical_location(osv.osv):

    _inherit = 'stock.inventory'

    def action_open(self, cr, uid, ids, context=None):
        """ Open the inventory :
        Only if all children inventories are open.
        """
        children_count = self.search(cr, uid, [('parent_id', 'child_of', ids),
                                             ('state', '!=', 'open')], context=context, count=True)
        if children_count > 1:
            raise osv.except_osv(_('Warning !'), _('Some Sub-inventories are not open.'))
        return self.write(cr, uid, ids, {'state': 'open'}, context=context)

    field_to_propagate = ['inventory_type', 'date']

inventory_hierarchical_location()

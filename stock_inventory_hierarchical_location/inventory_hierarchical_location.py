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

from openerp.osv import osv
from openerp.tools.translate import _


class StockInventory(osv.osv):
    _inherit = 'stock.inventory'

    def __init__(self, pool, cr):
        """Propagate the "exhaustive" field from inventories to sub-inventories"""
        s = super(StockInventory, self)
        s.PARENT_VALUES.append('exhaustive')
        return s.__init__(pool, cr)

    def action_open(self, cr, uid, ids, context=None):
        """Open only if all the parents are Open."""
        #XXX the dosctring used to say this but it's not implemented, normal?
        # --> "Before opening, if locations are  missing, ask the user 
        # to validate the opening without these locations."
        for inventory in self.browse(cr, uid, ids, context=context):
            while inventory.parent_id:
                inventory = inventory.parent_id
                if inventory.state != 'open':
                    raise osv.except_osv(_('Warning !'),
                                         _('One of the parent inventories are not open.'))
        return super(StockInventory, self).action_open(cr, uid, ids, context=context)

    def check_location(self, cr, uid, ids, location_ids, name, context=None):
        """Check if location is a child of parent inventory location"""
        res_location_ids = location_ids[0][2]
        nbr_location_ids = len(res_location_ids)
        for inventory in self.browse(cr, uid, ids, context=None):
            if inventory.parent_id.id:
                parent_locations = self.read(cr, uid, [inventory.parent_id.id], ['location_ids'])
                parent_children_locations = self.pool.get('stock.location').search(cr, uid, [('location_id', 'child_of', parent_locations[0]['location_ids'])])
                for location_id in res_location_ids:
                    if location_id not in parent_children_locations:
                        res_location_ids.remove(location_id)
        res = {}
        if nbr_location_ids != len(res_location_ids):
            res['warning'] = {'title': _('Warning: Wrong location'),
                              'message': _("This location is not declared on the parent inventory\n"
                                           "You cannot add it !")}
        res['value'] = {'location_ids': res_location_ids, }
        return res

    def _fill_location_lines(self, cr, uid, inventory_id, location_ids, set_stock_zero, context=None):
        """Add ids of children inventory into list """
        children_inventory_ids = self.search(cr, uid, [('parent_id', 'child_of', inventory_id)])
        context['children_inventory_ids'] = children_inventory_ids
        return super(StockInventory, self)._fill_location_lines(cr, uid, inventory_id, location_ids, set_stock_zero, context=context)

    def open_missing_location_wizard(self, cr, uid, ids, context=None):
        """Open wizard if inventory have children.
        Before, verify if all children of exhaustive inventory have at least one location."""
        children_ids = self.search(cr, uid, [('parent_id', 'child_of', ids)], context=context)
        for inventory in self.browse(cr, uid, children_ids, context=context):
            if inventory.exhaustive:
                if not inventory.location_ids:
                    raise osv.except_osv(_('Warning !'),
                                         _('Location missing for inventory "%s".') % inventory.name)
        children_count = self.pool.get('stock.inventory').search(cr, uid, [('parent_id', 'child_of', ids)], count=True)
        if children_count == 1:
            return self.action_open(cr, uid, ids, context)
        else:
            context['active_ids'] = ids
            context['active_id'] = ids[0]
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.inventory.missing.location',
                'target': 'new',
                'context': context,
                'nodestroy': True,
                }


# XXX: move to /wizard
class StockInventoryUninventoriedLocation(osv.osv_memory):
    _inherit = 'stock.inventory.uninventoried.locations'

    def inventories(self, cr, uid, inventory_parent_id):
        """Iterator of children inventories.
        return inventory_id;
       """
        children_ids = self.pool.get('stock.inventory').search(cr, uid, [('parent_id', 'child_of', inventory_parent_id)])
        for inventory_id in children_ids:
            yield inventory_id

    def get_locations(self, cr, uid, inventory_id, context=None):
        """Get all locations through inventory tree."""
        list_inventories_locations_ids = []
        for i_id in self.inventories(cr, uid, inventory_id):
            location_ids = super(StockInventoryUninventoriedLocation, self).get_locations(cr, uid, i_id, context=context)
            list_inventories_locations_ids = list(set(list_inventories_locations_ids + location_ids))
        return list_inventories_locations_ids

    def get_locations_inventoried(self, cr, uid, inventory_id, location_ids, context=None):
        """Get all locations on inventory lines through inventory tree."""
        list_all_inventoried_location_ids = []
        for i_id in self.inventories(cr, uid, inventory_id):
            list_loc_ids = super(StockInventoryUninventoriedLocation, self).get_locations_inventoried(cr, uid, i_id, location_ids, context=context)
            list_all_inventoried_location_ids = list(set(list_all_inventoried_location_ids + list_loc_ids))
        return list_all_inventoried_location_ids

    def default_locations(self, cr, uid, context=None):
        """Do something only if children state are confirm or done."""
        children_count = self.pool.get('stock.inventory').search(cr, uid, [('parent_id', 'child_of', context['active_id']),
                                             ('state', 'not in', ['confirm', 'done'])], context=context, count=True)
        if children_count > 1:
            raise osv.except_osv(_('Warning !'), _('Some Sub-inventories are not confirmed.'))
        return super(StockInventoryUninventoriedLocation, self).default_locations(cr, uid, context=context)

    _defaults = {
        'location_ids': default_locations,
        }


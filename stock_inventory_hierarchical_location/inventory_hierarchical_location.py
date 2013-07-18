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
        Open only if all the parents are Open.
        """
        inventories = self.browse(cr, uid, ids, context=context)
        for inventory in inventories:
            while inventory.parent_id:
                inventory = inventory.parent_id
                if inventory.state != 'open':
                    raise osv.except_osv(_('Warning !'), _('One of the parent inventories are not open.'))
        return super(inventory_hierarchical_location, self).action_open(cr, uid, ids, context=context)

    field_to_propagate = ['inventory_type', 'date']

    def check_location(self, cr, uid, ids, location_ids, name, context=None):
        """ Check if location is a children of parent inventory location """
        location_obj = self.pool.get('stock.location')
        res_location_ids = location_ids[0][2]
        nbr_location_ids = len(res_location_ids)
        for inventory in self.browse(cr, uid, ids, context=None):
            if inventory.parent_id.id:
                parent_locations = self.read(cr, uid, [inventory.parent_id.id], ['location_ids'])
                parent_children_locations = location_obj.search(cr, uid, [('location_id', 'child_of', parent_locations[0]['location_ids'])])
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

inventory_hierarchical_location()


class stock_inventory_hierarchical_uninventoried_location(osv.osv_memory):
    _inherit = 'stock.inventory.uninventoried.locations'

    def inventories(self, cr, uid, inventory_parent_id):
        """ Iterator of children inventories.
        return inventory_id;
        """
        inventory_obj = self.pool.get('stock.inventory')
        children_ids = inventory_obj.search(cr, uid, [('parent_id', 'child_of', inventory_parent_id)])
        for inventory_id in children_ids:
            yield inventory_id

    def get_locations(self, cr, uid, inventory_id, context=None):
        """ Get all locations through inventory tree. """
        list_inventories_locations_ids = []
        for i_id in self.inventories(cr, uid, inventory_id):
            location_ids = super(stock_inventory_hierarchical_uninventoried_location, self).get_locations(cr, uid, i_id, context=context)
            list_inventories_locations_ids = list(set(list_inventories_locations_ids + location_ids))
        return list_inventories_locations_ids

    def get_locations_inventoried(self, cr, uid, inventory_id, location_ids, context=None):
        """ Get all locations on inventory lines through inventory tree. """
        list_all_inventoried_location_ids = []
        for i_id in self.inventories(cr, uid, inventory_id):
            list_loc_ids = super(stock_inventory_hierarchical_uninventoried_location, self).get_locations_inventoried(cr, uid, i_id, location_ids, context=context)
            list_all_inventoried_location_ids = list(set(list_all_inventoried_location_ids + list_loc_ids))
        return list_all_inventoried_location_ids

    def default_locations(self, cr, uid, context=None):
        """ Do something only if children state are confirm or done.
        """
        inventory_obj = self.pool.get('stock.inventory')
        children_count = inventory_obj.search(cr, uid, [('parent_id', 'child_of', context['active_id']),
                                             ('state', 'not in', ['confirm', 'done'])], context=context, count=True)
        if children_count > 1:
            raise osv.except_osv(_('Warning !'), _('Some Sub-inventories are not confirmed.'))
        return super(stock_inventory_hierarchical_uninventoried_location, self).default_locations(cr, uid, context=context)

    _defaults = {
        'location_ids': default_locations,
        }

stock_inventory_hierarchical_uninventoried_location()

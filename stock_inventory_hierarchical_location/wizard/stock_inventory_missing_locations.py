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

from osv import osv, fields
from tools.translate import _


class inventory_missing_location(osv.osv_memory):

    _name = 'stock.inventory.missing.location'
    _description = 'Search on inventory tree for missing declared locations.'

    _columns = {
                'location_ids': fields.many2many('stock.location',
                                                 'stock_inventory_missing_location_rel',
                                                 'location_id',
                                                 'wizard_id',
                                                 'Missing location', readonly=True),
                }

    def confirm_missing_locations(self, cr, uid, ids, context=None):
        """ Call action open method from stock.inventory """
        ids = context['active_ids']
        self.pool.get('stock.inventory').action_open(cr, uid, ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def inventories(self, cr, uid, inventory_parent_id):
        """ Iterator of children inventories.
        """
        children_ids = self.pool.get('stock.inventory').search(cr, uid, [('parent_id', 'child_of', inventory_parent_id)])
        for inventory_id in children_ids:
            if inventory_id == inventory_parent_id:
                continue  # pass the parent inventory
            yield inventory_id

    def get_locations_from_children(self, cr, uid, inventory_id, context=None):
        """ Get all locations through inventory tree. """
        list_inventories_locations_ids = []
        for i_id in self.inventories(cr, uid, inventory_id):
            location_ids = self.pool.get('stock.inventory').read(cr, uid, [i_id], ['location_ids'], context=context)[0]
            location_ids = self.pool.get('stock.location').search(cr, uid, [
                                            ('location_id', 'child_of', location_ids['location_ids']),
                                            ('usage', '=', 'internal')], context=context)
            list_inventories_locations_ids = list(set(list_inventories_locations_ids + location_ids))
        return list_inventories_locations_ids

    def default_missing_locations(self, cr, uid, context=None):
        """ Initialize view with the list of missing locations on inventory tree.
        """
        if context is None:
            context = {}

        # get children locations for parent/current inventory
        parent_location_ids = self.pool.get('stock.inventory').read(cr, uid, [context['active_id']], ['location_ids'], context=context)[0]
        parent_location_ids = self.pool.get('stock.location').search(cr, uid, [
                                        ('location_id', 'child_of', parent_location_ids['location_ids']),
                                        ('usage', '=', 'internal')], context=context)
        # get locations for each sub-inventory
        location_ids = self.get_locations_from_children(cr, uid, context['active_id'])
        list_missing_ids = [_id for _id in parent_location_ids if _id not in location_ids]
        return list_missing_ids

    _defaults = {
        'location_ids': default_missing_locations,
        }

inventory_missing_location()

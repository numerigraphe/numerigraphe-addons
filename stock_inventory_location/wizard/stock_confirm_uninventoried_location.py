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

from osv import fields, osv
from tools.translate import _


class stock_inventory_uninventoried_location(osv.osv_memory):
    _name = 'stock.inventory.uninventoried.locations'
    _description = 'Confirm the uninventoried Locations.'

    _columns = {
                'location_ids': fields.many2many('stock.location',
                                                 'stock_inventory_uninventoried_location_rel',
                                                 'location_id',
                                                 'wizard_id',
                                                 'Uninventoried location', readonly=True),
                }

    def get_locations(self, cr, uid, inventory_id, context=None):
        """ Get all locations from inventory. """
        location_ids = self.pool.get('stock.inventory').read(cr, uid, [inventory_id], ['location_ids'], context=context)[0]
        return self.pool.get('stock.location').search(cr, uid, [
                        ('location_id', 'child_of', location_ids['location_ids']),
                        ('usage', '=', 'internal')], context=context)

    def get_locations_inventoried(self, cr, uid, inventory_id, location_ids, context=None):
        """ Get all locations on inventory lines. """
        inventory_line_obj = self.pool.get('stock.inventory.line')
        inventory_line_ids = inventory_line_obj.search(cr, uid, [('location_id', 'in', location_ids),
                                                                 ('inventory_id', '=', inventory_id)], context=context)
        inventory_line_locations_ids = inventory_line_obj.read(cr, uid, inventory_line_ids, ['location_id'], context=context)
        return list(set([_id['location_id'][0] for _id in inventory_line_locations_ids]))

    def default_locations(self, cr, uid, context=None):
        """ Initialize view with the list of uninventoried locations.
            Search for children of the location if exists.
        """
        if context is None:
            context = {}
        location_ids = self.get_locations(cr, uid, context['active_id'])
        inventory_line_locations_ids = self.get_locations_inventoried(cr, uid, context['active_id'], location_ids)
        return  [_id for _id in location_ids if _id not in inventory_line_locations_ids]

    _defaults = {
        'location_ids': default_locations,
        }

    def confirm_uninventoried_locations(self, cr, uid, ids, context=None):
        """ Call action confirm method from stock.inventory """
        inventory_ids = context['active_ids']
        # call the wizard to add lines for uninventoried locations with zero quantity
        inventory_obj = self.pool.get('stock.inventory')
        if not isinstance(inventory_ids, list):
            inventory_ids = [inventory_ids]

        for inventory in inventory_obj.browse(cr, uid, inventory_ids, context=context):
            if inventory.exhaustive:
                # get the locations that have not been entered into any line
                location_ids = [i for i in self.default_locations(cr, uid, context=context)]
                # search for children
                location_ids = self.pool.get('stock.location').search(cr, uid, [('location_id', 'child_of', location_ids),
                                                                                ('usage', '=', 'internal')], context=context)
                # _fill_location_lines() may raise an exception if the locaiton is empty
                lines = []
                try:
                    lines = inventory_obj._fill_location_lines(cr, uid,
                                                               inventory.id,
                                                               location_ids,
                                                               True,
                                                               context=context)
                except osv.except_osv as e:
                    pass
                
                # create inventory lines with zero qty
                inventory_lines_obj = self.pool.get('stock.inventory.line')
                for line in lines:
                    inventory_lines_obj.create(cr, uid, line, context=context)

        inventory_obj.action_confirm(cr, uid, inventory_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

stock_inventory_uninventoried_location()

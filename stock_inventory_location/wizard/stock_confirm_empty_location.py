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


class stock_inventory_empty_location(osv.osv_memory):

    _name = 'stock.inventory.empty.locations'
    _description = 'Ask to user to confirm the empty locations.'

    _columns = {
                'location_ids': fields.many2many('stock.location',
                                                 'stock_inventory_empty_location_rel',
                                                 'location_id',
                                                 'wizard_id',
                                                 'Empty locations', readonly=True),
                }

    def default_locations(self, cr, uid, context=None):
        """ initialize view with the list of empty locations """
        if context is None:
            context = {}

        inventory_obj = self.pool.get('stock.inventory')
        inventory_line_obj = self.pool.get('stock.inventory.line')

        location_ids = inventory_obj.read(cr, uid, [context['active_id']], ['location_ids'], context=context)[0]
        inventory_line_ids = inventory_line_obj.search(cr, uid, [('location_id', 'in', location_ids['location_ids']),
                                                                 ('inventory_id', '=', context['active_id'])], context=context)
        inventory_line_locations_ids = inventory_line_obj.read(cr, uid, inventory_line_ids, ['location_id'], context=context)
        list_loc_ids = list(set([_id['location_id'][0] for _id in inventory_line_locations_ids]))
        list_empty_locations_ids = [_id for _id in location_ids['location_ids'] if _id not in list_loc_ids]
        return list_empty_locations_ids

    _defaults = {
        'location_ids': default_locations,
        }


    def confirm_empty_locations(self, cr, uid, ids, context=None):
        """ Call action confirm method from stock.inventory """
        stock_inventory_obj = self.pool.get('stock.inventory')
        ids = context['active_ids']
        stock_inventory_obj.action_confirm(cr, uid, ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

stock_inventory_empty_location()

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

from osv import fields, osv
from tools.translate import _
from product._common import rounding
from collections import OrderedDict


class stock_fill_location_inventory(osv.osv_memory):
    _inherit = 'stock.fill.inventory'

    _columns = {
         'location_id': fields.many2one('stock.location', 'Location'),
         'inventory_type': fields.boolean('stock.inventory', 'Type'),
         }

    def get_inventory_type(self, cr, uid, context=None):
        if context.get('active_id', False):
            inventory_obj = self.pool.get('stock.inventory')
            inventory_type = inventory_obj.read(cr, uid, [context.get('active_id')], ['inventory_type'], context=context)[0]['inventory_type']
            return inventory_type
        return False

    _defaults = {
        'inventory_type': get_inventory_type,
        }

    def view_init(self, cr, uid, fields_list, context=None):
        """ inherit from original to add multiple selection of location
        and exclude from location list the locations already choosen by another inventory """
        if context is None:
            context = {}

        inventory_obj = self.pool.get('stock.inventory')
        inventory_state = inventory_obj.read(cr, uid, [context.get('active_id')], ['state'], context=context)[0]
        if inventory_state['state'] != 'open':
            raise osv.except_osv(_('Error !'), _('the inventory must be in "Open" state.'))

        nb_inventory = inventory_obj.search(cr, uid, [('id', '=', context.get('active_id'))], count=True, context=context)
        if nb_inventory == 0:
            raise osv.except_osv(_('Warning !'), _('No locations found for the inventory.'))

        return super(stock_fill_location_inventory, self).view_init(cr, uid, fields_list, context=context)

    def fill_inventory(self, cr, uid, ids, context=None):
        """ Fill the inventory only with open locations on the inventory.
        """
        if context is None:
            context = {}

        fill_inventory = self.browse(cr, uid, ids[0], context=context)
        if not fill_inventory.inventory_type:
            return super(stock_fill_location_inventory, self).fill_inventory(cr, uid, ids, context=context)  # call standard wizard

        inventory_obj = self.pool.get('stock.inventory')
        location_obj = self.pool.get('stock.location')

        location_ids = inventory_obj.read(cr, uid, [context.get('active_id')], ['location_ids'])
        options = {'recursive': False, 'set_stock_zero': False}

        if fill_inventory.recursive:
            location_ids = location_obj.get_children(cr, uid, location_ids[0].get('location_ids'), context=context)
            options['recursive'] = True
        else:
            location_ids = location_ids[0].get('location_ids')

        location_ids = list(OrderedDict.fromkeys(location_ids))

        if fill_inventory.set_stock_zero:
            options['set_stock_zero'] = True

        self._fill_location_lines(cr, uid, location_ids, options, context=context)
        return {'type': 'ir.actions.act_window_close'}

stock_fill_location_inventory()

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
from collections import OrderedDict


class stock_fill_location_inventory(osv.osv_memory):
    _inherit = 'stock.fill.inventory'

    _columns = {
         'location_id': fields.many2one('stock.location', 'Location'),
         'exhaustive': fields.boolean('stock.inventory', 'Type'),
         }

    def get_inventory_type(self, cr, uid, context=None):
        if context.get('active_id', False):
            inventory_obj = self.pool.get('stock.inventory')
            exhaustive = inventory_obj.read(cr, uid, [context.get('active_id')], ['exhaustive'], context=context)[0]['exhaustive']
            return exhaustive
        return False

    _defaults = {
        'exhaustive': get_inventory_type,
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
        if not fill_inventory.exhaustive:
            return super(stock_fill_location_inventory, self).fill_inventory(cr, uid, ids, context=context)  # call standard wizard

        location_ids = self.pool.get('stock.inventory').read(cr, uid, [context.get('active_id')], ['location_ids'])[0]

        if not location_ids['location_ids']:
            raise osv.except_osv(_('Error : Empty location !'), _('No location to import.\nYou must add a location on the locations list.'))

        if fill_inventory.recursive:
            location_ids = self.pool.get('stock.location').search(cr, uid, [('location_id', 'child_of', location_ids['location_ids']),
                                                                            ('usage', '=', 'internal')], context=context)
        else:
            location_ids = location_ids['location_ids']

        location_ids = list(OrderedDict.fromkeys(location_ids))

        lines = self.pool.get('stock.inventory')._fill_location_lines(cr, uid,
                                                   context['active_ids'][0],
                                                   location_ids,
                                                   fill_inventory.set_stock_zero,
                                                   context=context)

        inventory_lines_obj = self.pool.get('stock.inventory.line')
        for line in lines:
            inventory_lines_obj.create(cr, uid, line, context=context)
        return {'type': 'ir.actions.act_window_close'}

stock_fill_location_inventory()

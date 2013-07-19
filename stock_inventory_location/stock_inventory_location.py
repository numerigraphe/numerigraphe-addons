# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2011 Numérigraphe SARL. All Rights Reserved.
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

from osv import osv, orm, fields
from tools.translate import _


class stock_inventory_location(osv.osv):
    _inherit = 'stock.inventory'
    _columns = {
        'state': fields.selection((('draft', 'Draft'), ('open', 'Open'), ('done', 'Done'), ('confirm', 'Confirmed'), ('cancel', 'Cancelled')), 'State', readonly=True, select=True),
        'inventory_line_id': fields.one2many('stock.inventory.line', 'inventory_id', 'Inventory lines', readonly=True, states={'open': [('readonly', False)]}),
        'location_ids': fields.many2many('stock.location', 'stock_inventory_location_rel', 'location_id', 'inventory_id', 'Locations', readonly=True, states={'draft': [('readonly', False)]}),
        'inventory_type': fields.boolean('Complete', help="Check the box if the inventory is complete.\nLet the box unchecked if the inventory is partial."),
        }

    def action_open(self, cr, uid, ids, context=None):
        """ Open the inventory :
        - open all locations, import and print inventory sheet become possible
        """
        return self.write(cr, uid, ids, {'state': 'open'}, context=context)

    _defaults = {
        'state': lambda *a: 'draft',
        }

    def _check_location_free_from_inventories(self, cr, uid, ids):
        """ Verify if the location is free (exact id, not children).
        """
        for inventory in self.browse(cr, uid, ids, context=None):
            if not inventory.inventory_type:
                return True  # always accepted on partial inventories
            inventory_date = self.read(cr, uid, ids, ['date'])[0]
            location_ids = [location.id for location in inventory.location_ids]
            inv_ids = self.search(cr, uid, [('location_ids', 'in', location_ids),
                                            ('id', '!=', inventory.id),
                                            ('date', '=', inventory_date['date']),
                                            ('inventory_type', '=', True), ])
            if inv_ids:
                return False
        return True

    _constraints = [(_check_location_free_from_inventories, 'Error: Some locations was on another inventories.', ['id'])]

stock_inventory_location()


class stock_inventory_line(osv.osv):

    _inherit = 'stock.inventory.line'

    def onchange_location_id(self, cr, uid, ids, inventory_id, location_id, context=None):
        """ Raise exception if location_id not in locations list for this inventory """
        inventory_obj = self.pool.get('stock.inventory')
        location_obj = self.pool.get('stock.location')
        location_infos = location_obj.read(cr, uid, [location_id], ['usage'], context=context)
        if location_infos[0]['usage'] != 'internal':
            raise orm.except_orm(
                _('Wrong location'),
                _('You cannot add this type of location to inventory.'))

        location_ids = inventory_obj.read(cr, uid, [inventory_id], ['location_ids'], context=context)

        if location_ids[0]['location_ids']:
            # search children of location
            location_ids = location_obj.search(cr, uid, [('location_id',
                           'child_of', location_ids[0]['location_ids'])], context=context)
        if location_id not in location_ids:
            return {'value': {'location_id': False},
                    'warning': {'title': _('Warning: Wrong location'),
                                'message': _("You cannot add this location to inventory line.\n"
                                             "You must add this location on the locations list")}
                    }
        else:
            return True

    _defaults = {
                'inventory_id': lambda self, cr, uid, context: context.get('inventory_id', False),
                }

stock_inventory_line()


class stock_location(osv.osv):
    _inherit = 'stock.location'
    _order = 'name'

    def get_children(self, cr, uid, ids, context=None):
        """ Get all children locations of inventory
        and return the location.id list of all children.
        """
        res = self.search(cr, uid, [('location_id', 'child_of', ids), ('usage', '=', 'internal')])
        return res

stock_location()

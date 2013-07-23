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

from collections import Iterable

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

    def _get_locations_open_inventories(self, cr, uid, context=None):
        """ Search locations on open inventories, only if location_ids was added (complete inventory only) """
        open_inventories_ids = self.search(cr, uid, [('state', '=', 'open'), ], context=context)
        location_ids = []
        for open_inventory in self.browse(cr, uid, open_inventories_ids, context=context):
            location_ids.extend([location.id for location in open_inventory.location_ids])
        if location_ids:
            location_ids = list(set(location_ids))
            location_obj = self.pool.get('stock.location')
            location_ids = location_obj.get_children(cr, uid, location_ids, context=context)
        return location_ids

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

    def _check_inventory(self, cr, uid, ids, context=None):
        """Raise an error if the Location is being inventoried"""
        inventory_obj = self.pool.get('stock.inventory')
        location_inventory_open_ids = inventory_obj._get_locations_open_inventories(cr, uid, context=context)
        if not isinstance(ids, Iterable):
            ids = [ids]
        for id in ids:
            if id in location_inventory_open_ids:
                raise osv.except_osv(_('Error! Location on inventory'),
                                     _('This location is being inventoried'))
        return True

    def get_children(self, cr, uid, ids, context=None):
        """ Get all children locations of inventory
        and return the location.id list of all children.
        """
        return self.search(cr, uid, [('location_id', 'child_of', ids), ('usage', '=', 'internal')], context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """Refuse write if the location is being inventoried"""
        self._check_inventory(cr, uid, ids, context=context)
        if not isinstance(ids, Iterable):
            ids = [ids]
        ids_to_check = ids
        # If we are changing the parent, it must not be being inventoried
        if  vals.get('location_id'):
            ids_to_check.append(vals['location_id'])
        self._check_inventory(cr, uid, ids_to_check, context=context)
        return super(stock_location, self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):
        """Refuse create if the parent location is being inventoried"""
        self._check_inventory(cr, uid, vals.get('location_id'), context=context)
        return super(stock_location, self).create(cr, uid, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        """Refuse unlink if the location is being inventoried"""
        self._check_inventory(cr, uid, ids, context=context)
        return super(stock_location, self).unlink(cr, uid, ids, context=context)
stock_location()


class stock_move_lock(osv.osv):

    _inherit = 'stock.move'

    def _check_open_inventory_location(self, cr, uid, ids, context=None):
        """ Check if location is not in opened inventory
        Don't check on partial inventory (checkbox "Complete" not checked).
        """
        message = ""
        inventory_obj = self.pool.get('stock.inventory')
        location_inventory_open_ids = inventory_obj._get_locations_open_inventories(cr, uid, context=context)
        if not location_inventory_open_ids:
            return True  # Nothing to verify
        for move in self.browse(cr, uid, ids, context=context):
            if (move.location_id.usage != 'inventory'
                and move.location_dest_id.id in location_inventory_open_ids):
                message += " - %s\n" % (move.location_dest_id.name)

            if (move.location_dest_id.usage != 'inventory'
                and move.location_id.id in location_inventory_open_ids):
                message += " - %s\n" % (move.location_id.name)
        if message:
            raise osv.except_osv(_('Error! Location on inventory'),
                                 _('One or more locations are inventoried :\n%s') % message)
        return True

    _constraints = [
                    (_check_open_inventory_location,
                     "This location is being inventoried", ['location_id', 'location_dest_id']),
                   ]

stock_move_lock()

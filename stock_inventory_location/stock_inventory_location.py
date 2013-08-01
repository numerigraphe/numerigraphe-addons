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

from collections import Iterable

from osv import osv, orm, fields
from tools.translate import _


class StockInventory(osv.osv):
    """Add locations to the inventories"""
    _inherit = 'stock.inventory'
    _columns = {
        # XXX refactor if ever lp:~numerigraphe/openobject-addons/7.0-inventory-states is accepted upstream
        'state': fields.selection((('draft', 'Draft'), ('open', 'Open'), ('done', 'Done'), ('confirm', 'Confirmed'), ('cancel', 'Cancelled')), 'State', readonly=True, select=True),
        # Make the inventory lines read-only in all states except "Open", to ensure that no unwanted Location can be inserted
        'inventory_line_id': fields.one2many('stock.inventory.line', 'inventory_id', 'Inventory lines', readonly=True, states={'open': [('readonly', False)]}),
        'location_ids': fields.many2many('stock.location', 'stock_inventory_location_rel',
                                         'location_id', 'inventory_id',
                                         'Locations',
                                         readonly=True, states={'draft': [('readonly', False)]},
                                         help="""This is the list of the Stock Locations that you want to count the goods in.
Only these Locations can be entered in the Inventory Lines.
If some of them have not been entered in the Inventory Lines, OpenERP will warn you when you confirm the Inventory."""),
        'exhaustive': fields.boolean('Exhaustive', readonly=True, states={'draft': [('readonly', False)]},
                                         help="""Check the box if you are conducting an exhaustive Inventory.
Leave the box unchecked if you are conducting a standard Inventory (partial inventory for example).
For an exhaustive Inventory:
 - the status "Draft" lets you define the list of Locations where goods must be counted
 - the status "Open" indicates that the list of Locations is definitive and you are now counting the goods. In that status, no Stock Moves can be recorded in/out of the Inventory's Locations
 - only the Inventory's Locations can be entered in the Inventory Lines
 - if some of the Inventory's Locations have not been entered in the Inventory Lines, OpenERP warns you when you confirm the Inventory
 - every good that is not in the Inventory Lines is considered lost, and gets moved out of the stock when you confirm the Inventory"""),
        }

    def action_open(self, cr, uid, ids, context=None):
        """Open the inventory: open all locations, import and print inventory sheet become possible"""
        return self.write(cr, uid, ids, {'state': 'open'}, context=context)
    
    # XXX refactor if ever lp:~numerigraphe/openobject-addons/7.0-inventory-states is accepted upstream
    _defaults = {
        'state': lambda *a: 'draft',
        }

    def _check_location_free_from_inventories(self, cr, uid, ids):
        """Verify that no other Inventory is being conducted on the location (exact id, not children)."""
        for inventory in self.browse(cr, uid, ids, context=None):
            if not inventory.exhaustive:
                continue  # always accepted on partial inventories
            location_ids = [location.id for location in inventory.location_ids]
            inv_ids = self.search(cr, uid, [('location_ids', 'in', location_ids),
                                            ('id', '!=', inventory.id),
                                            ('date', '=', inventory.date),
                                            ('exhaustive', '=', True), ])
            if inv_ids:
                return False
        return True

    _constraints = [(_check_location_free_from_inventories,
                     'Other Physical inventories are being conducted using the same Locations.',
                     ['location_ids', 'date', 'exhaustive'])]

    def _get_locations_open_inventories(self, cr, uid, context=None):
        """Search for locations on open inventories (exhaustive inventory only), and their children """
        open_inventories_ids = self.search(cr, uid, [('state', '=', 'open'), ], context=context)
        location_ids = set()
        for open_inventory in self.browse(cr, uid, open_inventories_ids, context=context):
            location_ids.update([location.id for location in open_inventory.location_ids])
        # Extend to the children Locations
        if location_ids: #XXX probably works even otherwise
            location_ids = self.pool.get('stock.location').search(cr, uid,
                [('location_id', 'child_of', location_ids), ('usage', '=', 'internal')],
                context=context)
        return location_ids
    
    #FIXME overload inventory confirmation to delete the stock of the uninventories locations
    
StockInventory()


class StockInventoryLine(osv.osv):
    """Only allow the Inventory's Locations"""

    _inherit = 'stock.inventory.line'

    def onchange_location_id(self, cr, uid, ids, location_ids, exhaustive, location_id, context=None):
        """ Raise exception if Location is not internal, or location_id not in locations list for this inventory """
        location_ids = location_ids[0][2]
        if not exhaustive or not location_ids:
            return True  # don't check if partial inventory

        # search children of location
        location_ids = self.pool.get('stock.location').search(cr, uid,
                        [('location_id', 'child_of', location_ids)], context=context)
        if location_id not in location_ids:
            return {'value': {'location_id': False},
                    'warning': {'title': _('Warning: Wrong location'),
                                'message': _("You cannot add this location to inventory line.\n"
                                             "You must add this location on the locations list")}
                    }
        return True

StockInventoryLine()


class StockLocation(osv.osv):
    """Refuse changes during exhaustive Inventories"""
    _inherit = 'stock.location'
    _order = 'name'

    def _check_inventory(self, cr, uid, ids, context=None):
        """Raise an error if an exhaustive Inventory is being conducted on this Location"""
        inventory_obj = self.pool.get('stock.inventory')
        location_inventory_open_ids = inventory_obj._get_locations_open_inventories(cr, uid, context=context)
        if not isinstance(ids, Iterable):
            ids = [ids]
        for id in ids:
            if id in location_inventory_open_ids:
                raise osv.except_osv(_('Error! Location on inventory'),
                                     _('A Physical Inventory is being conducted at this location'))
        return True

    def write(self, cr, uid, ids, vals, context=None):
        """Refuse write if an inventory is being conducted"""
        self._check_inventory(cr, uid, ids, context=context)
        if not isinstance(ids, Iterable):
            ids = [ids]
        ids_to_check = ids
        # If we are changing the parent, there must be no inventory must conducted there either
        if  vals.get('location_id'):
            ids_to_check.append(vals['location_id'])
        self._check_inventory(cr, uid, ids_to_check, context=context)
        return super(StockLocation, self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):
        """Refuse create if an inventory is being conducted at the parent"""
        self._check_inventory(cr, uid, vals.get('location_id'), context=context)
        return super(StockLocation, self).create(cr, uid, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        """Refuse unlink if an inventory is being conducted"""
        self._check_inventory(cr, uid, ids, context=context)
        return super(StockLocation, self).unlink(cr, uid, ids, context=context)
StockLocation()


class StockMove(osv.osv):
    """Refuse Moves during exhaustive Inventories"""

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
                     "A Physical Inventory is being conducted at this location", ['location_id', 'location_dest_id']),
                   ]
StockMove()

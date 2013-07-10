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

'''

-  gestion des emplacements avec l'état de l'inventaire
-  sur confirmation inventaire (open -> confirm)

'''


class stock_inventory_location(osv.osv):
    _inherit = 'stock.inventory'
    _columns = {
        'state': fields.selection((('draft', 'Draft'), ('open', 'Open'), ('done', 'Done'), ('confirm', 'Confirmed'), ('cancel', 'Cancelled')), 'State', readonly=True, select=True),
        'location_ids': fields.many2many('stock.location', 'stock_inventory_location_rel', 'location_id', 'inventory_id', 'Locations'),
        }


    def action_open(self, cr, uid, ids, context=None):
        """ Open the inventory : 
        open all locations, import and print inventory sheet become possible
        """
        return self.write(cr, uid, ids, {'state': 'open'}, context=context)

    _defaults = {
        'state': lambda *a: 'draft',
        }

stock_inventory_location()


class stock_inventory_line(osv.osv):

    _inherit = 'stock.inventory.line'

    def onchange_location_id(self, cr, uid, ids, inventory_id, location_id, context=None):
        """ Raise exception if location_id not in locations list for this inventory """
        inventory_obj = self.pool.get('stock.inventory')
        location_obj = self.pool.get('stock.location')
        location_infos = location_obj.read(cr, uid, [location_id], ['usage'], context=context)
        # verify if type of location to add is internal
        if location_infos[0]['usage'] != 'internal':
            raise orm.except_orm(
                _('Wrong location'),
                _('You cannot add this type of location to inventory.'))

        location_ids = inventory_obj.read(cr, uid, [inventory_id], ['location_ids'], context=context)
        # search children of location
        location_ids = location_obj.search(cr, uid, [('location_id',
                       'child_of', location_ids[0]['location_ids'])], context=context)
        if location_id not in location_ids:
            raise orm.except_orm(
                _('Wrong location'),
                _('You cannot add this location to inventory line.\nYou must add this location on the locations list'))
        return True

    _defaults = {
                  'inventory_id': lambda self, cr, uid, context: context.get('inventory_id', False),
                  }

stock_inventory_line()


class stock_location(osv.osv):
    _inherit = 'stock.location'
    _order = 'name'

    def get_children(self, cr, uid, ids, context=None):
        """ Get all children of inventory """
        children = list()
        for location_id in ids:
            res = self.search(cr, uid, [('location_id', 'child_of', location_id), ('usage', '=', 'internal')])
            if res:
                children.extend(res)
        return children

stock_location()

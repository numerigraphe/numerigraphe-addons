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

from osv import osv, fields


class inventory_location(osv.osv):

    _name = 'stock.inventory.location'
    _columns = {
            'name': fields.char('name', size=64, required=True, select=True),
            'inventory_id': fields.many2one('inventory.inventory_id', ondelete='cascade'),
            'location_id': fields.many2one('location.location_id', ondelete='cascade'),
            'state': fields.selection([('draft', 'Draft'),
                                       ('open', 'Open'),
                                       ('print', 'Printed'),
                                       ('done', 'Done')],
                                      'state', required=True, readonly=True),  # open state needed to open inventory and lock stock move
            'active': fields.boolean('Active'),

        }

    _defaults = {
         'active': lambda *a: True,
         'state': lambda *a: 'draft',
    }

    #_constraints
    #_sql_constraints

inventory_location()


class stock_inventory(osv.osv):
    _inherit = 'stock.inventory'

    _columns = {
        'inventory_location_ids': fields.one2many('stock.location', 'location_id', 'Inventory/location couple'),
        }

stock_inventory()


class stock_location(osv.osv):
    _inherit = 'stock.location'

    _columns = {
        'inventory_lock': fields.one2many('inventory.inventory_id', 'location_lockedby', 'The lock of location by inventory')  # id de l'inventaire dont il fait parti
        }

stock_location()

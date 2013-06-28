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


class stock_inventory_location(osv.osv):

    _name = 'stock.inventory.location'

    def _products_count(self, cr, uid, ids, field_name, arg, context=None):
        """" Count the number of products imported on the inventory for each location """
        if context is None:
            context = {}
        inventory_lines_obj = self.pool.get('stock.inventory.line')

        count = {}
        for an_id in ids:
            res = self.read(cr, uid, [an_id], ['inventory_id', 'location_id'], context=context)
            nb = inventory_lines_obj.search(cr, uid, [
                                                         ('inventory_id', '=', res[0].get('inventory_id')[0]),
                                                         ('location_id', '=', res[0].get('location_id')[0])
                                                         ], count=True, context=context)
            count[an_id] = int(nb)
        return count

    _columns = {
            'name': fields.char('name', size=64, select=True, readonly=True),
            'inventory_id': fields.many2one('stock.inventory', 'Inventory', ondelete='cascade', readonly=True),
            'location_id': fields.many2one('stock.location', 'Location', ondelete='cascade'),
            'state': fields.selection([('draft', 'Draft'),
                                       ('open', 'Open'),
                                       ('print', 'Printed'),
                                       ('done', 'Done')],
                                      'state', required=True, readonly=True),  # open state needed to open inventory and lock stock move
            'empty': fields.boolean('Empty location'),
            'products_count': fields.function(_products_count, method=True, string='Number of products', type='integer'),
            'active': fields.boolean('Active'),

        }

    _defaults = {
         'active': lambda *a: True,
         'state': lambda *a: 'draft',
         'inventory_id': lambda self, cr, uid, context: context.get('inventory_id', False),
         }

    def create(self, cr, user, vals, context=None):
        """ Add a record, but not views """
        # Do not create views
        location_obj = self.pool.get('stock.location')
        location_infos = location_obj.read(cr, user, vals['location_id'], ['usage'])
        if location_infos.get('usage') == 'view':
            return False

        vals['name'] = '%s:%s' % (vals['inventory_id'], vals['location_id'])
        return super(stock_inventory_location, self).create(cr, user, vals, context=context)

#     def write(self, cr, uid, ids, vals, context=None):
#         return super(stock_inventory_location, self).write(cr, uid, ids, vals, context=context)

    def onchange_inventory_location_id(self, cr, uid, ids, inventory_id, location_id, context=None):
        """ If select location is view, complete list with all children locations """
        location_obj = self.pool.get('stock.location')
        location_ids = location_obj.search(cr, uid, [('location_id', 'child_of', [location_id])], order='name', context=context)
        for loc_id in location_ids:
            if loc_id == location_id:
                continue  # remove duplicates
            inventory_location_details = {'location_id': loc_id,
                                          'inventory_id': inventory_id}
            self.create(cr, uid, inventory_location_details, context=context)
        return {}


    def onchange_location_id(self, cr, uid, ids, location_id, context=None):
        print "stock_inventory_location.location_id : %s" % location_id
        return False

stock_inventory_location()


class stock_inventory(osv.osv):
    _inherit = 'stock.inventory'

    _columns = {
        'location_inventory_ids': fields.one2many('stock.inventory.location', 'inventory_id', 'Inventory', ondelete='cascade'),
        }

stock_inventory()


# est-ce qu bon endroit

# class stock_location(osv.osv):
#     _inherit = 'stock.location'
# 
#     _columns = {
#         'inventory_lock': fields.one2many('inventory.inventory_id', 'location_lockedby', 'The lock of location by inventory', ondelete='cascade')
#         }
# 
# stock_location()

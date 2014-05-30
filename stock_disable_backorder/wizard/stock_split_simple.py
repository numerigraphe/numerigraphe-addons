# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2014 Numérigraphe SARL. All Rights Reserved.
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


from openerp.osv import fields, orm
from openerp.addons import decimal_precision as dp


class StockMoveSplitSimple(orm.TransientModel):
    """This object lets users enter details to split a move line in two."""
    _name = "stock.move.split.simple"
    _description = "Stock move splitting details"

    _columns = {
        # We use the exact same field names as in the Stock Move model
        # so that we can use it's onchange functions
        'product_id': fields.many2one(
            'product.product', 'Product', required=True, readonly=True),
        'initial_qty': fields.float(
            'Initial quantity', readonly=True,
            digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_qty': fields.float(
            'Quantity', required=True,
            digits_compute=dp.get_precision('Product Unit of Measure'),
            help="The quantity the should be moved to another line, expressed "
                 "in the Unit of Measure of the original Stock Move."),
        'rest_qty': fields.float(
            'Quantity', readonly=True,
            digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_uom': fields.many2one(
            'product.uom', 'Unit of Measure', readonly=True),
        'initial_uos_qty': fields.float(
            'Initial quantity in UoS', readonly=True,
            digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_uos_qty': fields.float(
            'Quantity in UoS', required=True,
            digits_compute=dp.get_precision('Product Unit of Measure'),
            help="The quantity that should be moved to another line, "
                 "expressed in the Unit of Sale of the original Stock Move."),
        'rest_uos_qty': fields.float(
            'Quantity in UoS', readonly=True,
            digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_uos': fields.many2one(
            'product.uom', 'Unit of Sale', readonly=True),
    }

    def onchange_quantity(self, cr, uid, ids, product_id, product_qty,
                          product_uom, product_uos, initial_qty,
                          initial_uos_qty):
        """Call stock.move.onchange_quantity() and update remaining qty"""
        # Cap the split qty to the initial qty
        product_qty = max(min(product_qty, initial_qty), 0.0)
        changes = self.pool['stock.move'].onchange_quantity(
            cr, uid, ids, product_id, product_qty, product_uom, product_uos)
        # Update the remaining qty
        vals = changes['value']
        vals.update({
            'product_qty': product_qty,
            'rest_qty': max(initial_qty - product_qty, 0.0),
            'rest_uos_qty': max(initial_uos_qty
                                - vals.get('product_uos_qty', 0.0), 0.0)})
        return changes

    def onchange_uos_quantity(self, cr, uid, ids, product_id, product_uos_qty,
                              product_uos, product_uom, initial_qty,
                              initial_uos_qty):
        """Call stock.move.onchange_uos_quantity() and update remaining qty"""
        # Cap the split qty to the initial qty
        product_uos_qty = max(min(product_uos_qty, initial_uos_qty), 0.0)
        changes = self.pool['stock.move'].onchange_uos_quantity(
            cr, uid, ids, product_id, product_uos_qty, product_uos,
            product_uom)
        # Update the remaining qty
        vals = changes['value']
        vals.update({
            'product_uos_qty': product_uos_qty,
            'rest_qty': max(initial_qty - vals.get('product_qty', 0.0), 0.0),
            'rest_uos_qty': max(initial_uos_qty - product_uos_qty, 0.0)})
        return changes

    def split(self, cr, uid, ids, context=None):
        """Call stock.move.split() in a loop

        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: list of ids of wizard objects
        @param context: A standard dictionary
        @return: Dictionary with directives to close the window
        """
        if context is None or 'active_ids' not in context:
            return False
        move_obj = self.pool['stock.move']
        move_ids = context['active_ids']
        for data in self.browse(cr, uid, ids):
            _ = move_obj.split(cr, uid, move_ids, data.product_qty,
                               data.product_uos_qty, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def default_get(self, cr, uid, fields, context=None):
        """Get default values from the active Move in the context

        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for default value
        @param context: A standard dictionary
        @return: default values of fields
        """
        defaults = super(StockMoveSplitSimple, self).default_get(
            cr, uid, fields, context=context)
        if context is None or 'active_id' not in context:
            return defaults
        # Find the fields we need to read
        move_fields = filter(
            lambda x: x in fields,
            ['product_id', 'product_qty', 'product_uom',
             'product_uos_qty', 'product_uos'])
        # Read the values
        move = self.pool['stock.move'].read(
            cr, uid, context['active_id'], move_fields, context=context)
        if move:
            for field in [f for f in move_fields if move[f]]:
                # Set the related ID as default
                if type(move[field]) == tuple:
                    defaults[field] = move[field][0]
                else:
                    defaults[field] = move[field]
        if 'initial_qty' in fields:
            defaults['initial_qty'] = defaults.get('product_qty')
        if 'rest_qty' in fields:
            defaults['rest_qty'] = 0.0
        if 'initial_uos_qty' in fields:
            defaults['initial_uos_qty'] = defaults.get('product_uos_qty')
        if 'rest_uos_qty' in fields:
            defaults['rest_uos_qty'] = 0.0
        return defaults
